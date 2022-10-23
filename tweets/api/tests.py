from rest_framework.test import APIClient
from testing.testcases import TestCase
from tweets.models import Tweet

# 注意这里 url 是一样的, 只是方法不一样
TWEET_LIST_URL = '/api/tweets/'  # 用 get 方法
TWEET_CREATE_URL = '/api/tweets/'  # 用 post 方法

class TweetApiTests(TestCase):

    def setUp(self):
        # 一般测试都要有匿名用户和登录用户

        # 登录用户就需要创建用户, 并登录
        self.user1 = self.create_user('user1')
        # 使用 force_authenticate方法, 确保用户登录

        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)
        # 给这个用户创建 tweet, 目的是尽量模拟一个真实的环境, 已经有 tweet 基础上, 创建新 tweet 会增加 tweet 总数
        self.tweets1 = [self.create_tweet(
            user=self.user1,
        ) for i in range(3)]

        # 创建第二个用户的目的是检查按照用户名和倒叙排序
        self.user2 = self.create_user('user2')
        # 使用 force_authenticate方法, 确保用户登录
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)
        # 给这个用户创建 tweet
        self.tweets2 = [self.create_tweet(
            user=self.user2,
        ) for i in range(2)]  # 注意: 两个用户 tweets 的数量最好区分开, 好辨识


    def test_list_api(self):
        # 不带参数访问
        response = self.anonymous_client.get(TWEET_LIST_URL)  # 使用 get 方法
        self.assertEqual(response.status_code, 400)

        # 正常访问 GET 和 参数用字典传入
        response = self.anonymous_client.get(
            path=TWEET_LIST_URL,
            data={'user_id': self.user1.id},
        )
        self.assertEqual(len(response.data['tweets']), 3)  # user1有三条 tweet

        response = self.anonymous_client.get(
            path=TWEET_LIST_URL,
            data={'user_id': self.user2.id},
        )
        self.assertEqual(len(response.data['tweets']), 2)
        # 检查排序: 时间倒叙
        # 注意 response 里的内容都是要通过字典的方式来访问的, self.tweets2 是通过对象的方式来访问的
        self.assertEqual(response.data['tweets'][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data['tweets'][1]['id'], self.tweets2[0].id)


    def test_create_api(self):
        # 匿名创建
        response = self.anonymous_client.post(TWEET_CREATE_URL, {'content': '1'})
        self.assertEqual(response.status_code, 403)

        # 必须带 content
        response = self.user1_client.post(TWEET_CREATE_URL)
        self.assertEqual(response.status_code, 400)

        # 验证数据有效性
        # content不能太短
        response = self.user1_client.post(TWEET_CREATE_URL, {'content': '1'})
        # print(response.status_code) 可以打印调试
        self.assertEqual(response.status_code, 400)
        # content 不能太长
        response = self.user1_client.post(TWEET_CREATE_URL, {'content': '1'*141})
        self.assertEqual(response.status_code, 400)
        # 正常创建
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(
            TWEET_CREATE_URL,
            {'content': 'Hello this is my first tweet'}
        )
        self.assertEqual(response.status_code, 201)
        # print(response.data)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)
        # 检查创建前后数量增加 1