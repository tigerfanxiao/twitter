from django.contrib.auth.models import User
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from friendships.models import Friendship


class FriendshipViewSet(GenericViewSet):
    # 我们希望 POST /api/friendship/1/follow 是去 follow user_id=1 的用户, 用 detail=True实现
    # 因此这里 queryset 需要是 User.objects.all()
    # 如果是 Friendship.objects.all 的话就会出现 404 Not Found
    # 因为 detail=True 的 actions 会默认先去调用 get_object() 也就是 queryset.filter(pk=1) 查询一下这个 object 在不在
    # 所以我们要把 queryset 设置为 User
    queryset = User.objects.all()
    # create api
    # 这是第二种控制 action 和 permission 的方法

    # 这里我们写一下自定义的action, followers
    @action(methods=['POST'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):  # pk 是从 url 中获取的, 类型为 str
        friendships = Friendship.objects.filter()

