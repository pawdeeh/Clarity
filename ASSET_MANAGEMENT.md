# File Upload & Asset Management

## Overview

The File Upload & Asset Management system provides a robust, production-ready solution for uploading, storing, and managing files within Clarity. It includes file validation, organiszed storage, metadata tracking, and integration with documents.

## Features

### ✓ File Upload
- **Single file upload**: Upload one file at a time
- **Bulk upload**: Upload multiple files simultaneously
- **File validation**: Automatic validation of file type and size
- **MIME type support**: Comprehensive support for common file types
- **Unique naming**: Files are automatically renamed with timestamps and UUIDs to prevent conflicts

### ✓ File Storage
- **Organized structure**: Files stored in date-based directory structure (YYYY/MM/DD)
- **Configurable limits**: Max file size is configurable via environment variables
- **Disk management**: Utilities for cleanup and storage monitoring

### ✓ Asset Management
- **Metadata tracking**: Original filename, file type, size, MIME type, upload time
- **Permission control**: Users can only delete their own assets (admins can delete any)
- **Organization**: Assets can be organized by collection
- **Filtering**: Search and filter by file type, uploader, or collection

### ✓ Document Integration
- **Link/Unlink**: Associate assets with documents
- **Document-Asset tracking**: Many-to-many relationships tracked in database
- **Asset retrieval**: Get all assets linked to a specific document

### ✓ Asset Statistics
- **Storage metrics**: Total storage used in bytes and MB
- **Type breakdown**: Count of assets by file type
- **Usage reporting**: Aggregate statistics for monitoring

## Configuration

### Environment Variables

```bash
# Location for file uploads (default: uploads)
UPLOAD_DIR=uploads

# Maximum file size in bytes (default: 104857600 = 100MB)
MAX_FILE_SIZE=104857600
```

### Supported File Types

The system supports the following file types out of the box:

**Images**
- JPEG (.jpg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)
- SVG (.svg)

**Documents**
- PDF (.pdf)
- Word (.doc, .docx)
- Plain Text (.txt)
- Markdown (.md)
- Excel (.xlsx)

**Videos**
- MP4 (.mp4)
- WebM (.webm)
- QuickTime (.mov)

**Audio**
- MP3 (.mp3)
- WAV (.wav)
- WebM Audio (.webm)

To add more file types, edit `ALLOWED_MIME_TYPES` in `app/assets_config.py`.

## API Endpoints

### Upload Endpoints

#### Upload Single File
**POST** `/api/assets/upload/`

Upload a single file and create an asset record.

**Authentication**: Required (Bearer token)

**Parameters**:
- `file`: File to upload (form data)
- `collection_id`: Optional collection ID for organization

**Response** (200 OK):
```json
{
  "id": 1,
  "filename": "20260304_150530_a1b2c3d4.txt",
  "original_filename": "my_document.txt",
  "file_type": "document",
  "file_size": 1024,
  "mime_type": "text/plain",
  "uploaded_by": 1,
  "collection_id": null,
  "created_at": "2026-03-04T15:05:30",
  "updated_at": "2026-03-04T15:05:30"
}
```

**Example (curl)**:
```bash
curl -X POST "http://localhost:8000/api/assets/upload/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/file.txt"
```

#### Upload Multiple Files
**POST** `/api/assets/upload-multiple/`

Upload multiple files at once.

**Authentication**: Required (Bearer token)

**Parameters**:
- `files`: Multiple files to upload (form data)
- `collection_id`: Optional collection ID

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "filename": "20260304_150530_a1b2c3d4.txt",
    "original_filename": "file1.txt",
    ...
  },
  {
    "id": 2,
    "filename": "20260304_150542_b2c3d4e5.txt",
    "original_filename": "file2.txt",
    ...
  }
]
```

**Example (curl)**:
```bash
curl -X POST "http://localhost:8000/api/assets/upload-multiple/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@file1.txt" \
  -F "files=@file2.txt" \
  -F "files=@file3.txt"
