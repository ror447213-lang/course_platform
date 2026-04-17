@echo off
echo Starting CourseStore...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt -q
uvicorn main:app --reload --port 8000
pause
