"""
Asset management configuration and utilities.
Handles file storage, validation, and metadata extraction.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 104857600))  # 100MB default
ALLOWED_MIME_TYPES = {
    # Images
    "image/jpeg": {"ext": ".jpg", "category": "image"},
    "image/png": {"ext": ".png", "category": "image"},
    "image/gif": {"ext": ".gif", "category": "image"},
    "image/webp": {"ext": ".webp", "category": "image"},
    "image/svg+xml": {"ext": ".svg", "category": "image"},
    
    # Documents
    "application/pdf": {"ext": ".pdf", "category": "document"},
    "application/msword": {"ext": ".doc", "category": "document"},
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {"ext": ".docx", "category": "document"},
    "text/plain": {"ext": ".txt", "category": "document"},
    "text/markdown": {"ext": ".md", "category": "document"},
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {"ext": ".xlsx", "category": "document"},
    
    # Videos
    "video/mp4": {"ext": ".mp4", "category": "video"},
    "video/webm": {"ext": ".webm", "category": "video"},
    "video/quicktime": {"ext": ".mov", "category": "video"},
    
    # Audio
    "audio/mpeg": {"ext": ".mp3", "category": "audio"},
    "audio/wav": {"ext": ".wav", "category": "audio"},
    "audio/webm": {"ext": ".webm", "category": "audio"},
}

# Ensure upload directory exists
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


class AssetManager:
    """Manages file uploads, storage, and retrieval."""
    
    @staticmethod
    def validate_file(file: UploadFile) -> Tuple[bool, Optional[str]]:
        """
        Validate file type and size.
        Returns: (is_valid, error_message)
        """
        if not file.content_type or file.content_type not in ALLOWED_MIME_TYPES:
            return False, f"File type '{file.content_type}' is not allowed"
        
        if file.size and file.size > MAX_FILE_SIZE:
            return False, f"File exceeds maximum size of {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
        
        return True, None
    
    @staticmethod
    def get_file_category(mime_type: str) -> str:
        """Get the category of a file based on MIME type."""
        return ALLOWED_MIME_TYPES.get(mime_type, {}).get("category", "other")
    
    @staticmethod
    async def save_file(file: UploadFile, original_filename: str) -> Tuple[str, str, int, str]:
        """
        Save uploaded file to disk and return file metadata.
        
        Returns: (filename, file_path, file_size, mime_type)
        """
        # Validate file
        is_valid, error_msg = AssetManager.validate_file(file)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        file_ext = Path(original_filename).suffix or ALLOWED_MIME_TYPES.get(file.content_type, {}).get("ext", "")
        filename = f"{timestamp}_{unique_id}{file_ext}"
        
        # Create directory structure by date
        date_dir = datetime.utcnow().strftime("%Y/%m/%d")
        file_dir = Path(UPLOAD_DIR) / date_dir
        file_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = file_dir / filename
        
        # Save file
        try:
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
            
            file_size = len(contents)
            logger.info(f"File saved: {file_path} ({file_size} bytes)")
            
            return filename, str(file_path), file_size, file.content_type
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete a file from disk."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    @staticmethod
    def get_file_path(file_path: str) -> Optional[Path]:
        """Get the absolute path to a file, validating it exists."""
        path = Path(file_path)
        if path.exists() and path.is_file():
            return path
        return None
    
    @staticmethod
    def cleanup_orphaned_files(referenced_files: set[str]) -> int:
        """
        Find and remove files that aren't referenced in the database.
        Use with caution!
        
        Returns: Number of files deleted
        """
        deleted_count = 0
        upload_path = Path(UPLOAD_DIR)
        
        if not upload_path.exists():
            return 0
        
        # Get all files in upload directory
        all_files = set()
        for file_path in upload_path.rglob("*"):
            if file_path.is_file():
                all_files.add(str(file_path))
        
        # Find orphaned files
        orphaned = all_files - referenced_files
        for orphaned_path in orphaned:
            if AssetManager.delete_file(orphaned_path):
                deleted_count += 1
        
        return deleted_count