```

### Retrieval Endpoints

#### Get Asset Details
**GET** `/api/assets/{asset_id}`

Get details about a specific asset.

**Authentication**: Not required

**Response** (200 OK):
```json
{
  "id": 1,
  "filename": "20260304_150530_a1b2c3d4.txt",
  "original_filename": "my_document.txt",
  "file_type": "document",
  "file_size": 1024,
  "mime_type": "text/plain",
  "uploaded_by": 1,
  "collection_id": null,
  "created_at": "2026-03-04T15:05:30",
  "updated_at": "2026-03-04T15:05:30"
}
```

#### List Assets
**GET** `/api/assets/`

List all assets with optional filtering.

**Authentication**: Not required

**Query Parameters**:
- `skip`: Number of results to skip (default: 0)
- `limit`: Max results to return (default: 100, max: 1000)
- `collection_id`: Filter by collection
- `file_type`: Filter by type (image, video, document, audio, other)
- `uploaded_by`: Filter by uploader user ID

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "filename": "20260304_150530_a1b2c3d4.txt",
    "original_filename": "file1.txt",
    ...
  },
  {
    "id": 2,
    "filename": "20260304_150542_b2c3d4e5.txt",
    "original_filename": "file2.txt",
    ...
  }
]
```

**Example**:
```bash
# List all assets
curl "http://localhost:8000/api/assets/"

# Filter by type
curl "http://localhost:8000/api/assets/?file_type=image"

# Filter by uploader
curl "http://localhost:8000/api/assets/?uploaded_by=1&limit=50"

# Filter by collection
curl "http://localhost:8000/api/assets/?collection_id=2&skip=10&limit=20"
```

#### Download Asset
**GET** `/api/assets/{asset_id}/download`

Download the actual file.

**Authentication**: Not required

**Response** (200 OK):
- Raw file content
- `Content-Type` header set to file's MIME type
- `Content-Disposition` header with original filename

**Example**:
```bash
curl -O "http://localhost:8000/api/assets/1/download"
```

### Document Association Endpoints

#### Link Asset to Document
**POST** `/api/assets/{asset_id}/link-to-document/{document_id}`

Link an asset to a document.

**Authentication**: Required (Bearer token)

**Authorization**: Must be document owner or admin

