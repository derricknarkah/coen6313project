import streamlit as st
import requests
import pdfplumber

# Microservice endpoints
microservice_urls = {
    "characters": "http://characters_service:5001/extract_characters",
    "introduction": "http://introduction_service:5001/extract_introduction",
    "theme": "http://theme_service:5001/extract_theme",
    "sentiment": "http://sentiment_service:5001/extract_sentiment"  
}

task_map = {
    "Theme": "theme",
    "Characters": "characters",
    "Introduction": "introduction",
    "Sentiment": "sentiment"
}

st.set_page_config(page_title="Atomize+ PDF Analysis App", page_icon="📄", layout="centered")

# Sidebar Header
st.sidebar.title("📘 Atomize+ PDF Analysis Tool")
st.sidebar.write("Extract key information from your documents effortlessly.")

# Main App Header
st.title("📄 PDF & Text Analysis")
st.markdown("#### Extract important elements like **Theme**, **Characters**, and a **Brief Introduction**.")

# Text input section for manual entry
st.subheader("📝 Extract Information from Text")
st.write("Enter or paste your text below, and select the information you want to extract.")

# Input box for text and dropdown for task selection
article = st.text_area("Enter text here", height=200, placeholder="Type or paste your text here...")
#task_option = st.selectbox("Choose Task:", ["Characters", "Introduction", "Theme"])
task_option = st.selectbox("Choose Task:", ["Characters", "Introduction", "Theme","Sentiment"])

# Analyze button for text input
if st.button("🔍 Analyze Text"):
    if article:
        with st.spinner("Processing..."):
            try:
                # Make the request
                response = requests.post(microservice_urls[task_map[task_option]], json={"text": article})
                if response.status_code == 200:
                    result = response.json().get(task_map[task_option], 'No result found')
                    st.success(f"{task_option}: {result}")
                else:
                    st.error("Error processing request")
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")

# Divider
st.markdown("---")

# PDF Upload and Page Range Input
st.subheader("📂 Extract Information from PDF")
st.write("Upload a PDF document, specify the page range, and select the type of information you want to extract.")

# PDF upload section
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# PDF Task Selection Dropdown
#pdf_task_option = st.selectbox("Choose PDF Task:", ["Characters", "Introduction", "Theme"])
pdf_task_option = st.selectbox("Choose PDF Task:", ["Characters", "Introduction", "Theme","Sentiment"])

# Extract text from PDF function with cleaning
def extract_text_from_pdf(file, start_page, end_page):
    text = ''
    with pdfplumber.open(file) as pdf:
        for i in range(start_page - 1, end_page):  # Adjust for zero-based indexing
            try:
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    page_text = page_text.replace("-\n", "").replace("\n", " ")
                    text += ' '.join(page_text.split()) + " "
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
                with st.spinner("Analyzing..."):
                    try:
                        # Use pdf_task_option for the PDF analysis section
                        response = requests.post(microservice_urls[task_map[pdf_task_option]], json={"text": extracted_text})
                        if response.status_code == 200:
                            result = response.json().get(task_map[pdf_task_option], 'No result found')
                            st.subheader(f"{pdf_task_option}:")
                            st.success(result)
                        else:
                            st.error("Error processing request")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Request failed: {e}")
            else:
                st.error("Could not extract text from the specified page range.")
        else:
            st.warning("End page must be greater than or equal to start page.")
