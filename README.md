# FlaskBlog

A clean, feature-rich blog application built with the Flask framework. This project demonstrates core web development concepts including user authentication, database management, and CRUD operations.

## 🚀 Features

### User Authentication & Authorization
- **User Registration and Login/Logout** - Secure account creation and session management
- **Password Hashing** - Secure password storage using Werkzeug
- **Profile Management** - Customizable user profiles with profile pictures
- **Account System** - Update username, email, and personal information

### Blog Post Management
- **CRUD Operations** - Create, Read, Update, and Delete blog posts
- **Rich Text Content** - Support for formatted blog post content
- **Automatic Timestamps** - Creation and modification dates tracked automatically
- **Author Attribution** - Posts linked to user accounts

### User Experience
- **Responsive Design** - Optimized for desktop and mobile devices
- **Pagination** - Efficient handling of large post collections
- **Modern UI** - Clean, professional interface using Bootstrap
- **Intuitive Navigation** - Easy-to-use menu system

### Advanced Features
- **Password Reset** - Email-based password recovery system
- **File Uploads** - Profile picture upload and management
- **User-specific Pages** - Dedicated pages for each user's posts
- **Session Management** - Secure user session handling

## 🛠 Tech Stack

### Backend
- **Python** - Primary programming language
- **Flask** - Micro web framework
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and validation
- **Werkzeug** - Password hashing and security

### Database
- **SQLite** - Lightweight database engine
- **SQLAlchemy ORM** - Database abstraction and management

### Frontend
- **HTML5** - Markup structure
- **CSS3** - Styling and layout
- **Bootstrap** - Responsive framework
- **JavaScript** - Client-side interactivity
- **Jinja2** - Template engine

### Media & Files
- **Flask-Uploads** - File upload handling
- **Pillow** - Image processing and optimization

## 📦 Installation & Setup

Follow these steps to run FlaskBlog on your local machine.

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Git (for version control)

### Step 1: Clone the Repository
```bash
git clone https://github.com/KRSaiVarun/FlaskBlog.git
cd FlaskBlog
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Set required environment variables:

**Windows (Command Prompt):**
```cmd
set SECRET_KEY=your_very_secret_key_here
set FLASK_APP=run.py
set FLASK_ENV=development
```

**macOS/Linux (Bash):**
```bash
export SECRET_KEY="your_very_secret_key_here"
export FLASK_APP=run.py
export FLASK_ENV=development
```

**Optional Email Configuration (for password resets):**
```bash
export EMAIL_USER="your_email@gmail.com"
export EMAIL_PASS="your_app_password"
```

### Step 5: Database Setup
Initialize the database:
```bash
python
>>> from flaskblog import db, create_app
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
... 
>>> exit()
```

### Step 6: Run the Application
```bash
# Method 1: Using python
python run.py

# Method 2: Using flask command
flask run
```

### Step 7: Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

## 📁 Project Structure

```
FlaskBlog/
├── flaskblog/                 # Main application package
│   ├── static/               # Static assets
│   │   ├── css/             # Stylesheets
│   │   ├── js/              # JavaScript files
│   │   └── images/          # Images and icons
│   ├── templates/           # HTML templates
│   │   ├── layout.html      # Base template
│   │   ├── home.html        # Home page
│   │   ├── register.html    # Registration page
│   │   ├── login.html       # Login page
│   │   ├── account.html     # User account page
│   │   ├── create_post.html # Post creation form
│   │   └── post.html        # Individual post view
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models (User, Post)
│   ├── routes.py            # URL routes and view functions
│   ├── forms.py             # WTForms definitions
│   └── utils.py             # Helper functions and utilities
├── instance/                # Instance-specific files
│   ├── config.py           # Configuration settings
│   └── site.db            # SQLite database file
├── migrations/             # Database migration scripts
├── requirements.txt        # Python dependencies
├── run.py                 # Application entry point
└── README.md              # Project documentation
```

## 🎯 Usage Guide

### For Visitors
1. **Browse Posts** - View all blog posts on the home page
2. **Read Content** - Click on any post to read full content
3. **Explore Users** - View posts by specific authors
4. **Pagination** - Navigate through multiple pages of posts

### For Registered Users
1. **Registration** - Create a new account
2. **Login** - Access your account dashboard
3. **Create Posts** - Write and publish new blog posts
4. **Manage Account** - Update profile information and picture
5. **Edit Content** - Modify your existing posts
6. **Password Reset** - Recover account access if needed

## 🔧 API Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/` | Home page with all posts | Public |
| GET | `/register` | User registration form | Public |
| POST | `/register` | Create new user | Public |
| GET | `/login` | User login form | Public |
| POST | `/login` | Authenticate user | Public |
| GET | `/logout` | User logout | Required |
| GET | `/account` | User profile page | Required |
| POST | `/account` | Update user profile | Required |
| GET | `/post/new` | Create new post form | Required |
| POST | `/post/new` | Submit new post | Required |
| GET | `/post/<int:post_id>` | View specific post | Public |
| GET | `/post/<int:post_id>/update` | Edit post form | Required |
| POST | `/post/<int:post_id>/update` | Update post | Required |
| POST | `/post/<int:post_id>/delete` | Delete post | Required |
| GET | `/user/<string:username>` | User's posts | Public |