**Response** (200 OK):
```json
{
  "message": "Asset linked successfully",
  "association_id": 1
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/assets/1/link-to-document/5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Unlink Asset from Document
**DELETE** `/api/assets/{asset_id}/unlink-from-document/{document_id}`

Remove the link between an asset and document.

**Authentication**: Required (Bearer token)

**Authorization**: Must be document owner or admin

**Response** (200 OK):
```json
{
  "message": "Asset unlinked successfully"
}
```

### Management Endpoints

#### Delete Asset
**DELETE** `/api/assets/{asset_id}`

Delete an asset and remove the file from disk.

**Authentication**: Required (Bearer token)

**Authorization**: Must be asset uploader or admin

**Response** (200 OK):
```json
{
  "message": "Asset deleted successfully",
  "id": 1
}
```

#### Get Asset Statistics
**GET** `/api/assets/stats/`

Get aggregate statistics about assets.

**Authentication**: Not required

**Response** (200 OK):
```json
{
  "total_assets": 15,
  "total_storage_bytes": 52428800,
  "total_storage_mb": 50.00,
  "assets_by_type": {
    "image": 8,
    "document": 5,
    "video": 2
  }
}
```

## Database Schema

### Assets Table

```sql
CREATE TABLE assets (
    id INTEGER PRIMARY KEY,
    filename VARCHAR NOT NULL,
    original_filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_type VARCHAR NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR NOT NULL,
    uploaded_by INTEGER NOT NULL REFERENCES users(id),
    collection_id INTEGER REFERENCES document_collections(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_assets_id ON assets(id);
CREATE INDEX ix_assets_filename ON assets(filename);
```

### Document-Asset Association Table

```sql
CREATE TABLE document_asset_association (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id),
    asset_id INTEGER NOT NULL REFERENCES assets(id)
);
```

## File Storage Structure

Files are organized in a date-based directory hierarchy:

```
uploads/
├── 2026/
│   ├── 03/
│   │   ├── 04/
│   │   │   ├── 20260304_150530_a1b2c3d4.txt
│   │   │   ├── 20260304_150542_b2c3d4e5.jpg
│   │   │   └── 20260304_151200_c3d4e5f6.pdf
│   │   └── 05/
│   │       └── 20260305_100000_d4e5f6g7.png
│   └── ...
└── ...
```

Filename format: `YYYYMMDD_HHMMSS_UNIQUEID.ext`

## Permission & Authorization Model

- **Upload**: Requires authentication. Any logged-in user can upload.
- **List**: No authentication required. Anyone can view asset metadata.
- **Download**: No authentication required. Anyone can download files.
- **Delete**: Only the uploader or admin can delete an asset.
- **Link to Document**: Only document owner or admin can link assets.
- **Unlink from Document**: Only document owner or admin can unlink assets.

## Error Handling

### Common Error Responses

**400 Bad Request** - Invalid file type or size exceeds limit
```json
{
  "detail": "File type 'application/x-msdownload' is not allowed"
}
```

**404 Not Found** - Asset or file doesn't exist
```json
{
  "detail": "Asset not found"
}
```

**403 Forbidden** - Insufficient permissions
```json
{
  "detail": "You can only delete your own assets"
}
```

**500 Internal Server Error** - Server-side error during upload or deletion
```json
{
  "detail": "Error uploading file"
}
```

## Best Practices

1. **File Type Validation**: Always validate on the client side before uploading.
2. **Size Limits**: Inform users of size limits upfront (default 100MB).
3. **Bulk Operations**: Use bulk upload when uploading multiple files to improve performance.
4. **Cleanup**: Regularly run cleanup to remove orphaned files (use `AssetManager.cleanup_orphaned_files()`).
5. **Backup**: Regularly backup the `uploads/` directory.
6. **Monitoring**: Use the stats endpoint to monitor storage usage.

## Example: Complete Workflow

```bash
#!/bin/bash

# 1. Get auth token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}' | jq -r '.access_token')

# 2. Upload a file
ASSET=$(curl -s -X POST "http://localhost:8000/api/assets/upload/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@README.md")

ASSET_ID=$(echo $ASSET | jq '.id')

# 3. Create a document
DOCUMENT=$(curl -s -X POST "http://localhost:8000/api/documents/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Doc","content":"Content","slug":"my-doc"}')

DOC_ID=$(echo $DOCUMENT | jq '.id')

# 4. Link asset to document
curl -s -X POST "http://localhost:8000/api/assets/$ASSET_ID/link-to-document/$DOC_ID" \
  -H "Authorization: Bearer $TOKEN"

# 5. Download the file
curl -O "http://localhost:8000/api/assets/$ASSET_ID/download"

# 6. Check stats
curl -s "http://localhost:8000/api/assets/stats/" | jq
```

## Troubleshooting

### Files not persisting after restart
- Check `UPLOAD_DIR` environment variable points to persistent storage
- In Docker, ensure the upload directory is mounted as a volume

### Permission denied when uploading
- Check file system permissions on upload directory
- Ensure the app user has write permissions

### File not found when downloading
- Verify file exists in `UPLOAD_DIR`
- Check file_path in database matches actual file location
- Consider running cleanup if this happens frequently

## Future Enhancements

- [ ] Virus scanning on upload
- [ ] Image thumbnail generation
- [ ] Cloud storage backend (S3, Azure Blob, etc.)
- [ ] File versioning
- [ ] Direct document embedding from assets
- [ ] Asset tagging system
- [ ] Bandwidth usage tracking
