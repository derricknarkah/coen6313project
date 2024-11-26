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

theme_template = PromptTemplate(
    input_variables=["text"],
    template=("Identify the main theme of the following text in a single word or a single sentence, "
        "and in one line provide a brief description for context -  do not exceed more than one line. Example: If the text discusses "
        "scientific paper, use the title of the paper as the theme "
        "and add '- Research Paper' to indicate its purpose. "
        "Example: If the title is 'Advances in Renewable Energy,' summarize as:\n\n"
        "'Advances in Renewable Energy - Research Paper'\n\n"
        "if the text is a story book, mention story name, theme accordingly"
        "Text:\n{text}\n\nTheme:")  
)

@app.route('/extract_theme', methods=['POST'])
def extract_theme():
    data = request.get_json()
    text = data.get('text', '')
    response = llm.generate([theme_template.format(text=text)])
    theme = response.generations[0][0].text.strip()
    return jsonify({"theme": theme})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
