# FlaskBlog - Django Blog Application

## Overview
A feature-rich blog application built with Django framework. Despite the name "FlaskBlog", this project uses Django (not Flask) to provide a robust blogging platform with user authentication, post management, and an admin dashboard.

## Current State
The application is fully set up and running on Replit with:
- Django 5.2.8 backend
- SQLite database configured and migrated
- User authentication system
- Blog post CRUD operations
- Admin dashboard for content management
- Responsive Bootstrap UI
- Running on port 5000

## Recent Changes (November 16, 2025)
- Reorganized project structure from flat directory to proper Django architecture
- Created proper Django app structure (blog_project/, blog_app/, templates/, static/)
- Converted Flask models and forms to Django equivalents
- Set up SQLite database and applied migrations
- Configured Django server to run on port 5000
- Fixed template directory structure for Django template loader
- All dependencies installed and configured
- **Added automatic Profile creation** via signals to prevent crashes for superusers and other users created outside the registration flow
- Created management command `create_missing_profiles` to backfill profiles for existing users

## Project Architecture

### Directory Structure
```
.
├── blog_project/          # Django project configuration
│   ├── __init__.py
│   ├── settings.py       # Project settings
│   ├── urls.py          # Root URL configuration
│   ├── wsgi.py          # WSGI entry point
│   └── asgi.py          # ASGI entry point
├── blog_app/            # Main Django application
│   ├── migrations/      # Database migrations
│   ├── __init__.py
│   ├── models.py        # Post and Profile models
│   ├── views.py         # View functions and classes
│   ├── forms.py         # Django forms
│   ├── urls.py          # App URL patterns
│   ├── apps.py          # App configuration
│   └── auth_backends.py # Custom authentication backend
├── templates/           # HTML templates
│   ├── base.html       # Base template (shared)
│   └── blog_app/       # App-specific templates
│       ├── index.html
│       ├── post_list.html
│       ├── post_detail.html
│       ├── post_form.html
│       ├── register.html
│       ├── login.html
│       ├── profile.html
│       └── admin_*.html
├── static/             # Static files
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript
│   └── images/        # Images
├── manage.py          # Django management script
├── pyproject.toml     # Python dependencies
└── db.sqlite3         # SQLite database
```

### Database Models
1. **Post Model**
   - title: CharField (max 200 chars)
   - content: TextField
   - author: ForeignKey to User
   - created_date: DateTimeField
   - published_date: DateTimeField (nullable)
   - status: CharField (draft/published)

2. **Profile Model**
   - user: OneToOneField to User
   - bio: TextField
   - location: CharField
   - birth_date: DateField
   - profile_image: CharField (URL)
   - date_joined: DateTimeField
   - is_admin: BooleanField

### Key Features
1. **User Authentication**
   - Registration with email validation
   - Login with username or email
   - Custom authentication backend
   - Profile management

2. **Blog Post Management**
   - Create, read, update, delete posts
   - Draft and published status
   - Post listing with pagination
   - User-specific post pages

3. **Admin Dashboard**
   - User management
   - Post moderation
   - Draft post publishing
   - User role management

### URL Routes
- `/` - Home page (post list)
- `/post/<id>/` - Individual post detail
- `/post/new/` - Create new post
- `/post/<id>/update/` - Edit post
- `/post/<id>/delete/` - Delete post
- `/register/` - User registration
- `/login/` - User login
- `/logout/` - User logout
- `/profile/` - User profile
- `/profile/update/` - Update profile
- `/admin/dashboard/` - Admin dashboard
- `/admin/user/<id>/` - User management
- `/admin/post/<id>/` - Post management

## Technical Stack
- **Framework**: Django 5.2.8
- **Database**: SQLite (development)
- **Frontend**: Bootstrap, vanilla JavaScript
- **Python Version**: 3.11

## Environment Configuration
- `SECRET_KEY`: Configured in settings.py (should be moved to environment variable for production)
- `DEBUG`: True (development mode)
- `ALLOWED_HOSTS`: ['*'] (configured for Replit)
- `CSRF_TRUSTED_ORIGINS`: Configured for Replit domains

## Development Workflow
1. Run server: `python manage.py runserver 0.0.0.0:5000`
2. Make migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`

## Next Steps for Enhancement
1. Create a superuser account for admin access
2. Add sample blog posts
3. Implement password reset via email
4. Add post categories and tags
5. Implement comment system
6. Add search functionality
7. Deploy to production (consider PostgreSQL for database)

## Known Issues & Future Improvements
1. **Profile Access Protection**: While critical views (admin_dashboard, profile_update) have defensive profile access using get_or_create(), some other views still directly access request.user.profile. The automatic profile creation via signals handles most cases, but additional defensive programming could be added to other views for extra robustness.
2. **Email Configuration**: Password reset functionality requires email configuration (EMAIL_USER and EMAIL_PASS environment variables).

## User Preferences
None specified yet.
