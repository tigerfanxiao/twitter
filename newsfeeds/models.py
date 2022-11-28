from django.contrib.auth.models import User
from django.db import models
from tweets.models import Tweet
from utils.memcached_helper import MemcachedHelper
from django.db.models.signals import post_save
from newsfeeds.listeners import push_newsfeed_to_cache

class NewsFeed(models.Model):
    # 注意: 这个 user 不是谁发了这个帖子, 而是谁可以看到这个帖子
    # 这里使用 push 模型, 一个人发了一条帖子, 会给所有关注他的人创建一条 newsfeed 的记录
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # 不应该用 tweet 中的 created_at, 这样可能数据库不支持, 也很费时间

    class Meta:
        index_together = (('user', 'created_at'), )
        unique_together = (('user', 'tweet'), )
        ordering = ('-created_at', )
        # 虽然这里默认了使用ordering的排序方法, 还是建议在 viewset 中取 queryset 的时候直接指定 order_by
        # 这样对看代码的人来说, 更直观. 不需要到深入一层到 model 中才能发现排序的逻辑

    @property
    def cached_tweet(self):
        return MemcachedHelper.get_object_through_cache(Tweet, self.tweet_id)

    def __str__(self):
        return f'{self.created_at} inbox of {self.user}: {self.tweet}'


post_save.connect(push_newsfeed_to_cache, sender=NewsFeed)