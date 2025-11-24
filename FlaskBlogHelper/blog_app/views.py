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
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from typing import Protocol, cast

# Reusable constants
LOGIN_TEMPLATE = 'blog_app/login.html'
PERM_ERROR = "You do not have permission to access this page."
SUCCESS_POST_CREATE = "Post created successfully!"
SUCCESS_POST_UPDATE = "Post updated successfully!"
SUCCESS_POST_DELETE = "Post deleted successfully!"


class UserWithProfile(Protocol):
    """Typing Protocol to tell static checkers that User objects have a Profile."""
    profile: 'Profile'
    id: int
    username: str
    is_authenticated: bool


from .models import Post, Profile
from .forms import PostForm, UserRegisterForm, UserLoginForm, ProfileUpdateForm, UserUpdateForm


class AdminRequiredMixin(LoginRequiredMixin):
    """Mixin to require admin privileges."""

    def dispatch(self, request, *args, **kwargs):
        user_with_profile = cast(UserWithProfile, request.user)
        if not (request.user.is_authenticated and user_with_profile.profile.is_admin):
            messages.error(request, PERM_ERROR)
            return redirect('post-list')
        return super().dispatch(request, *args, **kwargs)


class PostListView(ListView):
    model = Post
    template_name = 'blog_app/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_date']
    paginate_by = 10  # Add pagination

    def get_queryset(self):
        # Only show published posts to non-admin users
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.filter(status='published')

        user_with_profile = cast(UserWithProfile, self.request.user)
        if not user_with_profile.profile.is_admin:
            return queryset.filter(Q(status='published') | Q(author=self.request.user))

        return queryset


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog_app/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        # Control post visibility
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.filter(status='published')

        user_with_profile = cast(UserWithProfile, self.request.user)
        if not user_with_profile.profile.is_admin:
            return queryset.filter(Q(status='published') | Q(author=self.request.user))

        return queryset


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog_app/post_form.html'
    success_url = reverse_lazy('post-list')
    login_url = 'login'

    def get_initial(self):
        """Set initial status for new posts."""
        return {'status': 'draft'}

    def form_valid(self, form):
        try:
            form.instance.author = self.request.user
            if form.cleaned_data.get('status') == 'published':
                form.instance.published_date = timezone.now()
            messages.success(self.request, SUCCESS_POST_CREATE)
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
    login_url = 'login'

    def test_func(self):
        post = cast(Post, self.get_object())
        user_with_profile = cast(UserWithProfile, self.request.user)
        return self.request.user == post.author or user_with_profile.profile.is_admin

    def get_success_url(self):
        # Use get_object() to retrieve the instance so static analyzers can determine the attribute
        obj = self.get_object()
        return reverse('post-detail', kwargs={'pk': obj.pk})

    def form_valid(self, form):
        try:
            obj = cast(Post, self.get_object())
            if form.cleaned_data.get('status') == 'published' and obj.status != 'published':
                form.instance.published_date = timezone.now()
            elif form.cleaned_data.get('status') == 'draft':
                form.instance.published_date = None

            response = super().form_valid(form)
            messages.success(self.request, SUCCESS_POST_UPDATE)
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
        post = cast(Post, self.get_object())
        user_with_profile = cast(UserWithProfile, self.request.user)
        return self.request.user == post.author or user_with_profile.profile.is_admin

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, SUCCESS_POST_DELETE)
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
            Profile.objects.get_or_create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Welcome to FlaskBlog, {username}! Your account has been created successfully.')

            # Optional: Auto-login after registration
            # login(request, user)
            # return redirect('post-list')

            return redirect('login')

        # Enhanced error handling
        self._handle_form_errors(form, request)
        return render(request, 'blog_app/register.html', {'form': form})

    def _handle_form_errors(self, form, request):
        """Handle common form errors with user-friendly messages."""
        error_handlers = {
            'password1': self._handle_password_errors,
            'username': self._handle_username_errors,
            'email': self._handle_email_errors
        }

        for field, handler in error_handlers.items():
            if field in form.errors:
                handler(form.errors[field], request)

    def _handle_password_errors(self, errors, request):
        for error in errors:
            error_str = str(error).lower()
            if 'common' in error_str:
                messages.warning(request, 'Please choose a stronger password that is not commonly used.')
            elif 'numeric' in error_str:
                messages.warning(request, 'Your password cannot be entirely numeric.')
            elif 'similar' in error_str:
                messages.warning(request, 'Your password is too similar to your personal information.')
            elif 'short' in error_str:
                messages.warning(request, 'Your password is too short.')

    def _handle_username_errors(self, errors, request):
        for error in errors:
            if 'valid username' in str(error).lower():
                messages.warning(request, 'Username can only contain letters, numbers, and @/./+/-/_ characters.')
            elif 'already exists' in str(error).lower():
                messages.warning(request, 'This username is already taken.')

    def _handle_email_errors(self, errors, request):
        for error in errors:
            if 'already exists' in str(error).lower():
                messages.warning(request, 'This email address is already registered.')


