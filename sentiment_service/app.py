# sentiment_service/app.py
from flask import Flask, request, jsonify
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load API key from .env file
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
llm = OpenAI(api_key=openai_api_key)

# Define the prompt template for sentiment analysis
sentiment_template = PromptTemplate(
    input_variables=["text"],
    template="Analyze the sentiment of the following text and determine if it is Positive, Negative, or Neutral:\n\nText:\n{text}\n\nSentiment:"
)

@app.route('/sentiment', methods=['POST'])
def extract_sentiment():
    data = request.get_json()
    text = data.get('text', '')
    response = llm.generate([sentiment_template.format(text=text)])
    sentiment = response.generations[0][0].text.strip()
    return jsonify({"sentiment": sentiment})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
