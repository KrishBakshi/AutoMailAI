import json
import access_token
import os
import fitz  # PyMuPDF for PDF parsing
import docx

from google import genai
from google.genai import types

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
