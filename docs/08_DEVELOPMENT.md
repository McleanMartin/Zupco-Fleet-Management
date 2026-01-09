# Development Guide

## Development Environment Setup

### Prerequisites
- Python 3.8+
- Git
- Code editor (VS Code, PyCharm, etc.)
- Virtual environment

### Setup Steps
1. Clone repository
2. Create virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Create superuser: `python manage.py createsuperuser`
6. Start dev server: `python manage.py runserver`

## Code Structure

### Django Apps
- `fleet/`: Core fleet management models and views
- `api/`: REST API endpoints
- `config/`: Project settings

### Coding Standards
- Follow PEP 8
- Use Django conventions
- Write docstrings for functions/classes
- Add comments for complex logic

## Adding Features

### New Model
1. Define model in `fleet/models.py`
2. Create migration: `python manage.py makemigrations`
3. Apply migration: `python manage.py migrate`
4. Register in admin: `fleet/admin.py`
5. Create serializer: `api/serializers.py`
6. Create ViewSet: `api/views.py`
7. Add URL: `api/urls.py`

### New API Endpoint
1. Add ViewSet method or new View
2. Create/update serializer
3. Add URL route
4. Test with browsable API

## Testing

### Running Tests
```bash
python manage.py test
```

### Writing Tests
- Unit tests for models
- API endpoint tests
- Integration tests

## Debugging

### Django Debug Toolbar
- Install: `pip install django-debug-toolbar`
- Add to INSTALLED_APPS
- Configure in settings

### Logging
- Django logging configuration
- Use Python logging module
- Check console output

## Version Control

### Git Workflow
1. Create feature branch
2. Make changes
3. Commit with descriptive messages
4. Push to repository
5. Create pull request

### Commit Messages
- Use clear, descriptive messages
- Reference issue numbers if applicable

---

**Document Version**: 1.0

