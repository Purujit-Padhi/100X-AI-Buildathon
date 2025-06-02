from flask import Flask, render_template, request, jsonify,redirect,send_from_directory,url_for
from flask_sqlalchemy import SQLAlchemy
import fitz  # PyMuPDF
import threading
import os
from datetime import datetime
import AI as ai_part
import json
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker



app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



Base = declarative_base()
engine = create_engine("sqlite:///users.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()

Base_r = declarative_base()
engine_r = create_engine("sqlite:///recruters.db", echo=False)
Session_r = sessionmaker(bind=engine_r)
session_r = Session_r()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # plain text password

    # Optional
    email = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    profile_link = Column(String, nullable=True)



    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', password='{self.password}', full_name='{self.full_name}, file_path='{self.file_path}', personal_link='{self.profile_link}')>"

# Create the table (only once)
Base.metadata.create_all(engine)



class recrutor(Base_r):
    __tablename__ = 'recrutors'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # plain text password


    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', password='{self.password}')>"

# Create the table (only once)
Base_r.metadata.create_all(engine_r)


def async_ai_analysis(filepath):
    ai_part.upload_json_analyse(filepath)



@app.route('/download/<filename>')
def download_file(filename):
    upload_folder = UPLOAD_FOLDER
    return send_from_directory(upload_folder,filename, as_attachment=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    filename = os.path.basename(filename)
    print(filename)
    return send_from_directory('uploads', filename)


@app.route('/recrutor_operating_page')
def prompt_tab():
    return render_template('recrutor_operating_page.html',username=" ")

@app.route('/candidate/<username>')
def welcome(username):
    # Python function to print the username
    return render_template('candidate.html', username=username)


@app.route('/upload_new_user', methods=['GET','POST'])
def upload_new_user():
    if request.method == "POST":
        username = request.form['username']
        full_name = request.form['fullname']
        email = request.form['email']
        pflink = request.form['pflink']
        file = request.files['resume']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{username}resume_{timestamp}.pdf'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # --> save in database
        user = session.query(User).filter_by(username=username).first()
        user.full_name = full_name
        user.email = email
        user.file_path = filepath
        user.profile_link = pflink 
        if not user.profile_link.startswith("http") and len(user.profile_link) > 5:
            user.profile_link = "https://" + user.profile_link
        session.commit()
        async_ai_analysis(filepath)
        user = session.query(User).filter_by(username=username).first()
        # print(user)
        with open('resume_data.json', 'r') as f:  # Use your actual file path
            full_data = json.load(f)

        sections = full_data[filepath.replace("\\","/")]
        print(sections)

    # Python function to print the username
    return render_template('predefined_candidate.html', user=user, sections=sections)


@app.route('/blank/<username>')
def existing_user(username):
    user = session.query(User).filter_by(username=username).first()
    print(user)
    with open('resume_data.json', 'r') as f:  # Use your actual file path
        full_data = json.load(f)

    filepath = user.file_path
    sections = full_data[filepath.replace("\\","/")]
    return render_template('predefined_candidate.html', user=user, sections=sections)


@app.route('/')
def hello_world():
    return render_template('login.html',error="")


# Update on change in coliumn in db
@app.route('/candidate_login', methods=['GET','POST'])
def login():
    error = None
    if request.method == "POST":
        name = request.form['username']
        pswd = request.form['password']

        user = session.query(User).filter_by(username=name).first()

        if user:
            # Check if password matches for that user
            if user.password == pswd:
                # Login success (redirect or whatever you want)
                print("already exists")
                return redirect(url_for('existing_user', username=name))
            else:
                error = "❌ Password does not match."
        else:
            # User does not exist, create user
            user = User(username=name, password=pswd, email="", full_name="", file_path="", profile_link="")
            session.add(user)
            session.commit()
            return redirect(url_for('welcome', username=name))

    return render_template('login.html', error=error)



# --->>> Recrutor Parts

@app.route('/recruter_login')
def recruter_login():
    return render_template('recruter_login.html',error="")


@app.route('/recrutor_operating_page/<username>')
def recrutor_operating_page(username):
    return render_template('recrutor_operating_page.html', username=username)


@app.route('/recruter_login_post', methods=['GET','POST'])
def recruter_login_post():
    print("reqruotor_post")
    error = None
    if request.method == "POST":
        name = request.form['username']
        pswd = request.form['password']

        recrutor_user = session_r.query(recrutor).filter_by(username=name).first()

        if recrutor_user:
            # Check if password matches for that user
            if recrutor_user.password == pswd:
                # Login success (redirect or whatever you want)
                print("already exists")
                return redirect(url_for('recrutor_operating_page', username=name))
            else:
                error = "❌ Password does not match."
        else:
            # User does not exist, create user
            recrutor_user = recrutor(username=name, password=pswd)
            session_r.add(recrutor_user)
            session_r.commit()
            return redirect(url_for('recrutor_operating_page', username=name))

    return render_template('login.html', error=error)


@app.route("/search_on_values", methods=['GET','POST'])
def update():
    if request.method == "POST":
        search_text = str(request.form['search'])
        username = request.form.get('username', 'User')
        filtered_candidates = ai_part.json_find_best_match(search_text)

        display_data = []

        for pdf_name in filtered_candidates.keys():
            candidate_filepath = os.path.join(UPLOAD_FOLDER, pdf_name)
            candidate = session.query(User).filter_by(file_path=candidate_filepath).first()
            if not candidate:
                continue

            with open('resume_data.json', 'r') as f:
                full_data = json.load(f)

            sections = full_data.get(candidate.file_path.replace("\\", "/"), [])

            display_data.append({
                "fullname": candidate.full_name,
                "email": candidate.email,
                "file_path":candidate.file_path,
                "profile_link": candidate.profile_link,
                "sections": sections
            })

        return render_template('filtered_recruter.html', candidates=display_data)



if __name__ == '__main__':
    app.run(debug=True)
