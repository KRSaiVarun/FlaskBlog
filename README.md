# FlaskBlog

A clean, feature-rich blog application built with the Flask framework. This project demonstrates core web development concepts including user authentication, database management, and CRUD operations.

## Features

- **User Authentication & Authorization**
  - User Registration and Login/Logout.
  - Secure password hashing.
  - Profile pages for each user.
  - Account management (username, email, profile picture).

- **Blog Post Management**
  - Create, Read, Update, and Delete (CRUD) blog posts.
  - Rich text content for posts.
  - Automatic timestamps for post creation and updates.

- **User Interface**
  - Responsive design for optimal viewing on desktop and mobile.
  - Pagination for the home page to handle many posts.
  - Clean and modern layout.

- **Additional Features**
  - Password reset functionality via email.
  - File upload for user profile pictures.
  - Dedicated pages for posts by a specific user.

## Tech Stack

* **Backend:** Python, Flask
* **Database:** SQLite (with SQLAlchemy ORM)
* **Frontend:** HTML, CSS (Bootstrap), JavaScript
* **Authentication:** Flask-Login
* **File Handling:** Flask-Uploads / Pillow (for image processing)
* **Forms:** Flask-WTF
* **Password Hashing:** Werkzeug
* **Development Server:** Flask built-in server

## Installation & Setup

Follow these steps to get the project running on your local machine.

### Prerequisites

* Python 3.7 or higher
* pip (Python package manager)

### 1. Clone the Repository

```bash
git clone https://github.co
m/KRSaiVarun/FlaskBlog.git
cd FlaskBlog

# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

FlaskBlog/
├── flaskblog/                 # Main application package
│   ├── static/               # CSS, JavaScript, images
│   ├── templates/            # HTML Jinja2 templates
│   ├── __init__.py           # Application factory
│   ├── models.py             # Database models (User, Post)
│   ├── routes.py             # Application routes and view functions
│   ├── forms.py              # WTForms for registration, login, posts, etc.
│   └── utils.py              # Helper functions (e.g., saving pictures)
├── instance/                 # Instance folder (contains config.py and site.db)
├── migrations/               # Database migration scripts (if using Flask-Migrate)
├── requirements.txt          # Project dependencies
├── run.py                    # Script to run the application
└── README.md                 # This file


---

### Key Highlights of this README:

1.  **Professional Structure:** It follows the standard format of popular open-source projects.
2.  **Clear Feature List:** Immediately tells a visitor what the project does.
3.  **Detailed Setup Instructions:** Guides a user with zero context from cloning to running the app, including important steps like virtual environments and environment variables.
4.  **Tech Stack:** Shows the technologies used, which is crucial for developers.
5.  **Project Structure:** Helps other developers navigate the codebase quickly.
6.  **Contribution Guidelines:** Encourages and explains how others can help improve the project.

Project Link: https://github.com/KRSaiVarun/FlaskBlog

What is Django?
Django is a high-level Python web framework that enables rapid development of secure and maintainable websites. Unlike Flask (which is a micro-framework), Django comes with "batteries included" - meaning it provides many built-in features out of the box.

Key Django Features:
Built-in ORM (Object-Relational Mapping) for database operations

Automatic admin interface

User authentication system

URL routing and templating

Form handling

Security features (CSRF protection, SQL injection prevention, etc.)

Scalability for large applications

Why you might choose Django over Flask for a blog:
Aspect	Flask (Your Current Choice)	Django (Alternative)
Setup	Minimal, add what you need	"Batteries included"
Admin Panel	Manual creation needed	Built-in auto-generated
ORM	SQLAlchemy (separate)	Built-in Django ORM
Authentication	Flask-Login (extension)	Built-in auth system
Learning Curve	Gentle start, grows complex	Steeper initial learning
Blog Development	More manual coding needed	Faster development


Why you used Flask in your blog project:
Simplicity & Learning: Perfect for beginners to understand web fundamentals

Flexibility: You can choose exactly which components to use

Lightweight: Minimal overhead, fast for small to medium projects

Great for Blogs: The scale of a blog fits well with Flask's capabilities

Educational Value: Building everything manually teaches core concepts

Extensible: You used great extensions like:

Flask-Login for authentication

Flask-WTF for forms

Flask-SQLAlchemy for database

Your Tech Stack Choices:
python
# You built components manually:
- User Authentication → Used Flask-Login
- Database → Used SQLAlchemy + SQLite  
- Forms → Used Flask-WTF
- File Uploads → Implemented manually
- Templates → Used Jinja2 with Bootstrap
The Trade-off:
With Flask: You understand every piece of your application

With Django: You'd get these features built-in, but might not understand the underlying mechanics as deeply

Should you switch to Django?
Stick with Flask if:

You're learning web development fundamentals

You want fine-grained control over components

Your blog is relatively simple

You enjoy choosing your own libraries

Consider Django if:

You want to build the blog faster with less code

You need built-in admin features

You're planning a larger application with more features

You want to learn industry-standard practices



