from rest_framework.serializers import ModelSerializer

from tweets.api.serializers import TweetSerializer
from newsfeeds.models import NewsFeed


class NewsFeedSerializer(ModelSerializer):
    # 如果这里不加这个, 会默认显示 tweet 的 id
    # 如果在NewsFeedSerializer 里面传入 context会向下传递到 TweetSerializer
    tweet = TweetSerializer(source='cached_tweet')

    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'tweet', )