from django.contrib import admin
from likes.models import Like


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'user',
        'content_type',
        'object_id',
        'content_object',
        'created_at'
    )
    list_filter = ('content_type',)   # 这里提供了comment 和 tweet 的筛选功能
