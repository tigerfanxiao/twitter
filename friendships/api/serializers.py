from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import IntegerField
from rest_framework.exceptions import ValidationError
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
    user = UserSerializerForFriendship(source='to_user')
    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


class FriendshipSerialierForCreate(ModelSerializer):
    # 需要检测 to_user是否存在
    # 不能重复 follow, 已经有了 unique_together约束
    # 不能和自己建立 friendship 关系
    from_user_id = IntegerField()
    to_user_id = IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        # 不能关注自己
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'from_user_id and to_user_id should be different'
            })

        if Friendship.objects.filter(
            from_user_id=attrs['from_user_id'],
            to_user_id=attrs['to_user_id'],
        ).exists():
            raise ValidationError({
                'message': 'You has already followed this user.'
            })
        return attrs

    def create(self, validated_data):
        return Friendship.objects.create(
            # 注意: 这里不能用from_user作为参数, 因为这只能接受一个对象
            # 需要用 from_user_id作为参数
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id'],
        )

