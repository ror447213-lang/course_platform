from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
import aiofiles
import qrcode
from io import BytesIO
import base64
from database import get_db
import models
import schemas
import auth

router = APIRouter(prefix="/api/payments", tags=["Payments"])

UPLOAD_DIR = "uploads/screenshots"
os.makedirs(UPLOAD_DIR, exist_ok=True)

UPI_ID = os.getenv("UPI_ID", "rohit.hacrr@fam")
UPI_NAME = os.getenv("UPI_NAME", "CourseStore")

@router.get("/qr/{course_id}")
def generate_qr(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    course = db.query(models.Course).filter(
        models.Course.id == course_id,
        models.Course.is_active == True
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing_purchase = db.query(models.Purchase).filter(
        models.Purchase.user_id == current_user.id,
        models.Purchase.course_id == course_id
    ).first()
    if existing_purchase:
        raise HTTPException(status_code=400, detail="Already purchased this course")

    upi_url = f"upi://pay?pa={UPI_ID}&pn={UPI_NAME}&am={course.price:.2f}&cu=INR&tn=Course-{course.id}"

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(upi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#4F46E5", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        "qr_code": f"data:image/png;base64,{qr_base64}",
        "upi_id": UPI_ID,
        "amount": course.price,
        "course_title": course.title,
        "upi_url": upi_url
    }

@router.post("/submit/{course_id}", response_model=schemas.PaymentOut)
async def submit_payment(
    course_id: int,
    utr_number: Optional[str] = Form(None),
    screenshot: Optional[UploadFile] = File(None),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(models.Course).filter(
        models.Course.id == course_id,
        models.Course.is_active == True
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing_purchase = db.query(models.Purchase).filter(
        models.Purchase.user_id == current_user.id,
        models.Purchase.course_id == course_id
    ).first()
    if existing_purchase:
        raise HTTPException(status_code=400, detail="Already purchased this course")

    existing_pending = db.query(models.Payment).filter(
        models.Payment.user_id == current_user.id,
        models.Payment.course_id == course_id,
        models.Payment.status == models.PaymentStatus.PENDING
    ).first()
    if existing_pending:
        raise HTTPException(status_code=400, detail="You already have a pending payment for this course")

    if not utr_number and not screenshot:
        raise HTTPException(status_code=400, detail="Please provide UTR number or payment screenshot")

    screenshot_path = None
    if screenshot:
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if screenshot.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        file_ext = screenshot.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        async with aiofiles.open(file_path, 'wb') as f:
            content = await screenshot.read()
            if len(content) > 5 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="File size must be less than 5MB")
            await f.write(content)
        screenshot_path = file_path

    payment = models.Payment(
        user_id=current_user.id,
        course_id=course_id,
        amount=course.price,
        utr_number=utr_number,
        screenshot_path=screenshot_path,
        status=models.PaymentStatus.PENDING
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

@router.get("/my-payments", response_model=list[schemas.PaymentOut])
def get_my_payments(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Payment).filter(
        models.Payment.user_id == current_user.id
    ).order_by(models.Payment.created_at.desc()).all()
