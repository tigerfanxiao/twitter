
# memcached
FOLLOWINGS_PATTERN = 'followings:{user_id}'
# USER_PATTERN = 'user:{user_id}'
USER_PROFILE_PATTERN = 'userprofile:{user_id}' # 注意这里也是用 user_id 而不是用 userprofile的 id

# redis
USER_TWEETS_PATTERN = 'user_tweets:{user_id}'  # 查询某个用户发的 tweet 
USER_NEWSFEEDS_PATTERN = 'user_newsfeeds:{user_id}'
