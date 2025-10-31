# CliniCore Setup Guide

This guide will help you set up the CliniCore Healthcare Management System from scratch.

## Prerequisites

Before you begin, ensure you have the following installed:

### Backend Requirements
- Python 3.11 or higher
- PostgreSQL 14 or higher
- pip (Python package installer)

### Frontend Requirements
- Node.js 18 or higher
- npm or yarn package manager

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd CliniCore
```

### 2. Database Setup

#### Create PostgreSQL Database

**Windows (PowerShell):**
```powershell
psql -U postgres
```

**Linux/Mac:**
```bash
sudo -u postgres psql
```

**In PostgreSQL prompt:**
```sql
CREATE DATABASE clinicore;
CREATE USER clinicore_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE clinicore TO clinicore_user;
\q
```

### 3. Backend Setup

#### Navigate to Backend Directory
```bash
cd backend
```

#### Create Virtual Environment
**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` file with your database credentials:
```
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/clinicore
SECRET_KEY=your-secret-key-here
```

**Generate a secure SECRET_KEY:**
```bash
# Using OpenSSL
openssl rand -hex 32

# Using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Run Database Migrations
```bash
alembic upgrade head
```

#### Start the Backend Server
```bash
# Option 1: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python
python main.py
```

The backend will be running at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. Frontend Setup

Open a **new terminal window** and navigate to the frontend directory:

```bash
cd frontend
```

#### Install Dependencies
```bash
npm install
```

#### Configure Environment Variables
```bash
# Windows
copy .env.local.example .env.local

# Linux/Mac
cp .env.local.example .env.local
```

The default configuration should work if the backend is running on port 8000.

#### Start the Development Server
```bash
npm run dev
```

The frontend will be running at: http://localhost:3000

### 5. Verify Installation

1. **Backend Health Check:**
   - Visit http://localhost:8000
   - You should see: `{"status": "healthy"}`
   - Visit http://localhost:8000/docs for API documentation

2. **Frontend:**
   - Visit http://localhost:3000
   - You should see the CliniCore dashboard with sidebar navigation

## Using NPM Scripts (Root Directory)

From the root directory, you can use these convenience scripts:

```bash
# Frontend
npm run frontend:dev       # Start frontend dev server
npm run frontend:build     # Build frontend for production
npm run frontend:start     # Start production server

# Backend
npm run backend:dev        # Start backend dev server
npm run backend:migrate    # Run database migrations
npm run backend:migration  # Create new migration

# Setup
npm run setup:frontend     # Install frontend dependencies
npm run setup:backend      # Install backend dependencies
```

## Common Issues and Solutions

### Issue: Database Connection Error

**Error:** `Could not connect to database`

**Solution:**
1. Verify PostgreSQL is running
2. Check DATABASE_URL in `.env` file
3. Ensure database and user exist
4. Test connection: `psql -U postgres -d clinicore`

### Issue: Port Already in Use

**Backend (Port 8000):**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**Frontend (Port 3000):**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

### Issue: Python Virtual Environment Not Activating

**Windows:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Module Not Found

**Backend:**
```bash
pip install -r requirements.txt --upgrade
```

**Frontend:**
```bash
rm -rf node_modules package-lock.json  # or del /s on Windows
npm install
```

## Next Steps

1. **Explore the API Documentation:**
   - Visit http://localhost:8000/docs
   - Try out the endpoints using the interactive interface

2. **Customize the Application:**
   - Add new models in `backend/models.py`
   - Create new API endpoints in `backend/main.py`
   - Build new frontend pages in `frontend/src/app/`

3. **Create Database Migrations:**
   ```bash
   cd backend
   alembic revision --autogenerate -m "description of changes"
   alembic upgrade head
   ```

4. **Add UI Components:**
   ```bash
   cd frontend
   npx shadcn@latest add [component-name]
   ```

## Development Workflow

1. **Make Changes:**
   - Backend: Edit Python files (auto-reloads with `--reload`)
   - Frontend: Edit React/TypeScript files (auto-reloads in dev mode)

2. **Test Changes:**
   - Backend: Use http://localhost:8000/docs
   - Frontend: Check http://localhost:3000

3. **Create Migrations:**
   - After model changes: `alembic revision --autogenerate`
   - Apply: `alembic upgrade head`

4. **Commit Changes:**
   ```bash
   git add .
   git commit -m "feat: description of changes"
   git push
   ```

## Production Deployment

For production deployment, refer to:
- `docs/deployment/` (coming soon)
- Consider using Docker for containerization
- Set up proper environment variables
- Use production database credentials
- Enable HTTPS/SSL
- Set DEBUG=False in production

## Support

If you encounter issues:
1. Check this guide thoroughly
2. Review the main README.md
3. Check the documentation in `/docs`
4. Open an issue on the repository

---

**Happy Coding! 🚀**

