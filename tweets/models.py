from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, pre_delete
from likes.models import Like
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES
from utils.listeners import invalidate_object_cache
from utils.memcached_helper import MemcachedHelper
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
    created_at = models.DateTimeField(
        auto_now_add=True)  # 只有在创建的时候插入, django会加上utc时区信息
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

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)

    # 在 class Meta中建立联合索引, 默认排序等
    # 如果只是给单个字段做索引, 在字段约束中加 db_index=True即可
    # 注意: 如果是后期添加的索引, 需要重新 migrate 才能生效
    class Meta:
        index_together = (('user', 'created_at'),)  # 注意: 因为可能有多个联合索引, 所以是 tuple(tuple)
        ordering = ('user', '-created_at')  # 默认的排序值, 不会对数据库有影响, 只影响默认的 queryset

    def __str__(self):
        return f"{self.created_at} {self.user}: {self.content}"


class TweetPhoto(models.Model):
    # 图片在哪个 Tweet 下面
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)

    # 谁上传了这张图片，这个信息虽然可以从 tweet 中获取到，但是重复的记录在 TweetPhoto 里可以在
    # 使用上带来很多便利，比如某个人经常上传一些不合法的照片，那么这个人新上传的照片可以被标记
    # 为重点审查对象。或者我们需要封禁某个用户上传的所有照片的时候，就可以通过这个 model 快速
    # 进行筛选, 如果通过 tweet_photo.tweet.user 这两个点, 等于做了 2 次join 的查询, 保存了 user 信息就不需要做多次查询

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    # 图片文件
    file = models.FileField()
    order = models.IntegerField(default=0)  # 图片上传的顺序

    # 图片状态，用于审核等情况
    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )

    # 软删除(soft delete)标记，当一个照片被删除的时候，首先会被标记为已经被删除，在一定时间之后
    # 才会被真正的删除。这样做的目的是，如果在 tweet 被删除的时候马上执行真删除的通常会花费一定的
    # 时间，影响效率。可以用异步任务在后台慢慢做真删除。
    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 哪些查询场景
    class Meta:
        index_together = (
            ('user', 'created_at'), # 查询出某个用户发布的所有图片, 可以快速封建这个用户的所有图片
            ('has_deleted', 'created_at'), # 如果在一段时间后把文件删除, 首先要查询出已经标记为删除的图片, 然后再按照创建时间排序
            ('status', 'created_at'),   # 查询出某个文件创天, 然后再按照创建时间排序
            ('tweet', 'order'),  # 查询出某个 tweet, 然后按照上传顺序排序
        )

    def __str__(self):
        return f'{self.tweet_id}: {self.file}'


post_save.connect(invalidate_object_cache, sender=Tweet)
pre_delete.connect(invalidate_object_cache, sender=Tweet)