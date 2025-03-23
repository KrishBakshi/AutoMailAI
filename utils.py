import json 
import access_token
import os
import fitz  # PyMuPDF for PDF parsing
import docx

from google import genai
from google.genai import types

# API key as envirnomental varibale
os.environ['GOOGLE_API_KEY'] = access_token.GOOGLE_API_KEY
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
    contents= prompt,
    )
    return response.text  # Gemini will return structured JSON

# Define the system instruction
sys_instruct = """
You are an AI assistant tasked with drafting a professional and personalized email to a hiring manager 
expressing interest in a job opportunity at their company. 
You need to adjust accordingly with grammar and spot possible areas where the info in the resume and that of the hiring manager/recruiter are relavent.
Make the email such that it piques the interest of the hiring manger, such as a certain skill set they need or can be of great value to them.
The email should adhere to the following template and should generate in 260 - 280 words consistently, with placeholders to be filled accordingly:

Subject: Seeking Opportunities to Contribute at {Company Name}

Dear {Hiring Manager's Name},

I hope this email finds you well. My name is [Extract Full Name from Resume], and I am writing to express my keen interest in exploring career opportunities at {Company Name}. Your organization's work in {Industry/Field} has greatly impressed me, particularly your contributions to {Specific Projects, Innovations, or Company Achievements}.

With a background in [Extract Academic Background: degree, university, and GPA], I have developed strong skills in [Extract Relevant Technical Skills] and gained hands-on experience through projects such as [Extract Relevant Projects from Resume]. My expertise in {Specific Skills or Tools Relevant to the Job} aligns well with the work being done at your company, and I am eager to bring my knowledge and passion to your team.

Additionally, my certification in Practical AI with Python showcases my commitment to continuous learning in AI and data-driven solutions. Furthermore, my proficiency in Japanese, certified by the JLPT N3, allows me to collaborate effectively in diverse and international work environments.

I am particularly interested in {Specific Roles, Teams, or Projects at the Company} and believe that my skills in {Extract Skills from Resume} would allow me to contribute meaningfully to your organization's goals. I have attached my resume for your review and would welcome the opportunity to discuss how my experience and expertise align with your company’s needs.

Thank you for your time and consideration. I look forward to the possibility of joining {Company Name} and contributing to its continued success.

Best regards,
[Extract Full Name from Resume]

Resume:
{}

"""

# Response Pipeline
def generate_email(prompt):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct),
        contents=[prompt]
    )
    return response.text