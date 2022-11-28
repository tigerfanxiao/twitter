from tweets.models import TweetPhoto
from tweets.models import Tweet
from twitter.cache import USER_TWEETS_PATTERN
from utils.redis_helper import RedisHelper

class TweetService(object):

    @classmethod
    def create_photos_from_files(cls, tweet, files):
        photos = []
        for index, file in enumerate(files):
            photo = TweetPhoto(
                tweet=tweet,
                user=tweet.user,
                file=file,
                order=index,
            )
            photos.append(photo)
        TweetPhoto.objects.bulk_create(photos)

    @classmethod
    def get_cached_tweets(cls, user_id):
        # 注意这里 django 的 queryset 是懒惰加载的方式, 在下面这句语句中, 并没有触发数据库查询.
        # 只有在真实访问 queryset时, 比如使用 for 循环访问, 类型转化list(queryset), 才会真正触发数据库查询
        queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        # 构建 redis 需要的 key 值
        key = USER_TWEETS_PATTERN.format(user_id=user_id)
        # 从 redis 中取出值
        return RedisHelper.load_objects(key, queryset)

    @classmethod
    def push_tweet_to_cache(cls, tweet):
        queryset = Tweet.objects.filter(user_id=tweet.user_id).order_by(
            '-created_at')
        key = USER_TWEETS_PATTERN.format(user_id=tweet.user_id)
        RedisHelper.push_object(key, tweet, queryset)