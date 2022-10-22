from rest_framework.serializers import ModelSerializer
from accounts.api.serializers import UserSerializerForFriendship

from friendships.models import Friendship

class FollowerSerializer(ModelSerializer):
    # 需要显示 user 的详细信息
    # 这里的 source 可以从 model 中去取字段, 实际的字段名是 from_user
    user = UserSerializerForFriendship(source='from_user')

    class Meta:
        model = Friendship  # 实例化的入参
        fields = ('user', 'created_at')
        # 这里只是key 名, 默认会从Serializer的定义中取找,
        # 如果没有找到, 才会去 model Friendship 的字段中去找
    # 因为只是展示数据, 不需要校验


class FollowingSerializer(ModelSerializer):
    # TODO: Add FollowingSerializer
    user = UserSerializerForFriendship(source='to_user')
    class Meta:
        model = Friendship
        fields = ('user', 'created_at')