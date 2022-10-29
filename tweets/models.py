from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from likes.models import Like
from utils.time_helpers import utc_now


class Tweet(models.Model):
    # 这里指定了 user 为 ForeignKey, django 会自己帮你建立索引, 方便你逆向查询
    user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Who post this tweet",
        # verbose_name=u"谁发了这个贴"
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)  # 只有在创建的时候插入, django会加上utc时区信息
    # updated_at = models.DateField(auto_now=True) # 每次修改都会更新

    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

    # 通过 tweet.like_set可以反查点赞
    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')


    # @property
    # def comments(self):
    #     return self.comment_set.all()


    # 在 class Meta中建立联合索引, 默认排序等
    # 如果只是给单个字段做索引, 在字段约束中加 db_index=True即可
    # 注意: 如果是后期添加的索引, 需要重新 migrate 才能生效
    class Meta:
        index_together = (('user', 'created_at'),) # 注意: 因为可能有多个联合索引, 所以是 tuple(tuple)
        ordering = ('user', '-created_at') # 默认的排序值, 不会对数据库有影响, 只影响默认的 queryset


    def __str__(self):
        return f"{self.created_at} {self.user}: {self.content}"
