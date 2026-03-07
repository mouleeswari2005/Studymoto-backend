"""
Content management REST endpoints (FAQ, Contact, Blog).
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models.content import FAQ, ContactMessage, BlogPost
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/content", tags=["content"])


# Contact Form Schema
class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    subject: Optional[str] = None
    message: str


# FAQ Endpoints
@router.get("/faqs", response_model=List[dict])
async def get_faqs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get public FAQs."""
    query = select(FAQ).where(FAQ.is_active == True).order_by(FAQ.order.asc()).offset(skip).limit(limit)
    result = await db.execute(query)
    faqs = result.scalars().all()
    return [
        {
            "id": faq.id,
            "question": faq.question,
            "answer": faq.answer,
            "category": faq.category,
        }
        for faq in faqs
    ]


# Contact Form Endpoint
@router.post("/contact", status_code=status.HTTP_201_CREATED)
async def submit_contact(
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db)
):
    """Submit contact form."""
    new_message = ContactMessage(
        name=contact_data.name,
        email=contact_data.email,
        subject=contact_data.subject,
        message=contact_data.message,
    )
    
    db.add(new_message)
    await db.commit()
    
    return {"message": "Contact message submitted successfully"}


# Blog Posts Endpoints
@router.get("/blog", response_model=List[dict])
async def get_blog_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get published blog posts."""
    query = (
        select(BlogPost)
        .where(BlogPost.is_published == True)
        .order_by(BlogPost.publish_date.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    posts = result.scalars().all()
    return [
        {
            "id": post.id,
            "title": post.title,
            "excerpt": post.excerpt,
            "tags": post.tags,
            "author": post.author,
            "publish_date": post.publish_date.isoformat() if post.publish_date else None,
            "created_at": post.created_at.isoformat(),
        }
        for post in posts
    ]


@router.get("/blog/{post_id}", response_model=dict)
async def get_blog_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific blog post."""
    result = await db.execute(
        select(BlogPost).where(
            BlogPost.id == post_id,
            BlogPost.is_published == True
        )
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "excerpt": post.excerpt,
        "tags": post.tags,
        "author": post.author,
        "publish_date": post.publish_date.isoformat() if post.publish_date else None,
        "created_at": post.created_at.isoformat(),
    }

