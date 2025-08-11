# Clarity Docs

A FastAPI-based service for managing and rendering documents, with SQLAlchemy for database operations, Alembic for migrations, and Docker for deployment.

---

## Features

- **FastAPI** framework for high-performance APIs.
- **SQLAlchemy** ORM for database interaction.
- **Alembic** for database migrations.
- **Pydantic** for request/response data validation.
- **Docker** and **docker-compose** for containerized deployment.
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

routes/
├── document_routes.py     # API routes for document handling

alembic/
├── env.py                 # Alembic migration configuration

docker-compose.yml         # Docker Compose file for multi-container setup
Dockerfile                 # Dockerfile for containerizing the app
wait-for-it.sh             # Script to wait for DB readiness before starting app
.env                       # Environment variables configuration file
```

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```
### 2. Environment Variables

Copy .env.example (if present) to .env and configure it, for example:
DATABASE_URL=postgresql://user:password@db:5432/dbname

### 3. Start with Docker
docker-compose up --build
This will:
Build the FastAPI app container.
Start the database container.
Run Alembic migrations.
Launch the API service.
### 4. Access the API
Once running, the app will be available at:
http://localhost:8000
Swagger UI documentation is available at:
http://localhost:8000/docs

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