# User Login View
class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('post-list')
        form = UserLoginForm()
        return render(request, LOGIN_TEMPLATE, {'form': form})

    def post(self, request):
        form = UserLoginForm(data=request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me') == 'on'

        if not (username and password):
            messages.error(request, 'Please enter both username/email and password.')
            return render(request, LOGIN_TEMPLATE, {'form': form})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            messages.success(request, f'Welcome back, {user.username}!')

            # Redirect to next parameter if exists
            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'post-list')
        else:
            messages.error(request, 'Invalid username/email or password. Please try again.')

        return render(request, LOGIN_TEMPLATE, {'form': form})


# Logout view
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


# Profile Views
@login_required
def profile_view(request):
    user_posts = Post.objects.filter(author=request.user).order_by('-created_date')
    context = {
        'user': request.user,
        'user_posts': user_posts
    }
    return render(request, 'blog_app/profile.html', context)


@login_required
def profile_update(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)  # Added request.FILES for image upload

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'blog_app/profile_update.html', context)


# Admin Views
@login_required
def admin_dashboard(request):
    user_with_profile = cast(UserWithProfile, request.user)
    if not user_with_profile.profile.is_admin:
        messages.error(request, PERM_ERROR)
        return redirect('post-list')

    # Optimized queries
    stats = {
        'user_count': User.objects.count(),
        'post_count': Post.objects.count(),
        'draft_count': Post.objects.filter(status='draft').count(),
        'published_count': Post.objects.filter(status='published').count(),
    }

    users = Profile.objects.select_related('user').all()
    posts = Post.objects.select_related('author').all().order_by('-created_date')[:10]  # Limit posts
    drafts = Post.objects.select_related('author').filter(status='draft').order_by('-created_date')

    context = {
        **stats,
        'users': users,
        'posts': posts,
        'drafts': drafts
    }

    return render(request, 'blog_app/admin_dashboard.html', context)


# Admin user management views
@login_required
def admin_user_detail(request, user_id):
    user_with_profile = cast(UserWithProfile, request.user)
    if not user_with_profile.profile.is_admin:
        messages.error(request, PERM_ERROR)
        return redirect('post-list')

    user = get_object_or_404(User, id=user_id)
    user_posts = Post.objects.filter(author=user).order_by('-created_date')

    context = {
        'user': user,
        'user_posts': user_posts
    }

    return render(request, 'blog_app/admin_user_detail.html', context)


@login_required
def admin_user_edit(request, user_id):
    user_with_profile = cast(UserWithProfile, request.user)
    if not user_with_profile.profile.is_admin:
        messages.error(request, PERM_ERROR)
        return redirect('post-list')

    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'User {user.username} has been updated successfully!')
            return redirect('admin-user-detail', user_id=user.pk)
    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user': user
    }

    return render(request, 'blog_app/admin_user_edit.html', context)


@login_required
def admin_user_delete(request, user_id):
    user_with_profile = cast(UserWithProfile, request.user)
    if not user_with_profile.profile.is_admin:
        messages.error(request, PERM_ERROR)
        return redirect('post-list')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Prevent admin from deleting themselves
        if user == request.user:
            messages.error(request, "You cannot delete your own account!")
            return redirect('admin-user-detail', user_id=user_id)

        username = user.username
        user.delete()
        messages.success(request, f'User {username} has been deleted successfully!')
        return redirect('admin-dashboard')

    context = {'user': user}
    return render(request, 'blog_app/admin_user_delete.html', context)


# Admin post management views
@login_required
def admin_post_edit(request, post_id):
    user_with_profile = cast(UserWithProfile, request.user)
    if not user_with_profile.profile.is_admin:
        messages.error(request, PERM_ERROR)
        return redirect('post-list')

    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)

        if form.is_valid():
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


@login_required
def admin_post_delete(request, post_id):
    user_with_profile = cast(UserWithProfile, request.user)
    if not user_with_profile.profile.is_admin:
        messages.error(request, PERM_ERROR)
        return redirect('post-list')

    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        title = post.title
        post.delete()
        messages.success(request, f'Post "{title}" has been deleted successfully!')
        return redirect('admin-dashboard')

    context = {'post': post}
    return render(request, 'blog_app/admin_post_delete.html', context)


@login_required
def admin_post_publish(request, post_id):
    user_with_profile = cast(UserWithProfile, request.user)
    if not user_with_profile.profile.is_admin:
        messages.error(request, PERM_ERROR)
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
