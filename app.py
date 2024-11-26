import streamlit as st
from flask import Flask, request, jsonify
from transformers import pipeline
from threading import Thread
import requests
from flask_cors import CORS
from pyngrok import ngrok

ngrok.set_auth_token('2mr9nENSIUVUd5sa0t8Rhvl2y6t_5fVGRGa7vwF6tftY4mof2')

# Initialize the summarizer model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Initialize Flask app
app = Flask(__name__)
CORS(app)
# Flask route to handle POST requests for summarization
@app.route('/summarize', methods=['POST'])
def summarize_article():
    data = request.get_json()
    article = data.get('article', '')

    # Check if the article is provided
    if not article:
        return jsonify({"error": "No article provided"}), 400

    # Summarize the article
    summary = summarizer(article, max_length=130, min_length=30, do_sample=False)

    # Return the summary
    return jsonify({"summary": summary[0]['summary_text']}), 200

# Function to run Flask app in the background
def run_flask():

     public_url = ngrok.connect(5001)  # Expose Flask app on port 5001
     print("ngrok URL:", public_url)  # Print the public ngrok URL

     # Run the Flask app
     app.run(host='0.0.0.0', port=5001)




# Start the Flask app in a separate thread
thread = Thread(target=run_flask)
thread.daemon = True
thread.start()

# Streamlit Interface
st.title("Article Summarization App")

# Text input for user to manually enter the article
article = st.text_area("Enter the article you want to summarize", height=300)

# Button to summarize the article
if st.button("Summarize"):
    if article:
        summary = summarizer(article, max_length=130, min_length=30, do_sample=False)
        st.subheader("Summary:")
        st.write(summary[0]['summary_text'])
    else:
        st.error("Please enter an article to summarize.")

# You can also show a simple way to test POST request in the Streamlit app
st.subheader("Test POST Request to the API")
url = st.text_input("Enter API URL", "http://localhost:5001/summarize")
article_test = st.text_area("Enter article for API request", height=200)

if st.button("Test API"):
    if article_test:
        response = requests.post(url, json={"article": article_test})
        if response.status_code == 200:
            st.success("API Request Successful!")
            st.write("Summary: ", response.json()['summary'])
        else:
            st.error(f"API Request Failed with status code {response.status_code}")
    else:
        st.error("Please enter an article to test the API.")
