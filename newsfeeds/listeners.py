def push_newsfeed_to_cache(sender, instance, created, **kwargs):
    if not created:
        return

    from newsfeeds.services import NewsFeedServices
    NewsFeedServices.push_newsfeed_to_cache(instance)