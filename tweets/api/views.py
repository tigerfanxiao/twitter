from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from tweets.models import Tweet
from tweets.api.serializers import TweetSerializer


# 一般不用 ModelViewSet, 因为 ModelViewSet 默认你增删查改都可以做, 我们不打算开放这些接口
# 我们只需要 list 和 create 两个接口
class TweetViewSet(GenericViewSet):
    # 指定默认的 queryset, serializers,
    queryset = Tweet.objects.all()  # 这里可以不需要, 因为 list方法已经返回了一个 queryset
    serializer_class = TweetSerializer  # 默认的 serializer_class django 会提供一个创建时用的表单


    # 权限检测有两种方法
    # 方法一: 重写 get_permissions函数. 这种写法的好处时, 如果你有多个 action 但是共享同一种 permission 时可以节省代码
    # 方法二: 用 action 装饰器, 定义 permissions 参数.
    def get_permissions(self):
        if self.action == 'list':  # 通过 self.action来看请求的动作
            return [AllowAny(), ]  # 默认是 AllowAny, 即使不写也可以
        return [IsAuthenticated(), ]

    def list(self, request):
        if 'user_id' not in request.query_params:
            return Response("Missing user_id", status=400)
        # 返回指定用户所有的 tweet, 并按照 created_at 倒叙排列
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')  # 这里需要建立联合索引, 在 model 中配置
        serializer = TweetSerializer(tweets, many=True)  # 这里传入的是 querySet 指定 many=True, 说明会返回 list of dict
        return Response({
            "tweets": serializer.data,
        })  # 一般是 return 一个 dict, 不会直接 return 一个 list



    def create(self, request):
        pass
