from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed
from utils.paginations import EndlessPagination
from newsfeeds.services import NewsFeedServices

class NewsFeedViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    # def get_queryset(self):
    #     # 自定义 queryset，因为 newsfeed 的查看是有权限的
    #     # 只能看 user=当前登录用户的 newsfeed
    #     # 也可以是 self.request.user.newsfeed_set.all()
    #     # 但是一般最好还是按照 NewsFeed.objects.filter 的方式写，更清晰直观
    #     return NewsFeed.objects.filter(
    #         user=self.request.user,
    #     ).order_by('-created_at')

    def list(self, request):  # list 默认是 GET 方法, 不需要特殊定义action
        # queryset = self.paginate_queryset(self.get_queryset())
        newsfeeds = NewsFeedServices.get_cached_newsfeeds(request.user.id)
        page = self.paginate_queryset(newsfeeds)
        serializer = NewsFeedSerializer(
            page,
            context={'request': request},
            many=True)
        return self.get_paginated_response(serializer.data)
