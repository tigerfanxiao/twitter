from django.contrib import admin
from tweets.models import Tweet, TweetPhoto

@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'user',
        'content',
    )
    date_hierarchy = 'created_at'


@admin.register(TweetPhoto)
class TweetPhotoAdmin(admin.ModelAdmin):
    list_display = (
        'tweet',
        'user',
        'file',
        'status',
        'has_deleted',
        'created_at',
    )
    list_filter = ('status', 'has_deleted')
    date_hierarchy = 'created_at'