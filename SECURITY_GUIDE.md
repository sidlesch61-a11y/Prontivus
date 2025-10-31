# CliniCore Security Guide

## Overview

This document outlines the comprehensive security measures implemented in the CliniCore healthcare management system. The system follows industry best practices for healthcare data protection, including HIPAA compliance and GDPR requirements.

## Security Architecture

### 1. Authentication & Authorization

#### JWT Token Security
- **Access Tokens**: 30-minute expiry with secure refresh mechanism
- **Refresh Tokens**: 7-day expiry with rotation
- **Token Storage**: Secure httpOnly cookies in production
- **Algorithm**: HS256 with strong secret keys

#### Password Security
- **Hashing**: bcrypt with salt rounds
- **Strength Requirements**:
  - Minimum 8 characters
  - Must contain uppercase, lowercase, digits, and special characters
  - Blocks common weak passwords
- **Rate Limiting**: 5 attempts per 15 minutes, then 15-minute lockout

#### Role-Based Access Control (RBAC)
- **Admin**: Full system access
- **Secretary**: Patient management, appointments, basic financial
- **Doctor**: Clinical data, appointments, patient records
- **Patient**: Own data only

### 2. Data Protection

#### Input Validation & Sanitization
- **CPF Validation**: Brazilian CPF format with checksum verification
- **Phone Validation**: International format with libphonenumbers
- **Email Validation**: RFC-compliant with length limits
- **XSS Prevention**: HTML sanitization and CSP headers
- **SQL Injection Prevention**: SQLAlchemy ORM only

#### Data Encryption
- **At Rest**: Database encryption for sensitive fields
- **In Transit**: HTTPS/TLS 1.3
- **Sensitive Fields**: CPF, phone, email, medical notes

### 3. API Security

#### Rate Limiting
- **General API**: 100 requests/minute per IP
- **Login Endpoints**: 5 attempts/15 minutes
- **Data Export**: 10 requests/hour per user

#### Security Headers
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
Referrer-Policy: strict-origin-when-cross-origin
```

#### CORS Configuration
- **Allowed Origins**: Configured frontend domains only
- **Methods**: GET, POST, PUT, DELETE, PATCH, OPTIONS
- **Credentials**: Enabled for authenticated requests

### 4. Logging & Monitoring

#### Security Event Logging
- **Login Attempts**: Success/failure with IP and user agent
- **Data Exports**: User, type, record count, filters
- **Patient Data Changes**: Field-level audit trail
- **Admin Actions**: All administrative operations
- **API Access**: Request/response logging with timing

#### Log Format
```json
{
  "event_type": "login_attempt",
  "timestamp": "2024-01-15T10:30:00Z",
  "username": "user@example.com",
  "ip_address": "192.168.1.100",
  "success": false,
  "failure_reason": "Invalid credentials",
  "severity": "WARNING"
}
```

### 5. File Upload Security

#### Validation
- **File Types**: Whitelist of allowed extensions
- **MIME Types**: Server-side validation
- **File Size**: 10MB maximum
- **Malware Scanning**: Implemented for uploaded files

#### Allowed Types
- Images: JPG, PNG, GIF
- Documents: PDF, DOC, DOCX, TXT
- Spreadsheets: XLSX, CSV

### 6. Database Security

#### Connection Security
- **Encryption**: TLS for database connections
- **Connection Pooling**: Secure pool configuration
- **Query Logging**: Audit trail for sensitive operations

#### Data Isolation
- **Multi-tenancy**: Clinic-based data isolation
- **Row-Level Security**: Users can only access their clinic's data
- **Backup Encryption**: Encrypted backups with rotation

## Compliance

### HIPAA Compliance
- **Administrative Safeguards**: Access controls, audit logs
- **Physical Safeguards**: Secure hosting, data center security
- **Technical Safeguards**: Encryption, access controls, audit logs

### GDPR Compliance
- **Right to be Forgotten**: Data deletion capabilities
- **Data Portability**: Export user data
- **Consent Management**: User consent tracking
- **Data Retention**: 7-year retention policy

## Security Testing

### Automated Tests
- **Input Validation**: Comprehensive test suite
- **Authentication**: Token validation and expiry
- **Authorization**: Role-based access testing
- **SQL Injection**: Prevention verification
- **XSS Prevention**: Script injection testing

### Manual Testing
- **Penetration Testing**: Regular security assessments
- **Code Review**: Security-focused code reviews
- **Vulnerability Scanning**: Automated vulnerability detection

## Incident Response

### Security Incident Types
1. **Unauthorized Access**: Failed login attempts, privilege escalation
2. **Data Breach**: Unauthorized data access or export
3. **Malware**: Infected file uploads
4. **DDoS**: Service availability attacks

### Response Procedures
1. **Detection**: Automated monitoring and alerting
2. **Assessment**: Impact and scope evaluation
3. **Containment**: Immediate threat mitigation
4. **Investigation**: Root cause analysis
5. **Recovery**: System restoration
6. **Lessons Learned**: Process improvement

## Security Best Practices

### For Developers
1. **Input Validation**: Always validate and sanitize user input
2. **Authentication**: Use strong authentication mechanisms
3. **Authorization**: Implement proper access controls
4. **Logging**: Log all security-relevant events
5. **Error Handling**: Don't expose sensitive information in errors

### For Administrators
1. **Regular Updates**: Keep system and dependencies updated
2. **Access Review**: Regular access control reviews
3. **Monitoring**: Monitor security logs and alerts
4. **Backup Security**: Secure backup storage and testing
5. **Incident Response**: Maintain incident response procedures

### For Users
1. **Strong Passwords**: Use complex, unique passwords
2. **Session Management**: Log out when finished
3. **Suspicious Activity**: Report unusual system behavior
4. **Data Handling**: Follow data handling policies

## Security Configuration

### Environment Variables
```bash
# Security Settings
SECRET_KEY=your-very-secure-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY=your-encryption-key

# Database Security
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db?sslmode=require

# CORS Settings
CORS_ORIGINS=["https://clinicore.com"]
```

### Production Security Checklist
- [ ] HTTPS enabled and enforced
- [ ] Strong secret keys in use
- [ ] Database encryption enabled
- [ ] Security headers configured
- [ ] Rate limiting active
- [ ] Logging and monitoring enabled
- [ ] Backup encryption configured
- [ ] Incident response plan in place

## Contact

For security concerns or questions:
- **Security Team**: security@clinicore.com
- **Incident Response**: security-incident@clinicore.com
- **Bug Reports**: security-bugs@clinicore.com

## Version History

- **v1.0**: Initial security implementation
- **v1.1**: Enhanced input validation and logging
- **v1.2**: Added comprehensive test suite
- **v1.3**: Implemented security middleware and monitoring
