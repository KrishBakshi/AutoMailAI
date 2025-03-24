import gradio as gr
import os
import utils
import config
import pandas as pd

def output(file, text1, text2, text3, text4, text5, text6):

    output_text = "" 

    if file is None:
        return "No file uploaded."

    file_path = file.name
    structured_data = utils.process_resume(file_path)
    if structured_data is None:
        return "Unsupported file type."

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

    output_text = utils.generate_email(prompt)
    
    return output_text, output_text

def bulk_output(excel, pdf):
    if excel is None:
        return "No file uploaded."

    excel_path = excel.name
    df = pd.read_excel(excel_path)
    emails = []

    if pdf is None:
        return "No file uploaded."

    file_path = pdf.name
    structured_data = utils.process_resume(file_path)
    if structured_data is None:
        return "Unsupported file type."
    
    for index, row in df.iterrows():
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

        email = utils.generate_email(prompt)
        config.write_email(row['Hiring Manager\'s Name'], row['Company Name'], email)

    return "Emails have been drafted and saved as Word documents."

with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.TabItem("Single Email"):
            with gr.Row():
                with gr.Column(scale=0.5):
                    text1 = gr.Textbox(label="Hiring Manager's Name")
                    text2 = gr.Textbox(label="Company Name")
                    text3 = gr.Textbox(label="Industry/Field")
                    text4 = gr.Textbox(label="Specific Projects, Innovations, or Company Achievements")
                    text5 = gr.Textbox(label="Specific Skills or Tools Relevant to the Job")
                    text6 = gr.Textbox(label="Specific Roles, Teams, or Projects at the Company")
                    submit_btn = gr.Button("Submit")
                with gr.Column(scale=0.5):
                    pdf_input = gr.File(label="Upload PDF", file_types=[".pdf", ".docx"], interactive=True, scale=1)
                    output_box = gr.Textbox(label="Output", lines=10, autoscroll=True)
                    write_btn = gr.Button("Draft Email")
                    progress_bar = gr.Progress()

            state = gr.State()
            submit_btn.click(output, inputs=[pdf_input, text1, text2, text3, text4, text5, text6], outputs=[output_box, state])
            write_btn.click(config.write_email, inputs=[text1, text2, state])

        with gr.TabItem("Batch Email"):
            with gr.Row():
                with gr.Column(scale=0.5):
                    pdf_input = gr.File(label="Upload PDF", file_types=[".pdf", ".docx"], interactive=True, scale=1)
                    excel_input = gr.File(label="Upload Excel", file_types=[".xlsx"], interactive=True, scale=1)
                    submit_btn = gr.Button("Submit and Draft")
                with gr.Column(scale=0.5):
                    output_box = gr.Textbox(label="Output", lines=10, autoscroll=True)
                    progress_bar = gr.Progress()

            submit_btn.click(bulk_output, inputs=[excel_input,pdf_input], outputs=[output_box])

demo.launch()