from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import models
import auth
from database import engine, get_db
from routers import auth_router, courses, payments, admin

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CourseStore API",
    description="Digital Course Selling Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(courses.router)
app.include_router(payments.router)
app.include_router(admin.router)

os.makedirs("uploads/screenshots", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(os.path.join(frontend_path, "css")):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_path, "css")), name="css")
if os.path.exists(os.path.join(frontend_path, "js")):
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")
if os.path.exists(os.path.join(frontend_path, "admin")):
    app.mount("/admin", StaticFiles(directory=os.path.join(frontend_path, "admin"), html=True), name="admin_static")

@app.get("/")
async def root():
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "CourseStore API Running"}

@app.get("/login.html")
async def login_page():
    return FileResponse(os.path.join(frontend_path, "login.html"))

@app.get("/register.html")
async def register_page():
    return FileResponse(os.path.join(frontend_path, "register.html"))

@app.get("/dashboard.html")
async def dashboard_page():
    return FileResponse(os.path.join(frontend_path, "dashboard.html"))

@app.get("/course_detail.html")
async def course_detail_page():
    return FileResponse(os.path.join(frontend_path, "course_detail.html"))

@app.get("/payment.html")
async def payment_page():
    return FileResponse(os.path.join(frontend_path, "payment.html"))

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.on_event("startup")
async def create_admin():
    db = next(get_db())
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@coursestore.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "Admin@123456")
        existing = db.query(models.User).filter(models.User.email == admin_email).first()
        if not existing:
            admin_user = models.User(
                name="Admin",
                email=admin_email,
                hashed_password=auth.hash_password(admin_password),
                role=models.UserRole.ADMIN
            )
            db.add(admin_user)
            db.commit()
            print(f"Admin created: {admin_email}")
        else:
            print(f"Admin exists: {admin_email}")
    finally:
        db.close()
