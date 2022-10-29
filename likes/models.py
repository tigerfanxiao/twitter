from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # 有没有一个通用的 foreignkey 来同时记录 tweet 和 comment
    # django 提供了ContentType
    object_id = models.PositiveIntegerField()
    # https://docs.djangoproject.com/en/3.1/ref/contrib/contenttypes/#generic-relations
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True
    )
    # 制定了属性中的 content_type 和 object_id
    # 这个属性定义的目的是当你用 like.content_object是就能查到对应的表单中 comment或者 tweet
    # 这一项没有实际存储在表单中, 只是提供了一种快捷的访问方式
    # 类似 manytomany 也不是实际存储在表单中的
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        # 这里使用unique together也会加你一个 <user, content_type, object_id>
        # 的索引. 这个索引同事还具备查询 user like 了哪些不同的 object 的功能
        # 因此如果 unique together 改成 <content_type, object_id, user> 就没有这样的效果了
        # 一个用户, 在某一个 comment 和 tweet 只能点赞一次, 在数据库层面保证. 因为高并发可能会在同时创建两行
        unique_together = (('user', 'content_type', 'object_id'),)
        # 这个 index 的作用是可以按照时间排序某个被 like 的 content_object的所有 likes
        # 比如某一个 tweets 下面所有的 likes, 并排序
        index_together = (
            ('content_type', 'object_id', 'created_at'),
            # clear
        )

    def __str__(self):
        return '{} - {} likes {} {}'.format(
            self.created_at,
            self.user,
            self.content_type,
            self.content_object,
        )
