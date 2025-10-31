# CliniCore Authentication & Authorization Guide

## ✅ Implementation Complete!

A complete JWT-based authentication and Role-Based Access Control (RBAC) system has been implemented.

---

## 📦 What Was Created

### Backend (`/backend`)

#### 1. **Core Authentication Module** (`app/core/auth.py`)
- ✅ Password hashing with bcrypt
- ✅ JWT token creation and verification
- ✅ User authentication functions
- ✅ Dependency for `get_current_user`
- ✅ `RoleChecker` class for RBAC
- ✅ Convenience functions for role checking

#### 2. **Pydantic Schemas** (`app/schemas/auth.py`)
- ✅ `LoginRequest` - Login credentials
- ✅ `LoginResponse` - Token + user data
- ✅ `RegisterRequest` - User registration
- ✅ `UserResponse` - User information
- ✅ `TokenResponse` - JWT tokens
- ✅ `MessageResponse` - Generic messages

#### 3. **Authentication Endpoints** (`app/api/endpoints/auth.py`)
- ✅ `POST /api/auth/login` - User login
- ✅ `POST /api/auth/register` - User registration
- ✅ `GET /api/auth/me` - Get current user
- ✅ `POST /api/auth/refresh` - Refresh token
- ✅ `POST /api/auth/logout` - Logout user
- ✅ `GET /api/auth/verify-token` - Verify token validity

#### 4. **Database Seed Script** (`seed_data.py`)
- ✅ Creates sample clinic
- ✅ Creates test users for all roles

### Frontend (`/frontend`)

#### 1. **Authentication Utility** (`src/lib/auth.ts`)
- ✅ Token storage management (localStorage)
- ✅ `login()` - Login function
- ✅ `logout()` - Logout function
- ✅ `getCurrentUser()` - Fetch user data
- ✅ `verifyToken()` - Token validation
- ✅ Role checking helpers (isAdmin, isDoctor, etc.)

#### 2. **Auth Context** (`src/contexts/AuthContext.tsx`)
- ✅ Global authentication state
- ✅ `AuthProvider` component
- ✅ `useAuth()` hook
- ✅ `useRequireAuth()` hook
- ✅ `useRequireRole()` hook

#### 3. **Pages Created**
- ✅ `login/page.tsx` - Login page
- ✅ `unauthorized/page.tsx` - Access denied page
- ✅ `(dashboard)/layout.tsx` - Protected dashboard layout
- ✅ `(dashboard)/page.tsx` - Dashboard home

---

## 🔐 Security Features

### Password Security
- ✅ Bcrypt hashing with automatic salt generation
- ✅ Passwords never stored in plain text
- ✅ Secure password verification

### JWT Tokens
- ✅ Access tokens (30 minutes expiration)
- ✅ Refresh tokens (7 days expiration)
- ✅ Signed with SECRET_KEY
- ✅ Include user_id, role, and clinic_id

### Role-Based Access Control (RBAC)
- ✅ 4 Roles: ADMIN, SECRETARY, DOCTOR, PATIENT
- ✅ Easy role checking with decorators/dependencies
- ✅ Fine-grained permission control

---

## 🚀 Usage Examples

### Backend - Protecting Endpoints

#### Require Authentication
```python
from app.core.auth import get_current_user
from app.models import User

@app.get("/api/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}!"}
```

#### Require Specific Role
```python
from app.core.auth import require_admin

@app.post("/api/admin-only")
async def admin_only_route(current_user: User = Depends(require_admin())):
    return {"message": "Admin access granted"}
```

#### Require Multiple Roles
```python
from app.core.auth import RoleChecker, UserRole

@app.get("/api/staff-only")
async def staff_route(
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.SECRETARY, UserRole.DOCTOR])
    )
):
    return {"message": "Staff access granted"}
```

#### Optional Authentication
```python
from app.core.auth import get_current_user_optional

@app.get("/api/public-or-private")
async def flexible_route(current_user: User | None = Depends(get_current_user_optional)):
    if current_user:
        return {"message": f"Welcome back, {current_user.username}!"}
    return {"message": "Welcome, guest!"}
```

### Frontend - Using Authentication

#### Login Page
```typescript
import { useAuth } from '@/contexts';

function LoginPage() {
  const { login } = useAuth();
  
  const handleLogin = async () => {
    await login({
      username_or_email: 'admin@clinic.com',
      password: 'admin123'
    });
  };
}
```

