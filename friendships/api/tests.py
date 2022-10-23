from testing.testcases import TestCase
from rest_framework.test import APIClient
from friendships.models import Friendship


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'

class FriendshipApiTests(TestCase):

    def setUp(self):
        self.anonymous_client = APIClient()

        self.linghu = self.create_user('linghu')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)

        self.dongxie = self.create_user('dongxie')
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

        # create followers and followings for dongxie
        for i in range(2):
            follower = self.create_user('dongxie_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.dongxie)

        for i in range(3):
            following = self.create_user('dongxie_following{}'.format(i))
            Friendship.objects.create(from_user=self.dongxie, to_user=following)


    def test_follow(self):
        # 需要登录才能follow
        url = FOLLOW_URL.format(self.linghu.id)
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # 用 get 来 follow
        response = self.dongxie_client.get(url)
        self.assertEqual(response.status_code, 405)

        # 不可以 follow自己
        response = self.linghu_client.post(url)
        self.assertEqual(response.status_code, 400)
        # follow 成功
        respoonse = self.dongxie_client.post(url)
        self.assertEqual(respoonse.status_code, 201)
        # 重复 follow 静默成功
        response = self.dongxie_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'], True)

        # 反向关注会创建新的数据
        count = Friendship.objects.count()
        response = self.linghu_client.post(FOLLOW_URL.format(self.dongxie.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.linghu.id)
        # 需要登录才能 unfollow
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # 不用 get 来unfollow
        response = self.dongxie_client.get(url)
        self.assertEqual(response.status_code, 405)

        # 不能 unfollow 自己
        response = self.linghu_client.post(url)
        self.assertEqual(response.status_code, 400)

        # unfollow成功
        # 先构建一个 friendship
        friendship = Friendship.objects.create(
            from_user=self.dongxie,
            to_user=self.linghu,
        )
        count = Friendship.objects.count()
        response = self.dongxie_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        # 未 follow 情况下做 unfollow 做静默处理
        count = Friendship.objects.count()
        response = self.dongxie_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.dongxie.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)
        # 降序排列
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        print(ts0)
        print(ts1)
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'dongxie_following2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'dongxie_following1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'dongxie_following0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.dongxie.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)
        # 降序排列
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'dongxie_follower1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'dongxie_follower0',
        )


