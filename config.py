from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import os

def write_email(name, company, ai_email):

    output_folder = './output'
    # Create a new Word document
    doc = Document()

    # Add AI-generated text to the document
    paragraph = doc.add_paragraph()
    run = paragraph.add_run(ai_email)

    # Formatting the text
    run.font.name = "Trebuchet MS"
    run.font.size = Pt(10)

    # # Justify the paragraph
    # paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY

    # Set vertical spacing (before and after paragraph)
    paragraph.paragraph_format.space_before = Pt(10)  # 10pt space before paragraph
    paragraph.paragraph_format.space_after = Pt(10)   # 10pt space after paragraph
    paragraph.paragraph_format.line_spacing = 1.0     # 1.5 line spacing

    # Save the document
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    doc.save(os.path.join(output_folder, f"{name}, {company}.docx"))
    