from datetime import timedelta
from testing.testcases import TestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from utils.time_helpers import utc_now


class TweetTests(TestCase):
    def setUp(self):
        self.linghu = self.create_user('linghu')
        self.tweet = self.create_tweet(self.linghu, content='Jiuzhang dafa hao')

    def test_hours_to_now(self):
        # 这个用户发布一个 tweet
        # 修改 tweet 的时间往前退 10 个小时
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()  # 修改完 created_at 在 insert数据库
        # 验证当前时间和 tweet 发布时间相差 10 个小时
        self.assertEqual(self.tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.linghu, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.linghu, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        dongxie = self.create_user('dongxie')
        self.create_like(dongxie, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)
