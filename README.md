# Backend Setup and Running Instructions

## Prerequisites

1. **Python 3.11+** installed
2. **PostgreSQL** installed and running
3. **Virtual environment** activated

## Setup Steps

### 1. Activate Virtual Environment

**Windows:**
```bash
.\env\Scripts\activate
```

**Linux/Mac:**
```bash
source env/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Database

1. Create a PostgreSQL database:
```sql
CREATE DATABASE student_productivity;
```

2. Update `.env` file with your database credentials:
```env
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/student_productivity
```

### 4. Run Database Migrations

```bash
# Create initial migration (if needed)
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## Starting the Server

### Option 1: Using uvicorn directly (Recommended)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Using the start script

```bash
python start.py
```

### Option 3: Using uvicorn with more options

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --log-level info
```

## Server Endpoints

Once started, the server will be available at:
- **API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Environment Variables

Make sure your `.env` file contains:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key (change in production!)
- `CORS_ORIGINS` - Allowed frontend origins
- Other optional settings

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Verify database exists

### Port Already in Use
- Change port: `uvicorn app.main:app --reload --port 8001`
- Or kill the process using port 8000

### Module Not Found
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

