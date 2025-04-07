import gradio as gr
import os
from tqdm import tqdm
import utils
import config
import pandas as pd

def output(file, text1, text2, text3, text4, text5, text6, template, progress: gr.Progress = gr.Progress(track_tqdm=True)):

    output_text = "" 

    if file is None:
        return gr.Error("No file uploaded.")

    file_path = file.name
    structured_data = utils.process_resume(file_path)
    if structured_data is None:
        return gr.Error("Unsupported file type.")

    # Get the selected template value
    selected_template = config.template[template]

    prompt = f"""
    {{
        "Hiring Manager's Name": "{text1}",
        "Company Name": "{text2}",
        "Industry/Field": "{text3}",
        "Specific Projects, Innovations, or Company Achievements": "{text4}",
        "Specific Skills or Tools Relevant to the Job": "{text5}",
        "Specific Roles, Teams, or Projects at the Company": "{text6}",
        "resume": {structured_data}
    }}
    """
    progress(0.5)
    output_text = utils.generate_email(prompt, selected_template)
    progress(1)

    return output_text, output_text

def bulk_output(excel, pdf, template, progress: gr.Progress = gr.Progress(track_tqdm=True)):
    # Check for uploaded files
    if excel is None:
        return gr.Error("No Excel file uploaded.")
    if pdf is None:
        return gr.Error("No PDF file uploaded.")

    # Determine file extension and read accordingly
    file_ext = os.path.splitext(excel.name)[-1].lower()
    try:
        if file_ext == '.csv':
            df = pd.read_csv(excel.name)
        elif file_ext in ['.xls', '.xlsx']:
            df = pd.read_excel(excel.name)
        else:
            return gr.Error("Unsupported file type. Please upload a .csv or .xlsx file.")
    except Exception as e:
        return gr.Error(f"Failed to read the file: {str(e)}")

    # Check required columns
    required_columns = [
        'Hiring Managers Name', 'Company Name', 'Industry/Field',
        'Specific Projects, Innovations, or Company Achievements',
        'Specific Skills or Tools Relevant to the Job',
        'Specific Roles, Teams, or Projects at the Company'
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return gr.Error(f"The uploaded Excel file is missing required columns: {', '.join(missing_columns)}")

    # Process the resume
    structured_data = utils.process_resume(pdf.name)
    if structured_data is None:
        return gr.Error("Unsupported or unreadable resume file.")

    # Get the selected template value
    selected_template = config.template[template]

    # Loop through each row and generate emails
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Generating emails"):
        prompt = f"""
        {{
            "Hiring Manager's Name": "{row['Hiring Managers Name']}",
            "Company Name": "{row['Company Name']}",
            "Industry/Field": "{row['Industry/Field']}",
            "Specific Projects, Innovations, or Company Achievements": "{row['Specific Projects, Innovations, or Company Achievements']}",
            "Specific Skills or Tools Relevant to the Job": "{row['Specific Skills or Tools Relevant to the Job']}",
            "Specific Roles, Teams, or Projects at the Company": "{row['Specific Roles, Teams, or Projects at the Company']}",
            "resume": {structured_data}
        }}
        """

        try:
            email = utils.generate_email(prompt, selected_template)
            config.write_email(row['Hiring Managers Name'], row['Company Name'], email)
        except Exception as e:
            return gr.Error(f"Error generating email for {row['Company Name']}: {str(e)}")

    return "Emails have been drafted and saved as Word documents."

def generate_and_download(name, company, ai_email):
    file_path = config.write_email(name, company, ai_email)
    return file_path

def bulk_generate_and_download():
    zip_file_path = config.return_bulk_file()
    return zip_file_path

with gr.Blocks(css="body { background: #f8fafc; font-family: 'Inter'; }") as demo:
    with gr.Tabs():
        with gr.TabItem("Single Email"):
            with gr.Row():
                with gr.Column(scale=1):
                    text1 = gr.Textbox(label="Hiring Manager's Name")
                    text2 = gr.Textbox(label="Company Name")
                    text3 = gr.Textbox(label="Industry/Field")
                    text4 = gr.Textbox(label="Specific Projects, Innovations, or Company Achievements")
                    text5 = gr.Textbox(label="Specific Skills or Tools Relevant to the Job")
                    text6 = gr.Textbox(label="Specific Roles, Teams, or Projects at the Company")
                    with gr.Row():
                        template = gr.Dropdown(choices=list(config.template.keys()), label="Select Email Template", interactive=True)
                    pdf_input = gr.File(label="Upload PDF", file_types=[".pdf", ".docx"], interactive=True, scale=1)
                    submit_btn = gr.Button("Submit")
                with gr.Column(scale=1):
                    output_box = gr.Textbox(label="Output", lines=10, autoscroll=True)
                    with gr.Row():
                        with gr.Column(scale=1):
                            write_btn = gr.Button("Draft Email")
                        with gr.Column(scale=1):
                            download_button = gr.File(label="Download Word Document")
                        

            state = gr.State()
            submit_btn.click(output, inputs=[pdf_input, text1, text2, text3, text4, text5, text6, template], outputs=[output_box, state])
            write_btn.click(generate_and_download, inputs=[text1, text2, state], outputs= [download_button])

        with gr.TabItem("Batch Email"):
            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input = gr.File(label="Upload PDF", file_types=[".pdf", ".docx"], interactive=True, scale=1)
                    excel_input = gr.File(label="Upload Excel", file_types=[".xlsx", ".csv"], interactive=True, scale=1)
                    with gr.Row():
                        template = gr.Dropdown(choices=list(config.template.keys()), label="Select Email Template", interactive=True)
                    submit_btn = gr.Button("Submit and Draft")
                with gr.Column(scale=1):
                    output_box = gr.Textbox(label="Output", lines=10, autoscroll=True)
                    with gr.Row():
                        with gr.Column(scale=1):
                            Zip_btn = gr.Button("Make Zip File")
                        with gr.Column(scale=1):
                            download_button = gr.File(label="Download ZIP File")

            submit_btn.click(bulk_output, inputs=[excel_input, pdf_input, template], outputs=[output_box])
            Zip_btn.click(bulk_generate_and_download, inputs=[], outputs=[download_button])

demo.launch()