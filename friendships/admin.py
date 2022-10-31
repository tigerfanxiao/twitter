from django.contrib import admin
from friendships.models import Friendship


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ['from_user_id', 'to_user_id', 'created_at']