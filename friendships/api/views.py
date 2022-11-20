from django.contrib.auth.models import User
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from friendships.api.paginations import FriendshipPagination
from friendships.services import FriendshipService

from friendships.models import Friendship
from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerialierForCreate,
)


class FriendshipViewSet(GenericViewSet):
    # 我们希望 POST /api/friendship/1/follow 是去 follow user_id=1 的用户, 用 detail=True实现
    # 因此这里 queryset 需要是 User.objects.all()
    # 如果是 Friendship.objects.all 的话就会出现 404 Not Found
    # 因为 detail=True 的 actions 会默认先去调用 get_object() 也就是 queryset.filter(pk=1) 查询一下这个 object 在不在
    # 所以我们要把 queryset 设置为 User
    queryset = User.objects.all()

    # 如果只有 GET 方法的 action, 不需要定义 serializer_class, 但是如果有POST方法的 action, 就一定要有 serializer_class
    serializer_class = FriendshipSerialierForCreate
    # create api
    # 这是第二种控制 action 和 permission 的方法

    # 一般来说，不同的 views 所需要的 pagination 规则肯定是不同的，因此一般都需要自定义
    pagination_class = FriendshipPagination  # 引入 pagination 之后就可以在方法中调动 self.pagination
    # 这里我们写一下自定义的action, followers显示用户的粉丝
    # GET /api/friendships/1/followers/
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):  # pk 是从 url 中获取的, 类型为 str
        friendships = Friendship.objects.filter(to_user_id=pk) #因为模型中的 class Meta有 ording, 所以这里省略 .order_by('-created_at')
        # 需要一个 FollowerSerializer

        # serializer = FollowerSerializer(friendships, many=True)
        # return Response({
        #     'followers': serializer.data,
        # }, status=status.HTTP_200_OK)

        # self.paginator # 可以返回一个实例化对象
        page = self.paginate_queryset(friendships)
        serializer = FollowerSerializer(page, many=True,
                                        context={'request': request})
        return self.get_paginated_response(serializer.data)

    # 显示我关注的人
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user=pk)  #因为模型中的 class Meta有 ording, 所以这里省略 .order_by('-created_at')
        # serializer = FollowingSerializer(friendships, many=True)
        # return Response({
        #     'followings': serializer.data,
        # }, status.HTTP_200_OK)
        page = self.paginate_queryset(friendships)
        serializer = FollowingSerializer(page, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # 以pk 为 id 到 queryset 中去取
        # 如果用户不存在则返回 404 错误
        follow_user = self.get_object()

        # 检查friendship是否已经存在, 如果重复做静默处理
        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
            return Response({
                'success': True,
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)

        # 创建一个 friendship, 要把数据传给 serializer, 而不是把实例传给 serialzizer
        # 由 serializer 中的 save 函数来创建和修改数据库, 所以要写 create 方法
        serializer = FriendshipSerialierForCreate(
            data={
                "from_user_id": request.user.id,
                "to_user_id": pk,
            })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check your input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        instance = serializer.save()
        # 这种删除缓存的处理办法的缺点在于只能 api 调用时才能触发, 在 admin 里创建时就不会触发.
        # 要解决这个问题, 需要使用 listener 机制
        # FriendshipService.invalidate_following_cache(request.user.id)  # 新增数据, 清缓存
        return Response(
            FollowingSerializer(instance, context={'request': request}).data,
            status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        unfollower_user = self.get_object()  # 验证 pk 对应的 user 是否存在
        # 不能自己 unfollow 自己
        if request.user.id == unfollower_user.id:
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)

        # 返回值有 deleted: 一共删除了多少个元素
        # _ 是每种类型删了多少, 如果是 Foreignkey 设置的 cascade 级联删除, 别的 model 有相关的元素也会被删除
        # 如果在 unfollow 情况下, 做删除操作, deleted 为 0, 静默处理
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=pk,
        ).delete()
        # 可以返回 204 no content
        # FriendshipService.invalidate_following_cache(request.user.id)
        return Response({'success': True, 'deleted': deleted})

    # 只有定义了list 方法, 才能在主页看到 friendship 列出来
    def list(self, request):
        return Response({
            'message': 'This is friendship homepage'
        })

