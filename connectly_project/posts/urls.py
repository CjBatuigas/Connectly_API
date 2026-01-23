from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.create_user, name='create_user'),
    path('posts/', views.get_posts, name='get_posts'),
    path('posts/create/', views.create_post, name='create_post'),
]
