from django.contrib.auth.models import User
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


from friendships.models import Friendship
from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
)
class FriendshipViewSet(GenericViewSet):
    # 我们希望 POST /api/friendship/1/follow 是去 follow user_id=1 的用户, 用 detail=True实现
    # 因此这里 queryset 需要是 User.objects.all()
    # 如果是 Friendship.objects.all 的话就会出现 404 Not Found
    # 因为 detail=True 的 actions 会默认先去调用 get_object() 也就是 queryset.filter(pk=1) 查询一下这个 object 在不在
    # 所以我们要把 queryset 设置为 User
    queryset = User.objects.all()
    # 如果只有 GET 方法的 action, 不需要定义 serializer_class, 但是如果有POST方法的 action, 就一定要有 serializer_class
    # create api
    # 这是第二种控制 action 和 permission 的方法

    # 这里我们写一下自定义的action, followers显示用户的粉丝
    # GET /api/friendships/1/followers/
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):  # pk 是从 url 中获取的, 类型为 str
        friendships = Friendship.objects.filter(to_user=pk).order_by('-created_at')
        # 需要一个 FollowerSerializer
        serializer = FollowerSerializer(friendships, many=True)
        return Response({
            'followers': serializer.data,
        }, status=status.HTTP_200_OK)

    # 显示我关注的人
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user=pk).order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)
        return Response({
            'followings': serializer.data,
        }, status.HTTP_200_OK)

    # 只有定义了list 方法, 才能在主页看到 friendship 列出来
    def list(self, request):
        return Response({
            'message': 'This is friendship homepage'
        })
