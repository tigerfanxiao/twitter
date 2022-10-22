from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from tweets.models import Tweet
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate


# 一般不用 ModelViewSet, 因为 ModelViewSet 默认你增删查改都可以做, 我们不打算开放这些接口
# 我们只需要 list 和 create 两个接口
class TweetViewSet(GenericViewSet):
    # 指定默认的 queryset, serializers,
    queryset = Tweet.objects.all()  # 这里可以不需要, 因为 list方法已经返回了一个 queryset
    serializer_class = TweetSerializerForCreate
    # 默认的 serializer_class django 会提供一个创建时用的表单


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
        # 这里需要在 model 中建立联合索引
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')  # 这里需要建立联合索引, 在 model 中配置
        serializer = TweetSerializer(tweets, many=True)  # 这里传入的是 querySet 指定 many=True, 说明会返回 list of dict
        return Response({
            "tweets": serializer.data,
        })  # 一般是 return 一个 dict, 不会直接 return 一个 list


    def create(self, request):
        # 提取用户提交的数据
        # 初始化一个 serializer, 传入用户输入和 request.user
        # 初始化 serializer 有基本参数, 通过data传入用户输入, 通过context传入其他参数(以键值对的方式传入)
        # data 传入的参数在 validated_data中获取, context 传入的参数在 self.context中获取
        serializer = TweetSerializerForCreate(
            data=request.data,  # 因为是 post 方法, 所以用户传入数据在 request.data中, 传入的也是键值对
            context={'request': request}
        )
        # 默认都要用 serialzier.is_valid()方法, 对数据进行验证.
        # 因为这里只是验证 content 的长度, rest_frame会帮我们做, 所以不需要重写 validate 方法
        # 在方法中如果验证失败, 返回的 VaidationError 信息会填充到 serializer.errors中
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check your input',
                # 这里返回的是一个 list, 即rest_frame帮我们验证的错误, 和我们自己重写 validate 方法返回的错误
                'errors': serializer.errors,
            }, status=400)
        # 调用 serializier.save() 把数据保存下来, 并返回创建的实例
        # 注意: 这个实例不能直接给 respose 返回, 需要序列化后才能返回
        tweet = serializer.save()
        # 返回 Response
        return Response({
            'success': True,
            'tweet': TweetSerializer(tweet).data,  # 这里我们用 TweetSerializer对实例进行序列化
        }, status=201)  # 创建成功, 返回值 201

