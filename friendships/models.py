from django.db import models
from django.contrib.auth.models import User


class Friendship(models.Model):
    # 定义字段
    from_user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        # 逆向查询的时候的 queryset = user.following_friendship_set
        # 查询到我专注的所有人
        related_name="following_friendship_set"
    )
    to_user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="follower_friendship_set"  # 查询到关注我的所有人
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 这里是写联合索引的地方
        index_together = (
            ('from_user_id', 'created_at'),  # 获取我关注的所有人, 按照时间倒叙
            ('to_user_id', 'created_at'),    # 获取关注我的所有人, 按照时间排序
        )
        unique_together = (
            ('from_user_id', 'to_user_id'),
        )  # 不同重复关注
        ordering = ('-created_at', )  # 加在所有的查询后面, 除非你制定了 order_by

    def __str__(self):
        return f'{self.from_user.id} followed {self.to_user.id}'
