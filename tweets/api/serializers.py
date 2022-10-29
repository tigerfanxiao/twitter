from rest_framework import serializers
from accounts.api.serializers import UserSerializerForTweet
from tweets.models import Tweet
from comments.api.serializers import CommentSerializer


# 这个 Serializer 是用来做展示的. 基本上每个 action 都需要创建一个 Serialzier.
class TweetSerializer(serializers.ModelSerializer):
    # 如果不写, 则默认返回 user_id, 不是一个 user 对象
    # 如果我对于 UserSerializer返回的字段不满意, 比如不想暴露太多的信息, 可以重新定义一个专门的 Serializer
    # 这里没有定义 id, created_at, content字段是因为这里是展示用, rest_framework会替我们做, 也无需对字段加限制条件做检验
    user = UserSerializerForTweet()

    class Meta:
        # 如果使用 ModelSerializer 就要指定 Meta
        # 在 Meta 中要指定 Model, 接受那种instance
        model = Tweet
        # 在 Meta 中指定这个 model 的哪些 field 返回
        # 如果需要 user 对象深层的信息, 就要指定 user 的 serialier
        fields = ('id', 'user', 'created_at', 'content')

class TweetSerializerWithComments(TweetSerializer):
    # 这里要获取到 comments
    # 首次会在 tweet的model 里去找, 接着会到 TweetSerializer 中去找
    comments = CommentSerializer(source='comment_set', many=True)

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content', 'comments')

    # 也可实现 serializerMethodField 方式来实现
    # comments = serializers.SerializerMethodField()
    # def get_comments(self, obj):
    #     return CommentSerializer(obj.comment_set.all(), many=True).data


# 如果有获取用户的输入, 比如创建这个动作, 就需要创建一个新的Serializer, 带有校验功能
class TweetSerializerForCreate(serializers.ModelSerializer):
    # 这里需要对字段做限制条件140字符. 所以要自己定义
    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model = Tweet
        # 用户只需要输入内容, 因为用户名是从 request.user 中获取, created_at, id都是自动添加的
        fields = ('content', )

    # 重写 create 函数, 在调用.save 方法修改数据库是会用到
    # .save的工作机制是: 如果传入 Serializer 的是一个 instance 就会调用 update 方法, 如果是一个数据就调用 create 方法
    # create 函数原型定义中, 就要获得validated_data, 然后返回一个 Model 的实例

    def create(self, validated_data):
        # 如果我们需要创建一个 tweet, 需要 user, content, created_at
        # 因为 user 在 request 中, 所以我们要从 request 获取到,
        # 说以在实例化 serializer 时, 我们通过 context 把 request 和用户输入一起传入
        return Tweet.objects.create(
            user=self.context['request'].user,
            content=validated_data['content']
        )

    # 因为有用户数据输入, 就需要重写 validata 方法来校验
    # validate方法默认获取 attrs 参数, 然后将校验后的参数返回
    # content的长度, 因为已经配置过 rest_framework会帮我校验, 所以我们不需要自己写
