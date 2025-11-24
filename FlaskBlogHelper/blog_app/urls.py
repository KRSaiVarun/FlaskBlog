from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='post-list'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update, name='profile-update'),
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin/user/<int:user_id>/', views.admin_user_detail, name='admin-user-detail'),
    path('admin/user/<int:user_id>/edit/', views.admin_user_edit, name='admin-user-edit'),
    path('admin/user/<int:user_id>/delete/', views.admin_user_delete, name='admin-user-delete'),
    path('admin/post/<int:post_id>/edit/', views.admin_post_edit, name='admin-post-edit'),
    path('admin/post/<int:post_id>/delete/', views.admin_post_delete, name='admin-post-delete'),
    path('admin/post/<int:post_id>/publish/', views.admin_post_publish, name='admin-post-publish'),
]
