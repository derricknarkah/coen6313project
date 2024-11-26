from flask import Flask, request, jsonify
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import os
from dotenv import load_dotenv
import logging


app = Flask(__name__)


# Load the API key from the .env file
#load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
llm = OpenAI(api_key=openai_api_key)

character_template = PromptTemplate(
    input_variables=["text"],
    template=("List the main characters in the following text, including a brief description "
              "for each character's role. Example:\n"
              "'John - a brave soldier; Sarah - a wise healer.'\n\n"
              "If the text is a scientific paper, list authors in the format: 'Name - Author.'\n"
              "Text:\n{text}\n\ncharacters:")
)

@app.route('/extract_characters', methods=['POST'])
def extract_characters():
    data = request.get_json()
    text = data.get('text', '')
    response = llm.generate([character_template.format(text=text)])
    characters = response.generations[0][0].text.strip()
    return jsonify({"characters": characters})  # Ensure response key matches expected key

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
