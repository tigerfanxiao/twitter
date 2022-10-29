from accounts.api.serializers import UserSerializerForLike
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from likes.models import Like
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet
from utils.decorators import required_params


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializerForLike()

    class Meta:
        model = Like
        fields = ('user', 'created_at')  # 为什么没有其他字段


class LikeSerializerForCreate(serializers.ModelSerializer):
    content_type = serializers.ChoiceField(choices=['comment', 'tweet'])
    object_id = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ('content_type', 'object_id')

    def _get_model_class(self, data):
        if data['content_type'] == 'comment':
            return Comment
        if data['content_type'] == 'tweet':
            return Tweet
        return None

    def validate(self, attrs):
        model_class = self._get_model_class(attrs)
        if model_class is None:
            raise ValidationError(
                {'content_type': 'Content type does not exist'})
        liked_object = model_class.objects.filter(id=attrs['object_id']).first()
        if liked_object is None:
            raise ValidationError({'object_id': 'object does not exists'})
        return attrs

    def create(self, validated_data):
        model_class = self._get_model_class(validated_data)
        instance, _ = Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=validated_data['object_id'],
            user=self.context['request'].user,
        )
        return instance
