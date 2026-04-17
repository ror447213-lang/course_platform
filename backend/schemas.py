from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from models import PaymentStatus, UserRole

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

    @validator("password")
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @validator("name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

class CourseCreate(BaseModel):
    title: str
    description: str
    price: float
    thumbnail_url: Optional[str] = None
    download_link: str

    @validator("price")
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    thumbnail_url: Optional[str] = None
    download_link: Optional[str] = None
    is_active: Optional[bool] = None

class CourseOut(BaseModel):
    id: int
    title: str
    description: str
    price: float
    thumbnail_url: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CourseOutWithDownload(CourseOut):
    download_link: str

class PaymentCreate(BaseModel):
    course_id: int
    utr_number: Optional[str] = None

class PaymentOut(BaseModel):
    id: int
    course_id: int
    amount: float
    utr_number: Optional[str]
    screenshot_path: Optional[str]
    status: PaymentStatus
    admin_note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentAdminOut(PaymentOut):
    user_id: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    course_title: Optional[str] = None

class PaymentVerify(BaseModel):
    status: PaymentStatus
    admin_note: Optional[str] = None

class AdminStats(BaseModel):
    total_users: int
    total_courses: int
    total_sales: int
    pending_payments: int
    total_revenue: float

class UserDashboard(BaseModel):
    user: UserOut
    purchased_courses: List[CourseOutWithDownload]
    pending_payments: List[PaymentOut]
