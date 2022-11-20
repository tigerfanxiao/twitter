from notifications.models import Notification
from testing.testcases import TestCase


COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'
NOTIFICATION_URL = '/api/notifications/'

class NotificationTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.linghu, self.linghu_client = self.create_user_and_client('linghu')
        self.dongxie, self.dongxie_client = self.create_user_and_client('dong')
        self.dongxie_tweet = self.create_tweet(self.dongxie)

    def test_comment_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)  # 最初通知为 0
        self.linghu_client.post(COMMENT_URL, {
            'tweet_id': self.dongxie_tweet.id,
            'content': 'a ha',
        })
        self.assertEqual(Notification.objects.count(), 1)  # 评价一个 tweet 后, 通知为 1

    def test_like_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.linghu_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.dongxie_tweet.id,
        })
        self.assertEqual(Notification.objects.count(), 1)  # 点赞一个帖子后, 通知为 1


class NotificationApiTests(TestCase):

    def setUp(self):
        self.linghu, self.linghu_client = self.create_user_and_client('linghu')
        self.dongxie, self.dongxie_client = self.create_user_and_client('dongxie')
        self.linghu_tweet = self.create_tweet(self.linghu)

    def test_unread_count(self):
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.linghu_tweet.id,
        })

        url = '/api/notifications/unread-count/'
        response = self.linghu_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

        comment = self.create_comment(self.linghu, self.linghu_tweet)
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        response = self.linghu_client.get(url)
        self.assertEqual(response.data['unread_count'], 2)
        response = self.dongxie_client.get(url)
        self.assertEqual(response.data['unread_count'], 0)  # dongxie是看不到的, 保证是按照用户 filter 的


    def test_mark_all_as_read(self):
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.linghu_tweet.id,
        })
        comment = self.create_comment(self.linghu, self.linghu_tweet)
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        unread_url = '/api/notifications/unread-count/'
        response = self.linghu_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        mark_url = '/api/notifications/mark-all-as-read/'
        # dongxie can not mark linghu's notification as read
        response = self.dongxie_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 0)
        # linghu can mark his notification as read
        response = self.linghu_client.get(mark_url)
        self.assertEqual(response.status_code, 405)
        response = self.linghu_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 2)
        response = self.linghu_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_list(self):
        # dongxie 对 linghu 的 tweet 点赞
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.linghu_tweet.id,
        })
        # linghu 对自己的 tweet 有一个评价
        # dongxie 对 linghu 的评价点赞
        comment = self.create_comment(self.linghu, self.linghu_tweet)
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        # 匿名用户无法访问 api
        response = self.anonymous_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 403)
        # dongxie 看不到任何 notifications
        response = self.dongxie_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)

        # 这里的返回值是 pagenization 过得
        # ([('count', 0), ('next', None), ('previous', None), ('results', [])])
        self.assertEqual(response.data['count'], 0)
        # linghu 看到两个 notifications
        response = self.linghu_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data['count'], 2)
        # 标记之后看到一个未读
        notification = self.linghu.notifications.first()
        notification.unread = False # 把第一个通知改为已读
        notification.save()
        response = self.linghu_client.get(NOTIFICATION_URL)
        self.assertEqual(response.data['count'], 2)
        # 查询未读的
        # listModelMixin里面是支持删选机制的
        # 在 view 中用 filterset_fields = ('unread',)  配置了筛选
        response = self.linghu_client.get(NOTIFICATION_URL, {'unread': True})
        self.assertEqual(response.data['count'], 1)
        # 查询已读的
        response = self.linghu_client.get(NOTIFICATION_URL, {'unread': False})
        self.assertEqual(response.data['count'], 1)

    def test_update(self):
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.linghu_tweet.id,
        })
        comment = self.create_comment(self.linghu, self.linghu_tweet)
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        notification = self.linghu.notifications.first()

        url = '/api/notifications/{}/'.format(notification.id)
        # post 不行，需要用 put
        response = self.dongxie_client.post(url, {'unread': False})
        self.assertEqual(response.status_code, 405)
        # 不可以被其他人改变 notification 状态
        response = self.anonymous_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 403)
        # 因为 queryset 是按照当前登陆用户来，所以会返回 404 而不是 403
        # 在 get_queryset中 filter 了 recipient, 如果不是当前用户, get_queryset找不到这个 notification 就是返回 404
        response = self.dongxie_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 404)
        # 成功标记为已读
        response = self.linghu_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 200)
        unread_url = '/api/notifications/unread-count/'
        response = self.linghu_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 1)

        # 再标记为未读
        response = self.linghu_client.put(url, {'unread': True})
        response = self.linghu_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)
        # 必须带 unread
        response = self.linghu_client.put(url, {'verb': 'newverb'})
        self.assertEqual(response.status_code, 400)
        # 不可修改其他的信息
        response = self.linghu_client.put(url,
                                          {'verb': 'newverb', 'unread': False})
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertNotEqual(notification.verb, 'newverb')