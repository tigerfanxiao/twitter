from rest_framework.serializers import ModelSerializer
from accounts.api.serializers import UserSerializerForTweet
from tweets.models import Tweet


class TweetSerializer(ModelSerializer):
    # 如果不写, 则默认返回 user_id, 不是一个 user 对象
    # 如果我对于 UserSerializer返回的字段不满意, 比如不想暴露太多的信息, 可以重新定义一个专门的 Serializer
    user = UserSerializerForTweet()

    class Meta:
        # 如果使用 ModelSerializer 就要指定 Meta
        # 在 Meta 中要指定 Model, 接受那种instance
        model = Tweet
        # 在 Meta 中指定这个 model 的哪些 field 返回
        # 如果需要 user 对象深层的信息, 就要指定 user 的 serialier
        fields = ('id', 'user', 'created_at', 'content')

    #



class TweetSerializerForCreate():
    pass