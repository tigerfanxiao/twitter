from rest_framework import serializers
from accounts.api.serializers import UserSerializerForComment
from rest_framework.exceptions import ValidationError
from comments.models import Comment
from tweets.models import Tweet


class CommentSerializerForCreate(serializers.ModelSerializer):
    # 对 tweet_id 做限制是因为默认是把 tweet 对象付给 tweet
    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    # 这里不需要对 content 做限制, 因为在模型定义中已经做了

    class Meta:
        model = Comment
        fields = ("content", "tweet_id", "user_id")

    def validate(self, attrs):
        tweet_id = attrs["tweet_id"]
        if not Tweet.objects.filter(id=tweet_id).exists():
            raise ValidationError({
                'message': 'tweet does not exists.'
            })

        return attrs


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializerForComment()

    class Meta:
        model = Comment
        fields = (
            "id",
            "tweet_id",
            "user",
            "content",
            "created_at",
            "updated_at",
        )