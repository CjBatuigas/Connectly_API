from posts.models import Post

class PostFactory:
    @staticmethod
    def create_post(content, author):
        return Post.objects.create(
            content=content,
            author=author
        )
