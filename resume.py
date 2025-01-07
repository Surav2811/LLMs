# import os
# import requests
#from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader
#from docx import Document
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
from tkinter.ttk import Progressbar

# Load environment variables
# load_dotenv(override=True)
# api_key = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

def parse_pdf(file_path):
    """Parse a PDF file and extract its text."""
    content = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            content += page.extract_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return content

# def parse_word(file_path):
#     """Parse a Word file and extract its text."""
#     content = ""
#     try:
#         doc = Document(file_path)
#         for paragraph in doc.paragraphs:
#             content += paragraph.text + "\n"
#     except Exception as e:
#         print(f"Error reading Word file: {e}")
#     return content

def parse_file(file_path):
    """Determine file type and parse accordingly."""
    if file_path.lower().endswith('.pdf'):
        return parse_pdf(file_path)
    # elif file_path.lower().endswith('.docx'):
    #     return parse_word(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a PDF or Word (.docx) file.")

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf"), ("Word Files", "*.docx")])
    if file_path:
        try:
            file_content = parse_file(file_path)
            input_text.delete(1.0, tk.END)
            input_text.insert(tk.END, file_content)
        except Exception as e:
            input_text.delete(1.0, tk.END)
            input_text.insert(tk.END, f"Error: {e}")

def submit():
    file_content = input_text.get(1.0, tk.END).strip()
    job_description = job_desc_text.get(1.0, tk.END).strip()
    job_link = job_link_entry.get().strip()

    if not file_content:
        messagebox.showerror("Error", "Please load a resume file first.")
        return

    if not job_description and not job_link:
        messagebox.showerror("Error", "Please provide either a job description or a job link.")
        return
    elif job_description and job_link:
        messagebox.showerror("Error", "Please provide only one: a job description or a job link, not both.")
        return

    # Start loading bar
    progress_bar.start(10)
    root.update_idletasks()

    system_prompt = """You are an expert in resume customization and optimization. Your primary role is to analyze a provided resume and update it based on a job description given either as plain text or extracted from a provided link. 

1. Extract key requirements from the job description, such as skills, experience, and qualifications.
2. Update the resume by:
   - Highlighting relevant skills and experiences that match the job requirements.
   - Optimizing the content for Applicant Tracking Systems (ATS).
   - Using professional, action-oriented language and quantitative metrics where applicable.
   - Reorganizing or prioritizing sections to align with the job description.
3. Ensure the resume remains concise, professional, and well-structured, adhering to industry standards.
4. At the end of the updated resume, provide a concise summary of the changes made. Explain how these updates improve alignment with the job description.

Input Examples:
- A resume and a job description as plain text.
- A resume and a link to a job posting.

Output:
- The updated resume.
- A brief paraphrased summary of the modifications and how they address the job description.

Your response should consist of the updated resume first, followed by the paraphrased summary of changes.
"""
    user_prompt = f"""
    Please check my resume for SQL senior developer in BFSI domain.
    The resume content is as follows:
    {file_content}

    Job Information:
    {job_description if job_description else f"Job Link: {job_link}"}
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = openai.chat.completions.create(model="llama3.2", messages=messages)
    response_markdown = response.choices[0].message.content

    # Stop loading bar
    progress_bar.stop()
    progress_bar["value"] = 0

    # Switch to the response tab and display the result
    notebook.select(response_tab)
    response_text.delete(1.0, tk.END)
    response_text.insert(tk.END, response_markdown)

# Create the main window
root = tk.Tk()
root.title("Resume Parser and Enhancer")

# Create a notebook (tabbed interface)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Create input tab
input_tab = ttk.Frame(notebook)
notebook.add(input_tab, text="Input")

# Create response tab
response_tab = ttk.Frame(notebook)
notebook.add(response_tab, text="Response")

# Input Tab Layout
input_frame = ttk.Frame(input_tab)
input_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Resume Section
resume_label = ttk.Label(input_frame, text="Resume Content:")
resume_label.grid(row=0, column=0, sticky="w")

input_text = scrolledtext.ScrolledText(input_frame, width=50, height=20)
input_text.grid(row=1, column=0, padx=5, pady=5)

# Job Description Section
job_desc_label = ttk.Label(input_frame, text="Job Description (or):")
job_desc_label.grid(row=0, column=1, sticky="w")

job_desc_text = scrolledtext.ScrolledText(input_frame, width=50, height=20)
job_desc_text.grid(row=1, column=1, padx=5, pady=5)

# Job Link Section
job_link_label = ttk.Label(input_frame, text="Job Link (or):")
job_link_label.grid(row=2, column=0, sticky="w")

job_link_entry = ttk.Entry(input_frame, width=50)
job_link_entry.grid(row=3, column=0, padx=5, pady=5)

# Buttons
button_frame = ttk.Frame(input_frame)
button_frame.grid(row=4, column=0, columnspan=2, pady=10)

open_button = ttk.Button(button_frame, text="Upload Resume", command=open_file)
open_button.pack(side="left", padx=5)

submit_button = ttk.Button(button_frame, text="Submit", command=submit)
submit_button.pack(side="left", padx=5)

# Progress Bar
progress_bar = Progressbar(button_frame, orient="horizontal", length=200, mode="indeterminate")
progress_bar.pack(side="left", padx=5)

# Response Tab Layout
response_text = scrolledtext.ScrolledText(response_tab, width=100, height=30)
response_text.pack(fill="both", expand=True, padx=10, pady=10)

# Start the main loop
root.mainloop()