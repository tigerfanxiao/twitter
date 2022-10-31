from comments.models import Comment
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase as DjangoTestCase  # 把 django 自带的重命名
from likes.models import Like
from rest_framework.test import APIClient
from tweets.models import Tweet
from newsfeeds.models import NewsFeed

# 很多测试都需要创建用户 create_user, 和 create_tweet, 所以抽象出两个方法
# 这里覆盖 django 自带的 TestCase是为了减少对已经有的代码进行修改, 是一种常用方法


class TestCase(DjangoTestCase):
    # 这里默认初始值都是先设置为 None 后, 再赋值. 这样不会让定义时写得太长
    @property
    def anonymous_client(self):
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client

    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'generic password'

        if email is None:
            email = f"{username}@email.com"
        # 这里要用 User 自带的 create_user 方法, 因为 django 会对 password 做 normalize处理
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default tweet content'
        return Tweet.objects.create(
            user=user,
            content=content,
        )

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'default comment content'
        return Comment.objects.create(
            user=user,
            tweet=tweet,
            content=content,
        )

    def create_like(self, user, target): # 这里 target 是 comment 或者 tweet
        # 使用 get_or_create方法,可以获得, 也可以创建, 为了测试的时候, 可以模拟点赞多次的情况
        # _ 表示是创建的还是 get 回来的结果
        instance, _ = Like.objects.get_or_create(
            user=user,
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
        )
        return instance

    def create_user_and_client(self, *args, **kwargs):
        user = self.create_user(*args, **kwargs)
        client = APIClient()
        client.force_authenticate(user)
        return user, client

    def create_newsfeed(self, user, tweet):
        return NewsFeed.objects.create(user=user, tweet=tweet)