## 🎨 Customization

### Styling
- Modify CSS files in `flaskblog/static/css/`
- Update Bootstrap classes in templates
- Customize color scheme and layout

### Functionality
- Add new routes in `routes.py`
- Create new database models in `models.py`
- Implement additional forms in `forms.py`

### Configuration
- Update application settings in `instance/config.py`
- Modify environment variables as needed
- Configure email settings for password resets

## 🚀 Deployment

### Development Deployment
```bash
flask run --host=0.0.0.0 --port=5000
```

### Production Deployment
For production deployment, consider:
- **WSGI Server**: Gunicorn or uWSGI
- **Reverse Proxy**: Nginx or Apache
- **Process Manager**: Systemd or Supervisor
- **Database**: PostgreSQL or MySQL
- **Cloud Platforms**: Heroku, AWS, DigitalOcean

Example production setup:
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 🧪 Testing

Run tests to ensure functionality:
```bash
# Install testing dependencies
pip install pytest flask-testing

# Run tests
python -m pytest tests/
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit Your Changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push to Branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open a Pull Request**

### Contribution Guidelines
- Follow PEP 8 Python style guide
- Write meaningful commit messages
- Add tests for new functionality
- Update documentation as needed
- Ensure code is clean and readable

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **K. R. Sai Varun** - Initial work - [KRSaiVarun](https://github.com/KRSaiVarun)

## 🙏 Acknowledgments

- Flask community for excellent documentation
- Bootstrap team for responsive design framework
- SQLAlchemy for robust ORM functionality
- Contributors and testers

## 🔄 Changelog

### Version 1.0.0
- Initial release
- User authentication system
- Blog post CRUD operations
- Responsive design implementation

## 🆘 Support

If you encounter any issues:

1. **Check Documentation** - Review this README and code comments
2. **Search Issues** - Look for similar problems in GitHub issues
3. **Create New Issue** - Provide detailed description and steps to reproduce
4. **Contact Maintainer** - Reach out for direct support

## 🌟 Why Flask Was Chosen

### Educational Value
This project intentionally uses Flask instead of Django to provide deeper understanding of web development fundamentals:

- **Manual Implementation** - Build components from scratch
- **Framework Understanding** - Learn how web frameworks work internally
- **Component Flexibility** - Choose and integrate specific libraries
- **Architecture Control** - Design application structure intentionally

### Technical Advantages
- **Lightweight** - Minimal overhead for blog applications
- **Flexible** - Easy to swap components and libraries
- **Explicit** - Every line of code is intentional and understood
- **Scalable** - Right-sized for project requirements

### Django Comparison

| Aspect | Flask (This Project) | Django (Alternative) |
|--------|---------------------|---------------------|
| **Architecture** | Micro-framework | Full-stack framework |
| **Setup** | Manual component selection | "Batteries included" |
| **Admin Panel** | Custom implementation | Built-in auto-generated |
| **ORM** | SQLAlchemy (flexible) | Built-in Django ORM |
| **Authentication** | Flask-Login (modular) | Built-in auth system |
| **Learning Curve** | Gentle, progressive | Steeper initial learning |
| **Development Speed** | More manual coding | Faster for standard features |

### When to Choose Django
While Flask is perfect for this educational project, consider Django for:
- Enterprise applications with complex business logic
- Projects requiring built-in admin interfaces
- Teams needing strict project structure conventions
- Applications requiring extensive built-in security
- Rapid development of standard web applications

## 📞 Contact

- **GitHub**: [KRSaiVarun](https://github.com/KRSaiVarun)
- **Project Link**: [https://github.com/KRSaiVarun/FlaskBlog](https://github.com/KRSaiVarun/FlaskBlog)
- **Issues**: [GitHub Issues](https://github.com/KRSaiVarun/FlaskBlog/issues)



---













