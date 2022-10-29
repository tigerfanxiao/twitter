from comments.api.permissions import IsObjectOwner
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


class CommentsViewSet(viewsets.GenericViewSet):
    """
    只实现 list, create, update, destroy方法
    """
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]

        if self.action in ["destroy", 'update']:
            # 这里顺序有必要的, 先检测登录, 然后再检测 owner
            return [IsAuthenticated(), IsObjectOwner()]  # 其中 IsObjectOwner 是自定义的 permissions
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        data = {
            "user_id": request.user.id,
            "tweet_id": request.data.get("tweet_id"),
            "content": request.data.get("content"),
        }

        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                "message": "Please check your input",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        instance = serializer.save()
        return Response(
            CommentSerializer(instance).data,
            status=status.HTTP_201_CREATED)

    # 一般来说谁部分更新不用 partial_update虽然 resf_frame提供了这个方法, 因为前端会多增加一个逻辑
    def update(self, request, *args, **kwargs):
        # 这里自带的 self.get_object()根据 pk 值查询对象, 同时对 pk 值也会做检测
        # 如果是更新一个对象, serializer 中指定传入一个 instance, 会调用 serializer中的 update 方法(需要重写)
        # 如果传入 data, 则会调用 serializer 中的 create 方法
        serializer = CommentSerializerForUpdate(
            instance=self.get_object(),  # 取出数据库里的值
            data=request.data,  # 接收要新的参数
        )
        # 因为有用户输入, 所以对这个 serializer 做校验
        if not serializer.is_valid():
            return Response({
                'message': "Please check input",
            }, status=status.HTTP_400_BAD_REQUEST)
        comment = serializer.save()  # 刷新数据库
        return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs): # 这里必须要要加*args, 否则无法传递 pk 值
        comment = self.get_object()
        comment.delete()
        # DRF里默认 destroy 返回 status_code = 204 no contet
        # 这里 return 了 success=True 更直观的让前端去做判断, 所以 return 200 更合适
        return Response({'success': True}, status=status.HTTP_200_OK)