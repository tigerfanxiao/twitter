from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    """
    这个 Permission 负责检查 obj.user 是不是 == request.user
    这个类是比较通用的, 今后如果有其他也用到这个类的方法, 可以将文件放到一个共享的位置
    Permission 会一个个被执行
    - 如果 detail=False 的 action, 只会检测 has_permission
    - 如果 detail=True 的 action, 同时会检测 has_permission 和 has_object_permission
    如果出错的时候, 默认的错误信息会显示 IsObjectOwner.message 中的内容
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        # 这里 obj 是根据 detail=True 时, 用 PK 指去 调用 self.get_object查询 queryset 得到对象
        return request.user == obj.user  # 写 twit