#### Protected Page
```typescript
import { useRequireAuth } from '@/contexts';

function DashboardPage() {
  const { user, isLoading } = useRequireAuth();
  // User will be redirected to login if not authenticated
  
  return <div>Welcome, {user?.username}</div>;
}
```

#### Role-Based UI
```typescript
import { useAuth } from '@/contexts';
import { isAdmin, isDoctor } from '@/lib/auth';

function AdminPanel() {
  const { user } = useAuth();
  
  if (!isAdmin(user)) {
    return <p>Access denied</p>;
  }
  
  return <div>Admin Panel</div>;
}
```

#### Making Authenticated API Calls
```typescript
import { getAccessToken } from '@/lib/auth';

async function fetchProtectedData() {
  const token = getAccessToken();
  
  const response = await fetch('http://localhost:8000/api/protected', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.json();
}
```

---

## 🧪 Testing the Authentication

### 1. Seed Test Data
```bash
cd backend
.\venv\Scripts\Activate.ps1
python seed_data.py
```

### 2. Test Credentials

| Role | Email | Password | Access Level |
|------|-------|----------|--------------|
| Admin | admin@clinic.com | admin123 | Full access |
| Secretary | secretary@clinic.com | secretary123 | Staff access |
| Doctor | dr.smith@clinic.com | doctor123 | Medical access |
| Patient | patient@example.com | patient123 | Limited access |

### 3. API Testing

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email":"admin@clinic.com","password":"admin123"}'
```

**Get Current User:**
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. Frontend Testing
1. Start backend: `cd backend; .\venv\Scripts\Activate.ps1; uvicorn main:app --reload`
2. Start frontend: `cd frontend; npm run dev`
3. Visit http://localhost:3000/login
4. Login with test credentials
5. You'll be redirected to the dashboard

---

## 📝 API Endpoints Reference

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login` | User login | No |
| POST | `/api/auth/register` | Register new user | No |
| GET | `/api/auth/me` | Get current user info | Yes |
| POST | `/api/auth/refresh` | Refresh access token | Yes |
| POST | `/api/auth/logout` | Logout user | Yes |
| GET | `/api/auth/verify-token` | Verify token validity | Yes |

### Request/Response Examples

**Login Request:**
```json
{
  "username_or_email": "admin@clinic.com",
  "password": "admin123"
}
```

**Login Response:**
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@clinic.com",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin",
    "is_active": true,
    "is_verified": true,
    "clinic_id": 1
  }
}
```

---

## 🔧 Configuration

### Environment Variables (`.env`)
```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**⚠️ Important:** Change `SECRET_KEY` in production!

Generate secure key:
```bash
openssl rand -hex 32
# or
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🛡️ Security Best Practices

### Implemented ✅
- Password hashing with bcrypt
- JWT tokens with expiration
- HTTPOnly cookies recommended for production
- CORS configured
- Role-based access control
- Token verification on each request

### Recommended for Production 🚀
- [ ] Implement token blacklisting for logout
- [ ] Add rate limiting for login attempts
- [ ] Implement 2FA/MFA
- [ ] Use HTTPS only
- [ ] Store tokens in HTTP-only cookies (not localStorage)
- [ ] Add CSRF protection
- [ ] Implement password reset flow
- [ ] Add email verification
- [ ] Log authentication events
- [ ] Implement account lockout after failed attempts

---

## 📚 Additional Resources

### Files Created
- Backend:
  - `app/core/auth.py` - Auth functions
  - `app/schemas/auth.py` - Pydantic schemas
  - `app/api/endpoints/auth.py` - API endpoints
  - `seed_data.py` - Test data script

- Frontend:
  - `src/lib/auth.ts` - Auth utilities
  - `src/contexts/AuthContext.tsx` - Auth context
  - `src/app/login/page.tsx` - Login page
  - `src/app/unauthorized/page.tsx` - Access denied page
  - `src/app/(dashboard)/layout.tsx` - Protected layout

### Documentation
- `backend/AUTHENTICATION_GUIDE.md` - This file
- `backend/MODELS_SUMMARY.md` - Database models
- `backend/SETUP_DATABASE.md` - Database setup

---

## ✅ Ready for Development!

The authentication system is fully implemented and ready to use. You can now:

1. 🔐 **Protect any endpoint** with role-based access control
2. 🎨 **Build authenticated UI** using the AuthContext
3. 👥 **Manage users** with different permission levels
4. 🚀 **Extend the system** with additional features

**Happy Coding!** 🎉

