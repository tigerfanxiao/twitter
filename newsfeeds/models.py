from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet


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

    def __str__(self):
        return f'{self.created_at} inbox of {self.user}: {self.tweet}'
