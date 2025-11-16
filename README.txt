ACTIVATES VENV (PLEASE USE IN BACKEND FOLDER):
.\venv\Scripts\activate

FREEZES REQUIREMENTS:
pip freeze > requirements.txt

RUN UVICORN:
uvicorn app.main:app --reload

CLOSE UVICORN:
ctrl + c