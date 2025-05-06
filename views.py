from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.views import View
from django.contrib.auth.models import User
from django.db.models import Count

from .models import Post, Profile
from .forms import PostForm, UserRegisterForm, UserLoginForm, ProfileUpdateForm, UserUpdateForm


class PostListView(ListView):
    model = Post
    template_name = 'blog_app/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_date']


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog_app/post_detail.html'
    context_object_name = 'post'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog_app/post_form.html'
    success_url = reverse_lazy('post-list')
    login_url = 'login'
    
    def form_valid(self, form):
        try:
            form.instance.author = self.request.user
            form.instance.published_date = timezone.now() if form.cleaned_data.get('status') == 'published' else None
            messages.success(self.request, "Post created successfully!")
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Error creating post: {str(e)}")
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog_app/post_form.html'
    success_url = reverse_lazy('post-list')  # Fallback success URL
    login_url = 'login'
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.profile.is_admin
    
    def get_success_url(self):
        # Use success_url or get_absolute_url from model
        return self.object.get_absolute_url()
    
    def form_valid(self, form):
        try:
            # Update published_date if status changes to published
            if form.cleaned_data.get('status') == 'published' and self.object.status != 'published':
                form.instance.published_date = timezone.now()
            elif form.cleaned_data.get('status') == 'draft':
                form.instance.published_date = None
                
            response = super().form_valid(form)
            messages.success(self.request, "Post updated successfully!")
            return response
        except Exception as e:
            messages.error(self.request, f"Error updating post: {str(e)}")
            return self.form_invalid(form)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog_app/post_confirm_delete.html'
    success_url = reverse_lazy('post-list')
    login_url = 'login'
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.profile.is_admin
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Post deleted successfully!")
        return super().delete(request, *args, **kwargs)


class AboutView(TemplateView):
    template_name = 'blog_app/about.html'


# User Registration View
class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('post-list')
        form = UserRegisterForm()
        return render(request, 'blog_app/register.html', {'form': form})
    
    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a profile for the user
            Profile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Welcome to FlaskBlog, {username}! Your account has been created successfully.')
            return redirect('login')
        else:
            # Provide user-friendly error messages for common validation issues
            password_errors = form.errors.get('password1', [])
            if password_errors:
                for error in password_errors:
                    if 'common' in str(error).lower():
                        messages.warning(request, 'Please choose a stronger password that is not commonly used.')
                    elif 'numeric' in str(error).lower():
                        messages.warning(request, 'Your password cannot be entirely numeric. Please include some letters.')
                    elif 'similar' in str(error).lower():
                        messages.warning(request, 'Your password is too similar to your personal information.')
                    
            username_errors = form.errors.get('username', [])
            if username_errors:
                for error in username_errors:
                    if 'valid username' in str(error).lower():
                        messages.warning(request, 'Username can only contain letters, numbers, and @/./+/-/_ characters.')
        
        return render(request, 'blog_app/register.html', {'form': form})


# User Login View
class LoginView(View):
    def get(self, request):
        # If user is already logged in, redirect to home page
        if request.user.is_authenticated:
            return redirect('post-list')
        form = UserLoginForm()
        return render(request, 'blog_app/login.html', {'form': form})
    
    def post(self, request):
        form = UserLoginForm(data=request.POST)
        
        # For custom authentication with email support, we extract the username/email and password directly
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me') == 'on'
        
        if username and password:
            # Use our custom authentication backend
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                if not remember_me:
                    # Session expires when the browser is closed
                    request.session.set_expiry(0)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('post-list')
            else:
                messages.error(request, 'Invalid username/email or password. Please try again.')
                return render(request, 'blog_app/login.html', {'form': form})
        else:
            messages.error(request, 'Please enter both username/email and password.')
        
        return render(request, 'blog_app/login.html', {'form': form})


# Logout view
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


# Profile View
@login_required
def profile_view(request):
    user_posts = Post.objects.filter(author=request.user).order_by('-created_date')
    context = {
        'user': request.user,
        'user_posts': user_posts
    }
    return render(request, 'blog_app/profile.html', context)


# Profile Update View
@login_required
def profile_update(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    
    return render(request, 'blog_app/profile_update.html', context)


# Admin Dashboard
@login_required
def admin_dashboard(request):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You do not have permission to access the admin dashboard.")
        return redirect('post-list')
    
    # Get dashboard data
    user_count = User.objects.count()
    post_count = Post.objects.count()
    draft_count = Post.objects.filter(status='draft').count()
    
    # Get all users with profiles
    users = Profile.objects.select_related('user').all()
    
    # Get all posts
    posts = Post.objects.select_related('author').all().order_by('-created_date')
    
    # Get all draft posts
    drafts = Post.objects.select_related('author').filter(status='draft').order_by('-created_date')
    
    context = {
        'user_count': user_count,
        'post_count': post_count,
        'draft_count': draft_count,
        'users': users,
        'posts': posts,
        'drafts': drafts
    }
    
    return render(request, 'blog_app/admin_dashboard.html', context)


# Admin: User Detail
@login_required
def admin_user_detail(request, user_id):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('post-list')
    
    user = get_object_or_404(User, id=user_id)
    user_posts = Post.objects.filter(author=user).order_by('-created_date')
    
    context = {
        'user': user,
        'user_posts': user_posts
    }
    
    return render(request, 'blog_app/admin_user_detail.html', context)


# Admin: Edit User
@login_required
def admin_user_edit(request, user_id):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('post-list')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, instance=user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'User {user.username} has been updated successfully!')
            return redirect('admin-user-detail', user_id=user.id)
    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user': user
    }
    
    return render(request, 'blog_app/admin_user_edit.html', context)


# Admin: Delete User
@login_required
def admin_user_delete(request, user_id):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('post-list')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} has been deleted successfully!')
        return redirect('admin-dashboard')
    
    context = {
        'user': user
    }
    
    return render(request, 'blog_app/admin_user_delete.html', context)


# Admin: Edit Post
@login_required
def admin_post_edit(request, post_id):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('post-list')
    
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        
        if form.is_valid():
            # Update published_date if status changes to published
            if form.cleaned_data.get('status') == 'published' and post.status != 'published':
                form.instance.published_date = timezone.now()
            elif form.cleaned_data.get('status') == 'draft':
                form.instance.published_date = None
                
            form.save()
            messages.success(request, f'Post "{post.title}" has been updated successfully!')
            return redirect('admin-dashboard')
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post
    }
    
    return render(request, 'blog_app/admin_post_edit.html', context)


# Admin: Delete Post
@login_required
def admin_post_delete(request, post_id):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('post-list')
    
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        title = post.title
        post.delete()
        messages.success(request, f'Post "{title}" has been deleted successfully!')
        return redirect('admin-dashboard')
    
    context = {
        'post': post
    }
    
    return render(request, 'blog_app/admin_post_delete.html', context)


# Admin: Publish Post
@login_required
def admin_post_publish(request, post_id):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('post-list')
    
    post = get_object_or_404(Post, id=post_id)
    
    if post.status == 'draft':
        post.status = 'published'
        post.published_date = timezone.now()
        post.save()
        messages.success(request, f'Post "{post.title}" has been published successfully!')
    else:
        messages.info(request, f'Post "{post.title}" is already published.')
    
    return redirect('admin-dashboard')
