from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas
import auth

router = APIRouter(prefix="/api/courses", tags=["Courses"])

@router.get("/", response_model=List[schemas.CourseOut])
def list_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).filter(models.Course.is_active == True).all()

@router.get("/{course_id}", response_model=schemas.CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(
        models.Course.id == course_id,
        models.Course.is_active == True
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.get("/{course_id}/download")
def get_download_link(
    course_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    purchase = db.query(models.Purchase).filter(
        models.Purchase.user_id == current_user.id,
        models.Purchase.course_id == course_id
    ).first()
    if not purchase:
        raise HTTPException(status_code=403, detail="You have not purchased this course")
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    return {"download_link": course.download_link, "course_title": course.title}

@router.post("/admin/create", response_model=schemas.CourseOut, status_code=201)
def create_course(
    course_data: schemas.CourseCreate,
    admin: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(get_db)
):
    course = models.Course(**course_data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.put("/admin/{course_id}", response_model=schemas.CourseOut)
def update_course(
    course_id: int,
    course_data: schemas.CourseUpdate,
    admin: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(get_db)
):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    update_data = course_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return course

@router.delete("/admin/{course_id}")
def delete_course(
    course_id: int,
    admin: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(get_db)
):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    course.is_active = False
    db.commit()
    return {"message": "Course deactivated successfully"}

@router.get("/admin/all/list", response_model=List[schemas.CourseOutWithDownload])
def admin_list_courses(
    admin: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Course).all()
