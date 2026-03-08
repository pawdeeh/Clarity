#!/usr/bin/env python3
"""
Create a default admin account for testing.
Usage: python3 create_admin.py
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import User
from app.auth import hash_password
from app.database import SQLALCHEMY_DATABASE_URL
import os

async def create_admin():
    """Create a default admin account"""
    # Create async engine
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Check if admin already exists
        from sqlalchemy import select
        stmt = select(User).where(User.email == "admin@clarity.local")
        result = await session.execute(stmt)
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print(f"✓ Admin account already exists: {existing_admin.email}")
            return
        
        # Create admin user
        admin_user = User(
            email="admin@clarity.local",
            full_name="Admin User",
            password_hash=hash_password("admin123"),
            is_active=True,
            role="admin"
        )
        
        session.add(admin_user)
        await session.commit()
        
        print(f"✓ Admin account created successfully!")
        print(f"  Email: admin@clarity.local")
        print(f"  Password: admin123")
        print(f"  Role: admin")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_admin())
