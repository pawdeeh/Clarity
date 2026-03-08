# Clarity Docs

A FastAPI-based service for managing and rendering documents, with SQLAlchemy for database operations, Alembic for migrations, and Docker for deployment.

---

## Features

- **FastAPI** framework for high-performance APIs.
- **SQLAlchemy** ORM for database interaction.
- **Alembic** for database migrations.
- **Pydantic** for request/response data validation.
- **Docker** and **docker-compose** for containerized deployment.
- **Vue 3** modern frontend with TypeScript.
- **File Upload & Asset Management** - Complete file handling system.
- Modular project structure for maintainability.

---

## Project Structure

```plaintext
app/
├── __init__.py            # Makes the directory a package
├── main.py                # Entry point for the FastAPI app
├── models.py              # SQLAlchemy models
├── database.py            # Database setup and session management
├── crud.py                # CRUD operations
├── schemas.py             # Pydantic schemas
├── render.py              # Logic for rendering documents
├── assets_config.py       # File upload and asset management utilities

routes/
├── document_routes.py     # API routes for document handling
├── api_auth.py            # Authentication routes
└── asset_routes.py        # File upload and asset management routes

frontend/
├── src/                   # Vue 3 source code
│   ├── pages/            # Page components
│   ├── stores/           # Pinia state management
│   ├── api/              # API client
│   ├── App.vue           # Root component
│   ├── main.ts           # Entry point
│   └── router.ts         # Vue Router configuration
├── package.json          # Frontend dependencies
├── vite.config.ts        # Vite build configuration
└── index.html            # HTML template

alembic/
├── env.py                 # Alembic migration configuration
└── versions/              # Migration files

docker-compose.yml         # Docker Compose for multi-container setup
Dockerfile                 # Dockerfile for containerizing the app
wait-for-it.sh             # Script to wait for DB readiness before starting app
.env                       # Environment variables configuration file
```

**See Also:**
- [frontend/README.md](frontend/README.md) - Frontend documentation
- [ASSET_MANAGEMENT.md](ASSET_MANAGEMENT.md) - File upload & asset system

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/PaddeePadoo/Clarity.git
cd Clarity
```

### 2. Environment Variables

Copy .env.example (if present) to .env and configure it:

```bash
DATABASE_URL=postgresql://user:password@db:5432/dbname
UPLOAD_DIR=uploads
MAX_FILE_SIZE=104857600
```

### 3. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start the API
python -m uvicorn app.main:app --reload
```

API available at: http://localhost:8000

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: http://localhost:5173

### 5. Using Docker (All-in-One)

```bash
docker-compose up --build
```

This will:
- Build the FastAPI app container
- Start the database container
- Run Alembic migrations
- Launch the API service
- Both services will be available

### Accessing the Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Migrations
Generate a new migration:
alembic revision --autogenerate -m "description"
Apply migrations:
alembic upgrade head

## Development
Run the app locally without Docker:
uvicorn app.main:app --reload

## License

MIT License