#!/usr/bin/env python3
"""
Initialize default admin account for Clarity.
Runs after database migrations during Docker startup.
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Base, User
from app.auth import hash_password

# Use the same database URL as app/database.py
DATABASE_URL = "postgresql+asyncpg://myuser:mypassword@db:5432/mydatabase"

async def init_admin():
    """Create default admin account if it doesn't exist."""
    
    # Create async engine and session
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if admin already exists
        from sqlalchemy import select
        result = await session.execute(select(User).filter(User.username == "admin"))
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("✓ Admin account already exists")
            return
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@clarity.local",
            full_name="Administrator",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True
        )
        session.add(admin)
        await session.commit()
        print("✓ Admin account created: admin / admin123")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_admin())
