from django.conf import settings
from django.core.cache import caches
from friendships.models import Friendship
from twitter.cache import FOLLOWINGS_PATTERN


# 如果是想访问 default cache, 可以只引入 from django.core.cache import cache
cache = caches['testing'] if settings.TESTING else caches['default']

class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        # 错误的写法一
        # 这种写法会导致 N + 1 Queries 的问题
        # 即，filter 出所有 friendships 耗费了一次 Query
        # 而 for 循环每个 friendship 取 from_user 又耗费了 N 次 Queries
        # 注意: .from_user和.from_user_id不同, .from_user会反向查询, from_user_id不会, 因为本来就在表中
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]

        # 错误的写法二
        # 这种写法是使用了 JOIN 操作，让 friendship table 和 user table 在 from_user
        # 这个属性上 join 了起来。join 操作在大规模用户的 web 场景下是禁用的，因为非常慢。
        # friendships = Friendship.objects.filter(
        #     to_user=user
        # ).select_related('from_user')
        # return [friendship.from_user for friendship in friendships]

        # 正确的写法一，自己手动 filter id，使用 IN Query 查询, 指产生一个 query, 而不是 n 个 round-trip query
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids)  # 这是一个 in 语句的 query

        # 正确的写法二，使用 prefetch_related，会自动执行成两条语句，用 In Query 查询
        # 实际执行的 SQL 查询和上面是一样的，一共两条 SQL Queries
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]

    # 当我去关注别人的好友列表式, 我可以看到我对他的好友是否关注了, 或者可以取关
    @classmethod
    def has_followed(cls, from_user, to_user):
        return Friendship.objects.filter(
            from_user=from_user,
            to_user=to_user,
        ).exists()

    @classmethod
    def get_following_user_id_set(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        user_id_set = cache.get(key)  # 在 get 时, django 也会进行发序列化, 返回一个 set
        if user_id_set is not None:
            return user_id_set

        friendships = Friendship.objects.filter(from_user_id=from_user_id)
        user_id_set = set([
            fs.to_user_id
            for fs in friendships
        ])
        cache.set(key, user_id_set)  # 本质上 memcached 中 key 和 value 都是字符串
        # 在调用 set 方法时, django 会对集合做处理, 将集合序列化成为一个字符串
        return user_id_set

    # 删除 key 的操作
    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        cache.delete(key)