# Multi-Tenancy and Licensing System

This document describes the multi-tenancy and licensing system implemented in CliniCore.

## Overview

The licensing system provides:
- **Multi-tenancy**: Each clinic operates in isolation
- **License management**: Control access to features based on license
- **User limits**: Enforce maximum user counts per clinic
- **Module access**: Enable/disable specific features per clinic
- **Admin panel**: Manage clinic licenses and access

## Database Schema

### Clinic Model Updates

The `Clinic` model has been extended with licensing fields:

```python
class Clinic(BaseModel):
    # ... existing fields ...
    
    # Licensing Information
    license_key: str = Column(String(100), unique=True, nullable=True, index=True)
    expiration_date: Date = Column(Date, nullable=True)
    max_users: int = Column(Integer, default=10, nullable=False)
    active_modules: List[str] = Column(JSON, nullable=True, default=list)
```

## Available Modules

The system supports the following modules:

- `bi` - Business Intelligence (Analytics and reporting)
- `telemed` - Telemedicine (Remote consultations)
- `stock` - Stock Management (Inventory management)
- `financial` - Financial Management (Billing and invoicing)
- `clinical` - Clinical Records (Patient medical records)
- `appointments` - Appointment Management (Scheduling system)
- `patients` - Patient Management (Patient registration)
- `procedures` - Procedure Management (Medical procedures)
- `tiss` - TISS Integration (Health insurance integration)
- `mobile` - Mobile App Access (Mobile application access)

## Module Dependencies

Some modules require other modules to function:

```python
MODULE_DEPENDENCIES = {
    "bi": ["financial", "clinical", "appointments"],
    "telemed": ["appointments", "clinical"],
    "stock": ["financial"],
    "financial": ["appointments"],
    "clinical": ["appointments"],
    "procedures": ["financial", "stock"],
    "tiss": ["financial", "clinical"],
    "mobile": ["appointments", "clinical", "patients"],
}
```

## Backend Implementation

### Licensing Middleware

The `app/core/licensing.py` module provides:

- `validate_license(clinic)`: Check if clinic license is valid and not expired
- `check_user_limit(clinic_id, db)`: Verify clinic hasn't exceeded user limit
- `check_module_access(clinic, module)`: Check if clinic has access to a module
- `require_license`: FastAPI dependency for license validation
- `require_user_limit_check`: FastAPI dependency for user limit validation
- `require_module(module)`: FastAPI dependency for module access validation

### Admin Endpoints

The `app/api/endpoints/admin.py` provides:

- `GET /api/admin/clinics` - List all clinics with filtering
- `GET /api/admin/clinics/{id}` - Get specific clinic
- `POST /api/admin/clinics` - Create new clinic
- `PUT /api/admin/clinics/{id}` - Update clinic
- `PATCH /api/admin/clinics/{id}/license` - Update clinic license
- `DELETE /api/admin/clinics/{id}` - Deactivate clinic
- `GET /api/admin/clinics/stats` - Get clinic statistics
- `GET /api/admin/modules` - Get available modules

### Usage in Endpoints

To protect an endpoint with licensing:

```python
from app.core.licensing import require_license, require_module

@router.get("/protected-endpoint")
async def protected_endpoint(
    clinic: Clinic = Depends(require_license)
):
    # This endpoint requires a valid license
    pass

@router.get("/bi-dashboard")
async def bi_dashboard(
    clinic: Clinic = Depends(require_module("bi"))
):
    # This endpoint requires BI module access
    pass
```

## Frontend Implementation

### Admin Panel

The admin panel at `/admin/clinics` provides:

- **Clinic Management**: Create, edit, and deactivate clinics
- **License Management**: Set license keys, expiration dates, and user limits
- **Module Configuration**: Enable/disable modules for each clinic
- **Statistics Dashboard**: View clinic and license statistics
- **Search and Filtering**: Find clinics by name, status, or license status

### Conditional Menu Rendering

The sidebar automatically shows/hides menu items based on:

- **User Role**: Admin users see administration menu
- **Active Modules**: Only modules enabled for the clinic are shown
- **Module Dependencies**: Required modules are automatically included

### User Context

The user context now includes clinic information:

```typescript
interface User {
  // ... existing fields ...
  clinic?: {
    id: number;
    name: string;
    active_modules: string[];
    // ... other clinic fields
  };
}
```

## Security Considerations

1. **License Validation**: All protected endpoints validate clinic license
2. **User Limits**: System prevents exceeding licensed user count
3. **Module Access**: Features are hidden/disabled based on license
4. **Admin Access**: Only admin users can manage clinic licenses
5. **Data Isolation**: Each clinic's data is completely isolated

## Testing

Run the licensing test script:

```bash
cd backend
python test_licensing.py
```

This will test:
- License validation
- User limit checking
- Module access control
- Database connectivity

## Migration

The licensing fields were added via Alembic migration:

```bash
alembic upgrade head
```

The migration:
1. Adds new columns to the `clinics` table
2. Sets default values for existing clinics
3. Creates indexes for performance

## Configuration

### Environment Variables

No additional environment variables are required. The system uses the existing database configuration.

### Default Values

- `max_users`: 10 (for new clinics)
- `active_modules`: [] (empty list, no modules enabled by default)
- `license_key`: null (unlimited access)
- `expiration_date`: null (no expiration)

## Monitoring

The admin panel provides statistics for:

- Total clinics
- Active clinics
- Expired licenses
- Total users across all clinics
- Clinics with licenses expiring soon (30 days)

## Future Enhancements

1. **License Types**: Different license tiers (Basic, Professional, Enterprise)
2. **Usage Tracking**: Monitor feature usage per clinic
3. **Automatic Renewal**: Auto-renew licenses before expiration
4. **Billing Integration**: Connect with billing systems
5. **Audit Logs**: Track license changes and access attempts
6. **API Rate Limiting**: Limit API calls based on license tier
7. **Feature Flags**: More granular control over individual features
