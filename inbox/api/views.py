from django_filters.rest_framework import DjangoFilterBackend
from inbox.api.serializers import (
    NotificationSerializer,
    NotificationSerializerForUpdate,
)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utils.decorators import required_params
from notifications.models import Notification


class NotificationViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,  # 这个 mixin 中实现了一个 list 方法, 不用我们字节写了
):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('unread',)  # 这里配置了筛选机制

    def get_queryset(self):
        # 还有一种写法是引入 Notification model, 然后 filter user, 但是要配置 AUTH_USER_MODEL
        # 如果在 settings 中没有配置 AUTH_USER_MODEL, django默认是情况下会使用django.contrib.auth.model.User
        # 查看 Notification model 还会看到这个第三方库中的 model 中定义时有foreign_key on_delete=CACADE, 这个是个不好的地方
        # self.request.user.notifications.all() # 这里利用了 django 的反查机制
        return Notification.objects.filter(recipient=self.request.user)

    # 这里 url_path 可以指定 url 的样式, 因为 url 中的潜规则是不用下划线
    # /api/notifications/unread-count
    @action(methods=['GET'], detail=False, url_path='unread-count')
    def unread_count(self, request, *args, **kwargs):
        # 如果代码量多, 可以不用 self.get_queryset() 因为可能超过一屏, 阅读时需要跳转查看
        # Notification.objects.filter(
        #     recipient=self.request.user,
        #     unread=True,
        # ).count()
        count = self.get_queryset().filter(unread=True).count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)


    @action(methods=['POST'], detail=False, url_path='mark-all-as-read')
    def mark_all_as_read(self, request, *args, **kwargs):
        updated_count = self.get_queryset().update(unread=False) # 在 Notification中已经对 recipient 和 unread 进行了索引
        return Response({'marked_count': updated_count}, status=status.HTTP_200_OK)

    @required_params(method='PUT', params=['unread'])
    def update(self, request, *args, **kwargs):
        """
        用户可以标记一个 notification 为已读或者未读。标记已读和未读都是对 notification
        的一次更新操作，所以直接重载 update 的方法来实现。另外一种实现方法是用一个专属的 action：
            @action(methods=['POST'], detail=True, url_path='mark-as-read')
            def mark_as_read(self, request, *args, **kwargs):
                ...
            @action(methods=['POST'], detail=True, url_path='mark-as-unread')
            def mark_as_unread(self, request, *args, **kwargs):
                ...
        两种方法都可以，我更偏好重载 update，因为更通用更 rest 一些, 而且 mark as unread 和
        mark as read 可以公用一套逻辑。
        """
        serializer = NotificationSerializerForUpdate(
            instance=self.get_object(), # update用的 serializer 是必须要传 instance, 才能在 save 是调用 update
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        notification = serializer.save()  # 会调用 serializer 中 update 的方法
        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK,
        )