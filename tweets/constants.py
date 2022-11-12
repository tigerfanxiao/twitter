class TweetPhotoStatus:
    PENDING = 0
    APPROVED = 1
    REJECTED = 2


TWEET_PHOTO_STATUS_CHOICES = (
    (TweetPhotoStatus.PENDING, 'Pending'),  # 后面的Pending 字符串会在 admin 页面显示
    (TweetPhotoStatus.APPROVED, 'Approved'),
    (TweetPhotoStatus.REJECTED, 'Rejected'),
)

TWEET_PHOTOS_UPLOAD_LIMIT = 9
