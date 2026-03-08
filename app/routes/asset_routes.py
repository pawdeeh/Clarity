# app/routes/asset_routes.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.database import get_db
from app.models import User, Asset
from app.auth import get_current_user
from app.assets_config import AssetManager
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/assets", tags=["assets"])


# ====== ASSET UPLOAD ENDPOINTS ======
@router.post("/upload/", response_model=schemas.Asset)
async def upload_asset(
    file: UploadFile = File(...),
    collection_id: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a file and create an asset record.
    Requires authentication.
    
    Query Parameters:
    - collection_id: Optional collection to organize asset
    
    Returns: Created Asset object
    """
    try:
        # Validate and save file
        filename, file_path, file_size, mime_type = await AssetManager.save_file(
            file, 
            file.filename
        )
        
        # Get file category
        file_type = AssetManager.get_file_category(mime_type)
        
        # Create asset in database
        return await crud.create_asset(
            db,
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            mime_type=mime_type,
            uploaded_by=current_user.id,
            collection_id=collection_id
        )
    except ValueError as e:
        logger.warning(f"File validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="Error uploading file")


@router.post("/upload-multiple/", response_model=List[schemas.Asset])
async def upload_multiple_assets(
    files: List[UploadFile] = File(...),
    collection_id: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload multiple files at once.
    Requires authentication.
    
    Returns: List of created Asset objects
    """
    assets = []
    failed_files = []
    
    for file in files:
        try:
            # Validate and save file
            filename, file_path, file_size, mime_type = await AssetManager.save_file(
                file,
                file.filename
            )
            
            # Get file category
            file_type = AssetManager.get_file_category(mime_type)
            
            # Create asset in database
            asset = await crud.create_asset(
                db,
                filename=filename,
                original_filename=file.filename,
                file_path=file_path,
                file_type=file_type,
                file_size=file_size,
                mime_type=mime_type,
                uploaded_by=current_user.id,
                collection_id=collection_id
            )
            assets.append(asset)
        except Exception as e:
            logger.warning(f"Failed to upload {file.filename}: {e}")
            failed_files.append({"filename": file.filename, "error": str(e)})
    
    if not assets:
        raise HTTPException(status_code=400, detail=f"All files failed to upload: {failed_files}")
    
    return assets


# ====== ASSET RETRIEVAL ENDPOINTS ======
@router.get("/{asset_id}", response_model=schemas.Asset)
async def get_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    """Get an asset by ID"""
    db_asset = await crud.get_asset(db, asset_id)
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return db_asset


@router.get("/", response_model=List[schemas.Asset])
async def list_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    collection_id: int = Query(None),
    file_type: str = Query(None, description="Filter by file type: image, video, document, audio, other"),
    uploaded_by: int = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    List assets with optional filtering.
    
    Query Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Number of records to return
    - collection_id: Filter by collection
    - file_type: Filter by file type (image, video, document, audio, other)
    - uploaded_by: Filter by uploader user ID
    """
    if collection_id:
        return await crud.get_assets_by_collection(db, collection_id, skip, limit)
    
    if uploaded_by:
        return await crud.get_assets_by_uploader(db, uploaded_by, skip, limit)
    
    if file_type:
        return await crud.get_assets_by_type(db, file_type, skip, limit)
    
    return await crud.get_assets(db, skip, limit)


@router.get("/{asset_id}/download")
async def download_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    """Download an asset file"""
    db_asset = await crud.get_asset(db, asset_id)
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    file_path = AssetManager.get_file_path(db_asset.file_path)
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file_path,
        filename=db_asset.original_filename,
        media_type=db_asset.mime_type
    )


# ====== ASSET MANAGEMENT ENDPOINTS ======
@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an asset and remove the file.
    Only the uploader or admin can delete.
    """
    db_asset = await crud.get_asset(db, asset_id)
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Check authorization
    if db_asset.uploaded_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only delete your own assets")
    
    # Delete file from disk
    if db_asset.file_path:
        AssetManager.delete_file(db_asset.file_path)
    
    # Delete from database
    await crud.delete_asset(db, asset_id)
    
    return {"message": "Asset deleted successfully", "id": asset_id}


@router.get("/stats/")
async def get_asset_stats(db: AsyncSession = Depends(get_db)):
    """Get aggregate statistics about assets"""
    return await crud.get_asset_stats(db)


@router.post("/{asset_id}/link-to-document/{document_id}")
async def link_asset_to_document(
    asset_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Link an asset to a document"""
    db_asset = await crud.get_asset(db, asset_id)
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db_document = await crud.get_document(db, document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check authorization - only document owner or admin can link assets
    if db_document.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only link assets to your own documents")
    
    return await crud.link_asset_to_document(db, asset_id, document_id)


@router.delete("/{asset_id}/unlink-from-document/{document_id}")
async def unlink_asset_from_document(
    asset_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unlink an asset from a document"""
    db_document = await crud.get_document(db, document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check authorization
    if db_document.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only unlink assets from your own documents")
    
    await crud.unlink_asset_from_document(db, asset_id, document_id)
    
    return {"message": "Asset unlinked successfully"}
