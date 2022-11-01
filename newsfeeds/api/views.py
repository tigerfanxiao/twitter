from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed


class NewsFeedViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 自定义 queryset，因为 newsfeed 的查看是有权限的
        # 只能看 user=当前登录用户的 newsfeed
        # 也可以是 self.request.user.newsfeed_set.all()
        # 但是一般最好还是按照 NewsFeed.objects.filter 的方式写，更清晰直观
        return NewsFeed.objects.filter(
            user=self.request.user,
        ).order_by('-created_at')

    def list(self, request):  # list 默认是 GET 方法, 不需要特殊定义action
        serializer = NewsFeedSerializer(
            self.get_queryset(),
            context={'request': request},
            many=True)
        return Response({
            'newsfeeds': serializer.data,
        }, status=status.HTTP_200_OK)
