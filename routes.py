import math
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from main import app, db
from forms import RegistrationForm, LoginForm, PostForm, UpdateProfileForm
from models import User, Post

@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = app.config['POSTS_PER_PAGE']
    posts = Post.get_all_posts(page, per_page)
    total_posts = Post.count_posts()
    total_pages = math.ceil(total_posts / per_page)
    
    return render_template('index.html', 
                          posts=posts, 
                          page=page, 
                          total_pages=total_pages)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    user_posts = Post.get_user_posts(current_user.id)
    return render_template('profile.html', title='Profile', posts=user_posts)

@app.route('/profile/update', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateProfileForm(current_user.username, current_user.email)
    
    if form.validate_on_submit():
        # Update user in database using SQLAlchemy
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile'))
    
    # Pre-populate form with current user data
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('update_profile.html', title='Update Profile', form=form)

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        Post.create_post(
            title=form.title.data,
            content=form.content.data,
            author_id=current_user.id
        )
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')

@app.route('/post/<post_id>')
def post(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        flash('Post not found. It may have been deleted.', 'warning')
        return redirect(url_for('home'))
    
    return render_template('post_detail.html', title=post.title, post=post)

@app.route('/post/<post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        flash('Post not found. It may have been deleted.', 'warning')
        return redirect(url_for('home'))
    
    # Check if the current user is the author of the post
    if post.author_id != current_user.id:
        flash('You are not authorized to edit this post.', 'danger')
        return redirect(url_for('home'))
    
    form = PostForm()
    if form.validate_on_submit():
        try:
            post.update(
                title=form.title.data,
                content=form.content.data
            )
            flash('Your post has been updated!', 'success')
            return redirect(url_for('post', post_id=post.id))
        except Exception as e:
            app.logger.error(f"Error updating post: {e}")
            flash('An error occurred while updating the post.', 'danger')
            return redirect(url_for('home'))
    
    # Pre-populate form with post data
    if request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    
    return render_template('edit_post.html', title='Update Post', form=form, legend='Update Post')

@app.route('/post/<post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        flash('Post not found. It may have been deleted already.', 'warning')
        return redirect(url_for('home'))
    
    # Check if the current user is the author of the post
    if post.author_id != current_user.id:
        flash('You are not authorized to delete this post.', 'danger')
        return redirect(url_for('home'))
    
    try:
        post.delete()
        flash('Your post has been deleted!', 'success')
    except Exception as e:
        app.logger.error(f"Error deleting post: {e}")
        flash('An error occurred while deleting the post.', 'danger')
    
    return redirect(url_for('home'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
