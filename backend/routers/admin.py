from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from fastapi.responses import FileResponse
import os
from database import get_db
import models
import schemas
import auth
from email_service import send_purchase_confirmation, send_rejection_email

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/stats", response_model=schemas.AdminStats)
def get_stats(
    admin: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(get_db)
):
    total_users = db.query(models.User).filter(models.User.role == models.UserRole.USER).count()
    total_courses = db.query(models.Course).filter(models.Course.is_active == True).count()
    total_sales = db.query(models.Purchase).count()
    pending_payments = db.query(models.Payment).filter(
        models.Payment.status == models.PaymentStatus.PENDING
    ).count()
    total_revenue = db.query(func.sum(models.Payment.amount)).filter(
        models.Payment.status == models.PaymentStatus.APPROVED
    ).scalar() or 0.0
    return {
        "total_users": total_users,
        "total_courses": total_courses,
        "total_sales": total_sales,
        "pending_payments": pending_payments,
        "total_revenue": total_revenue
    }

@router.get("/payments", response_model=List[schemas.PaymentAdminOut])
def get_all_payments(
    status: str = None,
    admin: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Payment)
    if status:
        query = query.filter(models.Payment.status == status)
    payments = query.order_by(models.Payment.created_at.desc()).all()
    result = []
    for p in payments:
        result.append(schemas.PaymentAdminOut(
            id=p.id,
            course_id=p.course_id,
            user_id=p.user_id,
            amount=p.amount,
            utr_number=p.utr_number,
            screenshot_path=p.screenshot_path,
            status=p.status,
            admin_note=p.admin_note,
            created_at=p.created_at,
            user_name=p.user.name if p.user else None,
            user_email=p.user.email if p.user else None,
            course_title=p.course.title if p.course else None,
        ))
    return result

@router.post("/payments/{payment_id}/verify")
async def verify_payment(
    payment_id: int,
    verify_data: schemas.PaymentVerify,
    admin: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(get_db)
):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status != models.PaymentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Payment already processed")

    payment.status = verify_data.status
    payment.admin_note = verify_data.admin_note

    if verify_data.status == models.PaymentStatus.APPROVED:
        existing_purchase = db.query(models.Purchase).filter(
            models.Purchase.user_id == payment.user_id,
            models.Purchase.course_id == payment.course_id
        ).first()
        if not existing_purchase:
            purchase = models.Purchase(
                user_id=payment.user_id,
                course_id=payment.course_id,
                payment_id=payment.id
            )
            db.add(purchase)
        db.commit()
        await send_purchase_confirmation(
            user_email=payment.user.email,
            user_name=payment.user.name,
            course_title=payment.course.title,
            download_link=payment.course.download_link
        )
        return {"message": "Payment approved and email sent", "status": "approved"}

    elif verify_data.status == models.PaymentStatus.REJECTED:
        db.commit()
        await send_rejection_email(
            user_email=payment.user.email,
            user_name=payment.user.name,
            course_title=payment.course.title,
            admin_note=verify_data.admin_note
        )
        return {"message": "Payment rejected and user notified", "status": "rejected"}

@router.get("/screenshot/{payment_id}")
def get_screenshot(
    payment_id: int,
    admin: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(get_db)
):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not payment or not payment.screenshot_path:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    if not os.path.exists(payment.screenshot_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(payment.screenshot_path)

@router.get("/users")
def get_all_users(
    admin: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(get_db)
):
    users = db.query(models.User).filter(models.User.role == models.UserRole.USER).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "created_at": u.created_at} for u in users]
