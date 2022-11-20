from comments.models import Comment
from django.utils import timezone
from rest_framework.test import APIClient
from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'
COMMENT_DETAIL_URL = '/api/comments/{}/'
TWEET_LIST_API = '/api/tweets/'  # 用户发了多少 tweet
TWEET_DETAIL_API = '/api/tweets/{}/'  # 某个具体的 tweet
NEWSFEED_LIST_API = '/api/newsfeeds/'  # 每个用户关注的人发的 tweet


class CommentApiTests(TestCase):
    def setUp(self):
        self.clear_cache()
        self.linghu = self.create_user('linghu')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)

        self.dongxie = self.create_user('dongxie')
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

        # linghu create tweet
        self.tweet = self.create_tweet(self.linghu)

    def test_list(self):
        # 必须带 tweet_id
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, 400)
        # 带了 tweet_id可以访问
        # 一开始没有评论
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)
        # 评论按照时间排序
        self.create_comment(self.linghu, self.tweet, '1')
        self.create_comment(self.dongxie, self.tweet, '2')
        self.create_comment(self.dongxie, self.create_tweet(self.dongxie), '3')
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id
        })

        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(response.data['comments'][0]['content'], "1")
        self.assertEqual(response.data['comments'][1]['content'], "2")

        # 同时提供 user_id和 tweet_id 只有 tweet_id 会在 filger 中生效
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'user_id': self.linghu.id,
        })
        self.assertEqual(len(response.data['comments']), 2)

    def test_create(self):
        # 匿名不可以创建
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # 啥参数都没带不行
        response = self.linghu_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # 只带 tweet_id不行
        response = self.linghu_client.post(
            COMMENT_URL,
            data={"tweet_id": self.tweet.id},
        )
        self.assertEqual(response.status_code, 400)

        # 只带 content 不行
        response = self.linghu_client.post(
            COMMENT_URL,
            data={"content": "ok"}
        )
        self.assertEqual(response.status_code, 400)

        # content太长不行
        response = self.linghu_client.post(
            COMMENT_URL,
            data={
                "tweet_id": self.tweet.id,
                "content": "1"*141
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # 正常发 comment
        response = self.linghu_client.post(
            COMMENT_URL,
            data={
                "tweet_id": self.tweet.id,
                "content": "1",
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.linghu.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], "1")

    def test_update(self):
        comment = self.create_comment(self.linghu, self.tweet, 'original')
        another_tweet = self.create_tweet(self.dongxie)
        url = COMMENT_DETAIL_URL.format(comment.id)

        # 适应 put 情况下
        # 匿名不能更新
        response = self.anonymous_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        # 非本人不能更新
        response = self.dongxie_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')
        # 不能更新÷content 之外的的内容, 静默处理, 只更新内容
        before_updated_at = comment.updated_at # 在修改数据之前, 保存一下状态
        before_created_at = comment.created_at
        now = timezone.now()  # 获取当地时区的时间, 原来数据保存的是 utc 时区的
        response = self.linghu_client.put(url, {
            'content': 'new',
            'user_id': self.dongxie.id,
            'tweet_id': another_tweet.id,
            'created_at': now,
        })  # 这里会修改数据库中的数据
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()  # 使获得修改后的数据
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.linghu)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)  # 创建时间不能被更新
        self.assertNotEqual(comment.updated_at, before_updated_at) # 修改时间被更新了





    def test_destroy(self):
        comment = self.create_comment(
            user=self.linghu,
            tweet=self.tweet
        )
        url = COMMENT_DETAIL_URL.format(comment.id)
        # 匿名不可以删除
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)
        # 非本人不能删除
        response = self.dongxie_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # 本人可以删除
        count = Comment.objects.count()
        response = self.linghu_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_comments_count(self):
        # test tweet detail api
        tweet = self.create_tweet(self.linghu)
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.dongxie_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments_count'], 0)  # 创建一个 tweet 时没有 comment

        # test tweet list api
        self.create_comment(self.linghu, tweet)  # linghu添加一个 comment
        response = self.dongxie_client.get(TWEET_LIST_API,
                                           {'user_id': self.linghu.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['comments_count'], 1)

        # test newsfeeds list api
        self.create_comment(self.dongxie, tweet)   # 东邪添加一个评论
        self.create_newsfeed(self.dongxie, tweet)  # 东邪订阅一个 newsfeed
        response = self.dongxie_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['results'][0]['tweet']['comments_count'], 2)  # 一共有两个评论
