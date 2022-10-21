from datetime import timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def test_hours_to_now(self):
        # 创建一个用户
        linghu = User.objects.create_user(username='linghu')
        # 这个用户发布一个 tweet
        tweet = Tweet.objects.create(user=linghu, content="Jiuzhang dafa good!")
        # 修改 tweet 的时间往前退 10 个小时
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()  # 修改完 created_at 在 insert数据库
        # 验证当前时间和 tweet 发布时间相差 10 个小时
        self.assertEqual(tweet.hours_to_now, 10)

