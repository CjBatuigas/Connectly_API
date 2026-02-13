from django.urls import path
from .views import UserListCreate, PostListCreate, CommentListCreate, LoginView


urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    # path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('login/', LoginView.as_view(), name='login'),
]
