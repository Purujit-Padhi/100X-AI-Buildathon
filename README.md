# 100X-AI-Buildathon
This is the project for the competition. Read the readme.txt file to understand it whole logically

=============================
📄 AI Resume Screening System
=============================

📌 PROJECT OVERVIEW
--------------------
This is an AI-powered resume screening web application built for the Hackathon.

The system automatically analyzes resumes (PDF format), extracts key information using Google's Gemini AI, and ranks candidates based on custom recruiter prompts (e.g., "Looking for Python and Flask expert").

This project demonstrates the use of:
- Google Gemini (Generative AI)
- Resume parsing via LLM
- Flask Web Framework (Python)
- SQLite databases for user management
- Auto matching and filtering of resumes


🧠 HOW IT WORKS
--------------------
1. A **candidate** logs in or registers on the site and uploads their resume (PDF).
2. The resume is sent to Gemini AI and parsed into structured data (Experience, Roles, Achievements, Skills, etc.).
3. The data is saved in `resume_data.json`.
4. A **recruiter** logs in, enters a prompt like: `Search for frontend developer with React`, and the app automatically scores resumes based on Gemini’s judgment.
5. Resumes that score highly are shown to the recruiter with extracted sections for easy comparison.


🚀 HOW TO RUN
--------------------
''' (for judge)
Install all the files and folder in the directory. and run app.py from the current dierectory of installed files and folder.This will return u an IP link, open it and there u go.
Follow up with the video shared for better understanding.
Suggesting for keeping pre resumes/cv to upload, to the website.
Then only, the database will have some resumes/cv to analyse by Ai.
--> Not prefered for scalling, as more work is required to be done and complete.
'''



1. Ensure Python 3.10+ is installed.
2. Install required libraries.
3. Use the web interface to register as a candidate or recruiter and follow the flow.

✅ FEATURES
--------------------
- AI resume parsing using Gemini (LLM)
- Automatic JSON conversion of resume data
- Candidate login, resume upload
- Recruiter login, prompt-based search
- Resume filtering and display with extracted sections
- Download functionality for selected resumes

📁 FILE STRUCTURE
--------------------
- `app.py` : Main Flask web server.
- `AI.py` : AI helper module for resume parsing and ranking with Gemini.
- `resume_data.json` : Output file containing extracted resume data.
- `uploads/` : Folder to store uploaded PDFs.
- `users.db` : SQLite DB for candidates. (will be created after the file(app.py) runs initially)
- `recruters.db` : SQLite DB for recruiters.(will be created after the file(app.py) runs initially)

🛠️ NOTES FOR JUDGES
--------------------
- This project showcases practical use of LLMs in recruitment automation.
- All AI logic is in `AI.py`, and the web server is controlled by `app.py`.
- Scores are calculated using AI prompts asking Gemini to rate resume relevance (0–10).
- Output is simplified for demo but easily extendable.


