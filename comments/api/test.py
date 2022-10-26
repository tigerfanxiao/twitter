from rest_framework.test import APIClient
from testing.testcases import TestCase

COMMENT_CREATE_URL = '/api/comments/'


class CommentApiTests(TestCase):
    def setUp(self):
        self.linghu = self.create_user('linghu')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)

        self.dongxie = self.create_user('dongxie')
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

        # linghu create tweet
        self.tweet = self.create_tweet(self.linghu)

    def test_create(self):
        # 匿名不可以创建
        response = self.anonymous_client.post(COMMENT_CREATE_URL)
        self.assertEqual(response.status_code, 403)

        # 啥参数都没带不行
        response = self.linghu_client.post(COMMENT_CREATE_URL)
        self.assertEqual(response.status_code, 400)

        # 只带 tweet_id不行
        response = self.linghu_client.post(
            COMMENT_CREATE_URL,
            data={"tweet_id": self.tweet.id},
        )
        self.assertEqual(response.status_code, 400)

        # 只带 content 不行
        response = self.linghu_client.post(
            COMMENT_CREATE_URL,
            data={"content": "ok"}
        )
        self.assertEqual(response.status_code, 400)

        # content太长不行
        response = self.linghu_client.post(
            COMMENT_CREATE_URL,
            data={
                "tweet_id": self.tweet.id,
                "content": "1"*141
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # 正常发 comment
        response = self.linghu_client.post(
            COMMENT_CREATE_URL,
            data={
                "tweet_id": self.tweet.id,
                "content": "1",
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.linghu.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], "1")
