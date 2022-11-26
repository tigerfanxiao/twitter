from testing.testcases import TestCase
from utils.redis_client import RedisClient


class UtilsTests(TestCase):

    def setUp(self):
        self.clear_cache()

    def test_redis_client(self):
        conn = RedisClient.get_connection()
        conn.lpush('redis_key', 1)  # 在一个列表名为 redis_key 中的插入元素
        conn.lpush('redis_key', 2)
        cached_list = conn.lrange('redis_key', 0, -1)  # 从下标0 到下标-1 的数都取出来(左右都包含)
        self.assertEqual(cached_list, [b'2', b'1'])  # 存储的方式是新的数据在左侧 left, 同时可以看到是用字节流的方式存储的

        RedisClient.clear()
        cached_list = conn.lrange('redis_key', 0, -1)
        self.assertEqual(cached_list, [])