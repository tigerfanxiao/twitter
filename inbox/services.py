from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from notifications.signals import notify
from tweets.models import Tweet


class NotificationService(object):

    @classmethod
    def send_like_notification(cls, like):
        target = like.content_object
        # 如果自己点赞自己的帖子, 自己点赞自己的评论, 不做通知
        # 注意: 这种判断一般写在内部而不是函数外部, 这样可以让阅读代码的人, 在使用我们的函数时, 不必注意这种检测问题
        if like.user == target.user:
            return
        if like.content_type == ContentType.objects.get_for_model(Tweet):
            notify.send(
                like.user,
                recipient=target.user,
                verb='liked your tweet',
                target=target,
            )
        if like.content_type == ContentType.objects.get_for_model(Comment):
            notify.send(
                like.user,
                recipient=target.user,
                verb='liked your comment',
                target=target,
            )

    @classmethod
    def send_comment_notification(cls, comment):
        if comment.user == comment.tweet.user:  # 自己评论自己的评论不做通知
            return
        notify.send(
            comment.user,
            recipient=comment.tweet.user,
            verb='liked your comment',
            target=comment.tweet,
        )