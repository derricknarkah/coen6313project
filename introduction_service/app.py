from flask import Flask, request, jsonify
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load the API key from the .env file
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
llm = OpenAI(api_key=openai_api_key)

intro_template = PromptTemplate(
    input_variables=["text"],
    template=("Provide a one-paragraph summary of the main topic of the following text. "
              "Exclude unrelated details and focus on the central idea. Example: "
              "'This text provides an overview of the effects of climate change on marine ecosystems...'\n\n"
              "If the text is a scientific paper, summarize it as if writing an abstract. "
              "Text:\n{text}\n\nintroduction:")
)

@app.route('/extract_introduction', methods=['POST'])
def extract_introduction():
    data = request.get_json()
    text = data.get('text', '')
    response = llm.generate([intro_template.format(text=text)])
    introduction = response.generations[0][0].text.strip()
    return jsonify({"introduction": introduction})  # Ensure response key matches expected key

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
