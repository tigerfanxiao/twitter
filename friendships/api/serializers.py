from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from accounts.api.serializers import UserSerializerForFriendship
from friendships.services import FriendshipService
from friendships.models import Friendship


class FollowingUserIdSetMixin:

    @property
    def following_user_id_set(self: serializers.ModelSerializer):
        if self.context['request'].user.is_anonymous:
            return {}
        if hasattr(self, '_cached_following_user_id_set'):
            return self._cached_following_user_id_set
        user_id_set = FriendshipService.get_following_user_id_set(
            self.context['request'].user.id,
        )
        setattr(self, '_cached_following_user_id_set', user_id_set)
        return user_id_set


class FollowerSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    # 需要显示 user 的详细信息
    # 这里的 source 可以从 model 中去取字段, 实际的字段名是 from_user
    user = UserSerializerForFriendship(source='from_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship  # 实例化的入参
        fields = ('user', 'created_at', 'has_followed')
        # 这里只是key 名, 默认会从Serializer的定义中取找,
        # 如果没有找到, 才会去 model Friendship 的字段中去找
    # 因为只是展示数据, 不需要校验

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False

        # TODO: 这里对每一个好友列表中的人都做了一次查询, 后续需要优化
        # return FriendshipService.has_followed(self.context['request'].user, obj.from_user)
        return obj.from_user_id in self.following_user_id_set

class FollowingSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    user = UserSerializerForFriendship(source='to_user')
    created_at = serializers.DateTimeField()
    has_followed = serializers.SerializerMethodField()
    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False

        # # <TODO> 这个部分会对每个 object 都去执行一次 SQL 查询，速度会很慢，如何优化呢？
        # # 我们将在后序的课程中解决这个问题
        # return FriendshipService.has_followed(self.context['request'].user,
        #                                       obj.to_user)
        return obj.to_user_id in self.following_user_id_set

class FriendshipSerialierForCreate(serializers.ModelSerializer):
    # 需要检测 to_user是否存在
    # 不能重复 follow, 已经有了 unique_together约束
    # 不能和自己建立 friendship 关系
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

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

