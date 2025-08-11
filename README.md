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
