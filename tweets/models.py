from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now


class Tweet(models.Model):
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

    def __str__(self):
        return f"{self.created_at} {self.user}: {self.content}"
