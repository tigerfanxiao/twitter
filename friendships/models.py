from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from accounts.services import UserService
# 在 save 之后, 和删除之前
# 因为是在创建和删除 Freindship 都会触发删除缓存的操作, 所以用 django 的 signal 机制在 model 层面来处理这个问题
from friendships.listeners import friendship_changed


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

    @property
    def cached_from_user(self):
        return UserService.get_user_through_cache(self.from_user_id)

    @property
    def cached_to_user(self):
        return UserService.get_user_through_cache(self.to_user_id)

    def __str__(self):
        return f'{self.from_user.id} followed {self.to_user.id}'


# hook up with listeners to invalidate cache
pre_delete.connect(friendship_changed, sender=Friendship)
# save是在修改和创建的时候都会触发
post_save.connect(friendship_changed, sender=Friendship)