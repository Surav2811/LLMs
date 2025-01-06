# imports

import os
import requests
from dotenv import load_dotenv
#from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI
from PyPDF2 import PdfReader

# Load environment variables

# load_dotenv(override=True)
# api_key = os.getenv('OPENAI_API_KEY')

# # Check the key

# if not api_key:
#     print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
# elif not api_key.startswith("sk-proj-"):
#     print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
# elif api_key.strip() != api_key:
#     print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
# else:
#     print("API key found and looks good so far!")

#openai = OpenAI()
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

def parse_word(file_path):
    """Parse a Word file and extract its text."""
    content = ""
    try:
        doc = Document(file_path)
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
    except Exception as e:
        print(f"Error reading Word file: {e}")
    return content

def parse_file(file_path):
    """Determine file type and parse accordingly."""
    if file_path.lower().endswith('.pdf'):
        return parse_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        return parse_word(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a PDF or Word (.docx) file.")

# Example usage
if __name__ == "__main__":
    file_path = input(r"Enter the path to the PDF or Word file: ").strip()
    if not os.path.exists(file_path):
        print("File does not exist. Please provide a valid path.")
    else:
        try:
            file_content = parse_file(file_path)
            #print("\nExtracted Content:\n")
            #print(file_content)
        except Exception as e:
            print(f"Error: {e}")

# Step 1: Create your prompts

system_prompt = "You are a HR expert in resume building and parsing. You have to check the resume and then Markdown the issues. Update the resume with buzz words and some percents. Bold and highlight the words which should make the resume more catching. Write your response in Markdown"
user_prompt = """
 Please check my resume for SQL senior developer in BFSI domain.
 The resume content are as follows:
""" + file_content

# Step 2: Make the messages list

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
] # fill this in

# Step 3: Call OpenAI

response = openai.chat.completions.create(model="llama3.2", messages=messages)

# Step 4: print the result
response_markdown = response.choices[0].message.content
display(Markdown(response_markdown))

