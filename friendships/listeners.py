def friendship_changed(sender, instance, **kwargs):
    # 这个 import 必须写在里面, 否则会报循环引用的错
    # 因为 friendship.service 会引用 friendship.model
    # friendship.model又会应用invalidate_following_cache
    # invalidate_following_cache又会应用friendship.service
    # 循环应用的工程规范把引用写在函数内部
    from friendships.services import FriendshipService
    FriendshipService.invalidate_following_cache(instance.from_user_id)