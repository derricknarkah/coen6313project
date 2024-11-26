import os
import streamlit as st
from flask import Flask, request, jsonify
from threading import Thread
import requests
import pdfplumber
import time
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from dotenv import load_dotenv
import logging

# Load the API key from the .env file
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# LangChain setup with OpenAI API
llm = OpenAI(api_key=openai_api_key)

# Define improved templates for each type of extraction
theme_template = PromptTemplate(
    input_variables=["text"],
    template=(
        "Identify the main theme of the following text in a single word or a single sentence, "
        "and in one line provide a brief description for context -  do not exceed more than one line. Example: If the text discusses "
        "scientific paper, use the title of the paper as the theme "
        "and add '- Research Paper' to indicate its purpose. "
        "Example: If the title is 'Advances in Renewable Energy,' summarize as:\n\n"
        "'Advances in Renewable Energy - Research Paper'\n\n"
        "if the text is a story book, mention story name, theme accordingly"
        "Text:\n{text}\n\nTheme:"
    )
)

# Updated Character Template
character_template = PromptTemplate(
    input_variables=["text"],
    template=(
        "List the main characters in the following text, including a brief description "
        "for each character's role. Example:\n"
        "'John - a brave soldier; Sarah - a wise healer.'\n\n"
        "If the text is a scientific paper or a research paper, list authors in the format: 'Name - Author.'\n"
        "Text:\n{text}\n\nCharacters:"
    )
)

# Updated Introduction Template
intro_template = PromptTemplate(
    input_variables=["text"],
    template=(
        "Provide a one-paragraph summary of the main topic of the following text. "
        "Exclude unrelated details and focus on the central idea. Example: "
        "'This text provides an overview of the effects of climate change on marine ecosystems...'\n\n"
        "If the text is a scientific paper, summarize it as if writing an abstract. "
        "Text:\n{text}\n\nIntroduction:"
    )
)




# Function to split text into smaller chunks for OpenAI's API
def split_text(text, max_tokens=512):
    words = text.split()
    for i in range(0, len(words), max_tokens):
        chunk = ' '.join(words[i:i + max_tokens])
        if len(chunk.split()) <= max_tokens:
            yield chunk

# Flask route to handle POST requests for extraction
@app.route('/extract_info', methods=['POST'])
def extract_info():
    data = request.get_json()
    text = data.get('text', '')
    task = data.get('task', '')

    if not text or not task:
        return jsonify({"error": "Text or task not provided"}), 400

    summaries = []
    template = None
    if task == "theme":
        template = theme_template
    elif task == "characters":
        template = character_template
    elif task == "introduction":
        template = intro_template
    else:
        return jsonify({"error": "Invalid task"}), 400

    # Process each text chunk
    for chunk in split_text(text):
        try:
            response = llm.generate([template.format(text=chunk)])
            summaries.append(response.generations[0][0].text.strip())
        except Exception as e:
            logging.error(f"Error processing chunk: {e}")
            return jsonify({"error": str(e)}), 500

    combined_result = ' '.join(summaries)
    return jsonify({task: combined_result}), 200

# Function to run Flask app in the background
def run_flask():
    app.run(host='0.0.0.0', port=5001)

# Start Flask in a separate thread
thread = Thread(target=run_flask)
thread.daemon = True
thread.start()
time.sleep(2)

# Streamlit Interface
st.set_page_config(page_title="PDF Analysis App", page_icon="📄", layout="centered")

# Sidebar Header
st.sidebar.title("📘 PDF Analysis Tool")
st.sidebar.write("Extract key information from your documents effortlessly.")

# Main App Header
st.title("📄 PDF & Text Analysis")
st.markdown("#### Extract important elements like **Theme**, **Characters**, and a **Brief Introduction**.")

# Text input section for manual entry
st.subheader("📝 Extract Information from Text")
st.write("Enter or paste your text below, and select the information you want to extract.")

# Input box for text and dropdown for task selection
article = st.text_area("Enter text here", height=200, placeholder="Type or paste your text here...")
task_option = st.selectbox("Choose Task:", ["Theme", "Characters", "Introduction"])
task_map = {"Theme": "theme", "Characters": "characters", "Introduction": "introduction"}

# Analyze button for text input
if st.button("🔍 Analyze Text"):
    if article:
        with st.spinner("Processing..."):
            response = requests.post("http://localhost:5001/extract_info", json={"text": article, "task": task_map[task_option]})
            if response.status_code == 200:
                st.success(f"{task_option}:")
                st.write(response.json().get(task_map[task_option], 'No result'))
            else:
                st.error("Error processing request")
    else:
        st.warning("Please enter text to analyze.")

# Divider
st.markdown("---")

# PDF Upload and Page Range Input
st.subheader("📂 Extract Information from PDF")
st.write("Upload a PDF document, specify the page range, and select the type of information you want to extract.")

# PDF upload section
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# Extract text from PDF function with cleaning
# Improved Extract Text from PDF function with additional cleaning
def extract_text_from_pdf(file, start_page, end_page):
    text = ''
    with pdfplumber.open(file) as pdf:
        for i in range(start_page - 1, end_page):  # Adjust for zero-based indexing
            try:
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    # Handle hyphenated line breaks
                    page_text = page_text.replace("-\n", "")
                    
                    # Replace newlines with space
                    page_text = page_text.replace("\n", " ")
                    
                    # Remove special or non-ASCII characters
                    page_text = ''.join(char for char in page_text if char.isprintable())
                    
                    # Remove excessive spaces
                    page_text = ' '.join(page_text.split())
                    
                    # Append cleaned page text to the overall text
                    text += page_text + " "
            except IndexError:
                st.error(f"Page {i+1} is out of range.")
                break
    return text.strip()


# Page selection dropdowns based on PDF upload
if uploaded_file is not None:
    with pdfplumber.open(uploaded_file) as pdf:
        total_pages = len(pdf.pages)

    start_page = st.selectbox("Start Page", options=list(range(1, total_pages + 1)), index=0)
    end_page = st.selectbox("End Page", options=list(range(1, total_pages + 1)), index=total_pages - 1)

    if st.button("📄 Extract and Analyze PDF"):
        if start_page <= end_page:
            with st.spinner("Extracting text from PDF..."):
                extracted_text = extract_text_from_pdf(uploaded_file, start_page, end_page)

            if extracted_text:
                #st.subheader("Extracted Text:")
                #st.text_area("Extracted Text", extracted_text, height=200)

                # Process extracted PDF text
                with st.spinner("Analyzing..."):
                    response = requests.post("http://localhost:5001/extract_info", json={"text": extracted_text, "task": task_map[task_option]})
                    if response.status_code == 200:
                        st.subheader(f"{task_option}:")
                        st.success(response.json().get(task_map[task_option], 'No result'))
                    else:
                        st.error("Error processing request")
            else:
                st.error("Could not extract text from the specified page range.")
        else:
            st.warning("End page must be greater than or equal to start page.")
