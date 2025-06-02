import google.generativeai as genai
from google.generativeai import types
import pathlib
import json
import re
import os

client = genai.Client(api_key="AIzaSyAkK1riTDCdg2cdXMkg9lkrUxWuEOGgqb8")
folder = "uploads"

# Retrieve and encode the PDF byte
def gemini_analyse(filepath):
    filepath = pathlib.Path(filepath)
    prompt = "Ananlyse the resume/cv and return me the (Experience,Roles,Achievments,Certificate,Language Known) in simple and sort keywords in list format"
    response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        types.Part.from_bytes(
            data=filepath.read_bytes(),
            mime_type='application/pdf',
        ),
        prompt])

    raw_text = response.text
    return raw_text


# Processing logic
def add_data_to_json(filename1, raw1):
    def parse_resume_single_heading(filename, raw):
        filename = str(filename).replace("\\", "/")
        data = {str(filename): []}
        lines = raw.strip().splitlines()
        current_heading = ""
        current_values = []

        for line in lines:
            line = line.strip()
            if line.startswith("*") and "**" in line:
                if current_heading and current_values:
                    data[filename].append([current_heading, current_values])
                current_heading = line.split("**")[1].strip(": ")
                current_values = []
            elif line.startswith("*"):
                item = line.lstrip("*").strip()
                current_values.append(item)

        if current_heading and current_values:
            data[filename].append([current_heading, current_values])
        return data

    resume_data = parse_resume_single_heading(filename1, raw1)

    json_path = "resume_data.json"

    # Load existing data if file exists
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            existing_data = json.load(f)
    else:
        existing_data = {}

    # Update with new data
    existing_data.update(resume_data)

    # Write back to file
    with open(json_path, "w") as f:
        json.dump(existing_data, f, indent=4)



def upload_json_analyse(filepath):
    raw_text = gemini_analyse(filepath)
    print("Gemini proccessing of getting raw data succesfull!")
    add_data_to_json(filepath,raw_text)
    print("Resume successfully parsed and saved to resume_data.json!")




def find_best_matching_resume(prompt: str, folder_path: str) -> str:
    """
    Analyzes all PDFs in the folder and returns the filename that best matches the prompt.
    """
    folder = pathlib.Path(folder_path)
    best_score = -1
    best_match = None
    all_best_match = []

    print(f"for promp {prompt}")

    for pdf_file in folder.glob("*.pdf"):
        try:
            print(f"Analyzing: {pdf_file.name}")

            # Send content + prompt to Gemini
            response = client.models.generate_content(
                model="gemini-2.0-flash",  # You can use gemini-1.5-pro or flash too
                contents=[
                    types.Part.from_bytes(
                        data=pdf_file.read_bytes(),
                        mime_type='application/pdf',
                    ),
                    f"Based on the following prompt: \"{prompt}\", give a score from 0 to 10 indicating how relevant this resume is. Then explain your reasoning in 1-2 lines. Only start the response with the score (e.g., '8: This resume ...')"
                ]
            )

            # Parse score from response
            response_text = response.text.strip()
            score_match = response_text.split(":")[0]
            score = int(score_match.strip())

            # Track best match
            if score > 8:
                best_score = score
                best_match = pdf_file.name
                all_best_match.append(best_match)

        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")

    return all_best_match


def json_find_best_match(prompt: str):
    
    best_resume = find_best_matching_resume(prompt, folder)

    if len(best_resume) < 0:
        filtered_data = {}
        return filtered_data


    with open('resume_data.json', 'r') as f:
        all_data = json.load(f)

    # Create a new dictionary for matched entries
    filtered_data = {}


    all_keys = list(all_data.keys())

    # Only iterate once over all keys
    for key in best_resume:
        matching_keys = [k for k in all_keys if key in k]
        for mk in matching_keys:
            filtered_data[key] = all_data[mk]

    return filtered_data

    # return best_match_json









if __name__ == "__main__":
    pass
