import json
import access_token
import os
import fitz  # PyMuPDF for PDF parsing
import docx

from google import genai
from google.genai import types

import gmail_api

# API key as envirnomental varibale
os.environ["GOOGLE_API_KEY"] = access_token.GOOGLE_API_KEY
api_key = os.environ.get("GOOGLE_API_KEY")


# Function to extract text from PDFs
def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


# Function to extract text from DOCX files
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def process_resume(file_path):
    if file_path.endswith(".pdf"):
        resume_text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        resume_text = extract_text_from_docx(file_path)
    else:
        print(f"Skipping unsupported file: {file_path}")
        return None

    # Extract structured resume data
    structured_data = extract_resume_data(resume_text)
    return structured_data


# Function to parse resume and extract structured data using Gemini
def extract_resume_data(resume_text):
    prompt = f"""
    Extract the following details from the resume:
    - Full Name(first word capital, eg: "Krish Bakshi", "Uzumaki Naruto")
    - Email
    - Phone Number
    - Work Experience (Company, Role, Contribution and work)
    - Projects(Project, Tech Stack/Tehnology)
    - Education (Degree, University, Year) /(Only first word capital)/
    - Skills
    Provide the data in a structured JSON format.
    
    Resume:
    {resume_text}
    """

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text  # Gemini will return structured JSON


# Response Pipeline
def generate_email(prompt, template):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=template),
        contents=[prompt],
    )
    return response.text

# Response to json
def response_to_json(response_text):
    lines = response_text.splitlines()
    subject = ""
    main_message = ""
    message_started = False

    for line in lines:
        line = line.strip()
        if line.startswith("Subject") and not subject:
            subject = line
        elif line.startswith("Dear") and not message_started:
            message_started = True
            main_message += line + "\n"
        elif message_started:
            main_message += line + "\n"

    email_data = {
        "subject": subject,
        "main_message": main_message.strip()
    }

    return json.dumps(email_data, indent=4)

def save_gmail_draft(response_text, file_path):
   service = gmail_api.gmail_authenticate()

   message_json = response_to_json(response_text)
   
   parsed_response = json.loads(message_json)

   subject = parsed_response['subject']
   body = parsed_response['main_message']

   # Create the email message body
   message_body = gmail_api.create_message(subject, body, file_path)
   gmail_api.create_draft(service, 'me', message_body)

   return "Draft email created successfully!, Please check your Gmail account."