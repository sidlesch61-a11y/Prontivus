# CliniCore - Healthcare Management System

A comprehensive, modern healthcare management platform built with a monorepo architecture. CliniCore provides end-to-end solutions for managing patients, appointments, medical records, prescriptions, and healthcare operations.

## 🏗️ Architecture

This is a monorepo project with the following structure:

```
CliniCore/
├── backend/          # FastAPI backend API
├── frontend/         # Next.js 14 web application
├── mobile/           # Mobile application (future)
├── docs/             # Documentation
└── README.md         # This file
```

## 🚀 Quick Start

### Prerequisites

- **Backend:**
  - Python 3.11+
  - PostgreSQL 14+
  - pip

- **Frontend:**
  - Node.js 18+
  - npm or yarn

### Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd CliniCore
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials and secret key

# Create database
psql -U postgres
CREATE DATABASE clinicore;
\q

# Run migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload
```

Backend will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## 📦 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Async ORM for database operations
- **PostgreSQL** - Relational database
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **JWT** - Authentication

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS
- **shadcn/ui** - UI component library
- **Lucide React** - Icon library

## 🎯 Features

### Current Features
- ✅ Modern monorepo architecture
- ✅ FastAPI backend with async PostgreSQL support
- ✅ Next.js 14 frontend with App Router
- ✅ Beautiful UI with shadcn/ui components
- ✅ Responsive sidebar navigation
- ✅ Dashboard with key metrics
- ✅ Database migrations with Alembic
- ✅ Type-safe development with TypeScript

### Planned Features
- 🔄 Patient management
- 🔄 Appointment scheduling
- 🔄 Medical records system
- 🔄 Prescription management
- 🔄 Doctor profiles
- 🔄 User authentication & authorization
- 🔄 Role-based access control
- 🔄 Reporting and analytics
- 🔄 Mobile application
- 🔄 Real-time notifications

## 📚 Project Structure

### Backend Structure
```
backend/
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py            # Alembic config
├── main.py               # FastAPI application entry
├── database.py           # Database connection
├── models.py             # SQLAlchemy models
├── config.py             # Application settings
├── requirements.txt      # Python dependencies
└── .env.example          # Environment template
```

### Frontend Structure
```
frontend/
├── src/
│   ├── app/              # Next.js pages
│   │   ├── layout.tsx    # Root layout
│   │   ├── page.tsx      # Dashboard
│   │   └── globals.css   # Global styles
│   ├── components/       # React components
│   │   ├── ui/           # shadcn/ui components
│   │   └── app-sidebar.tsx  # Navigation
│   ├── hooks/            # Custom hooks
│   └── lib/              # Utilities
├── public/               # Static files
└── package.json          # Dependencies
```

## 🔧 Development

### Backend Development

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Run tests
pytest

# Code formatting
black .
flake8 .
```

### Frontend Development

```bash
cd frontend

# Start dev server
npm run dev

# Build for production
npm run build

# Run production build
npm start

# Lint code
npm run lint

# Add new UI component
npx shadcn@latest add [component-name]
```

## 🌐 API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /api/health` - Detailed health information

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/clinicore
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
DEBUG=True
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=CliniCore
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Team

Developed by the CliniCore team.

## 📞 Support

For support and questions, please open an issue in the repository.

---

**Note:** This project is under active development. Features and documentation are continuously being updated.

