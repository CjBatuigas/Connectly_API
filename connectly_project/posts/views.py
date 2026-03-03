from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .permissions import IsPostAuthor
from rest_framework.authentication import TokenAuthentication
from .singletons.logger_singleton import LoggerSingleton
from posts.factories.post_factory import PostFactory

logger = LoggerSingleton().get_logger()


class UserListCreate(APIView):

    def get(self, request):
        logger.info("Fetching all users")
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        logger.info("User registration attempt")

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"User created successfully: {user.username}")
            return Response(
                {"id": user.id, "username": user.username, "email": user.email},
                status=status.HTTP_201_CREATED
            )

        logger.warning(f"User registration failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"User {request.user} requested their posts")

        posts = Post.objects.filter(author=request.user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        logger.info(f"User {request.user} attempting to create a post")

        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            logger.info(f"Post created successfully by {request.user}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(f"Post creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentListCreate(APIView):

    def get(self, request):
        logger.info("Fetching all comments")
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        logger.info("Comment creation attempt")

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Comment created successfully")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(f"Comment creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):

    def post(self, request):
        username = request.data.get("username")

        logger.info(f"Login attempt for user: {username}")

        user = authenticate(
            username=username,
            password=request.data.get("password")
        )

        if user is not None:
            login(request, user)
            logger.info(f"User logged in successfully: {username}")
            return Response(
                {"message": "Authentication successful!"},
                status=200
            )

        logger.warning(f"Failed login attempt for user: {username}")
        return Response({"error": "Invalid credentials"}, status=401)
    

class PostDetailView(APIView):
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        logger.info(f"User {request.user} accessing post {pk}")

        try:
            post = Post.objects.get(pk=pk)
            self.check_object_permissions(request, post)
            return Response({"content": post.content})
        except Post.DoesNotExist:
            logger.error(f"Post {pk} not found")
            return Response({"error": "Post not found"}, status=404)


class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        logger.info(f"Authenticated access by {request.user}")
        return Response({"message": "Authenticated!"})


class CreatePostView(APIView):
    """
    API view to create posts using the PostFactory.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        user = request.user

        logger.info(f"User {user} attempting to create a post")

        try:
            post = PostFactory.create_post(
                post_type=data['post_type'],
                title=data['title'],
                content=data.get('content', ''),
                metadata=data.get('metadata', {})
            )

            logger.info(f"Post {post.id} created successfully by user {user}")

            return Response(
                {
                    'message': 'Post created successfully!',
                    'post_id': post.id
                },
                status=status.HTTP_201_CREATED
            )

        except ValueError as e:
            logger.warning(f"Post creation failed for user {user}: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error creating post for user {user}: {e}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )