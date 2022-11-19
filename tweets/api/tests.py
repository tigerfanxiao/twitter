from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from testing.testcases import TestCase
from tweets.models import Tweet, TweetPhoto


# 注意这里 url 是一样的, 只是方法不一样
TWEET_LIST_URL = '/api/tweets/'  # 用 get 方法
TWEET_CREATE_URL = '/api/tweets/'  # 用 post 方法
TWEET_RETRIEVE_API = '/api/tweets/{}/'


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
        response = self.anonymous_client.post(TWEET_CREATE_URL,
                                              {'content': '1'})
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
        response = self.user1_client.post(TWEET_CREATE_URL,
                                          {'content': '1' * 141})
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

    def test_retrieve(self):
        # tweet with id= -1 does not exist
        url = TWEET_RETRIEVE_API.format(-1)
        response = self.anonymous_client.get(url)
        # 因为在 retrieve 函数中用了 self.get_object() 如果找不到, 会抛出 404
        self.assertEqual(response.status_code, 404)

        # 获取某个 tweet 的时候会一起把 Comments 也答应出来
        tweet = self.create_tweet(self.user1)
        url = TWEET_RETRIEVE_API.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        self.create_comment(user=self.user2, tweet=tweet, content="holly s**")
        self.create_comment(self.user1, tweet, 'hmm...')
        # 确保这个请求不会返回所有的 tweet, 在写测试代码时很常见, 这是一种干扰因子
        self.create_comment(self.user1, self.create_tweet(self.user2), 'nothing')
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data['comments']), 2)

    def test_create_with_files(self):
        # 还可以做的测试: 比如上传的 data没有 files, 兼容旧的 api
        # 还可以做的测试: 从 list api 中看有没有这些图片

        # 上传空文件列表
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'a selfie',
            'files': [],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 0)

        # 上传单个文件
        # content 需要是一个 bytes 类型，所以用 str.encode 转换一下
        file = SimpleUploadedFile(
            name='selfie.jpg',
            content=str.encode('a fake image'),
            content_type='image/jpeg',
        )
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'a selfie',
            'files': [file],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 1)

        # 测试多个文件上传
        file1 = SimpleUploadedFile(
            name='selfie1.jpg',
            content=str.encode('selfie 1'),
            content_type='image/jpeg',
        )
        file2 = SimpleUploadedFile(
            name='selfie2.jpg',
            content=str.encode('selfie 2'),
            content_type='image/jpeg',
        )
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'two selfies',
            'files': [file1, file2],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 3)

        # 从读取的 API 里确保已经包含了 photo 的地址
        retrieve_url = TWEET_RETRIEVE_API.format(response.data['id'])
        response = self.user1_client.get(retrieve_url)
        self.assertEqual(len(response.data['photo_urls']), 2)
        self.assertEqual('selfie1' in response.data['photo_urls'][0], True)
        self.assertEqual('selfie2' in response.data['photo_urls'][1], True)

        # 测试上传超过 9 个文件会失败
        files = [
            SimpleUploadedFile(
                name=f'selfie{i}.jpg',
                content=str.encode(f'selfie{i}'),
                content_type='image/jpeg',
            )
            for i in range(10)
        ]
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'failed due to number of photos exceeded limit',
            'files': files,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(TweetPhoto.objects.count(), 3)
