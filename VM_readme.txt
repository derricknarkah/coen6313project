Steps to run virtual machine:
1. open terminal -> navigate to pdf_app folder
2. ssh -i PDF-Extractor_key.pem azureuser@20.9.131.32
3. cd pdf_extractor/
(if u want to check api key ----> cat .env)
4. source venv/bin/activate
5. (if 1st time) pip install streamlit flask pdfplumber requests langchain openai python-dotenv langchain_community
6. streamlit run app.py --server.port 8501 --server.address 0.0.0.0


Steps to enter in tmux:
1. sudo apt install tmux -y (and create new app  --> tmux new -s myapp)
2. tmux attach -t myapp (if already created myapp using --> tmux new -s myapp)
3. streamlit run app.py --server.port 8501 --server.address 0.0.0.0  (inside tmux)
4. to stop session do CTRL+C
5. to exit type exit
6. to leave app running, just exit using ---> Ctrl + B, then D
7. to kill the session --> tmux kill-session -t myapp


Steps to copy content from local pc to azure vm:
scp -i PDF-Extractor_key.pem app.py .env azureuser@20.9.131.32:/home/azureuser/pdf_extractor/
(Assuming PDF-Extractor_key.pem is in the same folder as app.py)