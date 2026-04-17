# CourseStore - Digital Course Selling Platform

## Quick Start

### 1. Setup Backend
cd course_platform/backend
python -m venv venv
source venv/bin/activate  (Linux/Mac)
venv\Scripts\activate     (Windows)
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000

### 2. Open in Browser
http://localhost:8000

### Default Admin Login
Email: admin@coursestore.com
Password: Admin@123456

### API Docs
http://localhost:8000/docs
