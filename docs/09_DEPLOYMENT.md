# Deployment Guide

## Production Deployment

### Prerequisites
- Linux server (Ubuntu recommended)
- Python 3.8+
- PostgreSQL (recommended) or SQLite
- Nginx (reverse proxy)
- Gunicorn (WSGI server)

### Steps

1. **Server Setup**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx postgresql
   ```

2. **Application Setup**
   ```bash
   git clone <repository>
   cd zupco_simple
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt gunicorn
   ```

3. **Database Setup**
   - Configure PostgreSQL
   - Update settings.py
   - Run migrations

4. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

5. **Gunicorn**
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000
   ```

6. **Nginx Configuration**
   - Configure reverse proxy
   - Serve static files
   - SSL/TLS setup

### Security
- Set DEBUG = False
- Configure ALLOWED_HOSTS
- Use HTTPS
- Implement authentication
- Regular backups

---

**Document Version**: 1.0

