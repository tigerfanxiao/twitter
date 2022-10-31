from rest_framework.response import Response
from rest_framework import status
from functools import wraps


# 最外层的函数相当于一个 decorator 的生成器, 每次获得一个参数后, 就返回一个 decorator
def required_params(request_attr='query_params', params=None):
    """
    当我们使用@required_params(params=['some_param'])的时候
    这个required_params 函数需要返回一个 decorator 函数, 这个 decorator 函数
    就是被@required_params包裹起来的函数 view_func
    """
    # 从效果上来说, 参数中国写 params=[]很多时候也没太大问题
    # 但是从好的编程习惯上来说, 函数的参数列表中的值不能是一个 mutable 参数
    if params is None:
        params = []

    def decorator(view_func):
        """
        decorator 函数通过 wraps 来将 view_func 里的参数解析出来传递给 _wrapped_view
        这里的 instance 参数其实就是在 view_func 里的 self
        """
        @wraps(view_func) # wraps 的作用是把传给 view_func中的所有参数拿出来, 传给下面 _wrapped_view函数定义的参数中
        def _wrapped_view(instance, request, *args, **kwargs):
            # 如果是 get 方法, 直接从 request.query_params中获得参数
            # 如果是 post 方法, 从 request.data中获取参数
            data = getattr(request, request_attr)

            missing_params = [
                param for param in params  # 挑出我指定的必选参数
                if param not in data   # 如果必选参数, 已经不在 request 的 data 中, 则为缺失的参数
            ]
            if missing_params: # bool([]) 是 False
                params_str = ','.join(missing_params)
                return Response({
                    'message': u'missing {} in request.'.format(params_str),
                }, status=status.HTTP_400_BAD_REQUEST)
            # 做完检测之后, 在去调动被 @required_params包裹起来的 view_func
            return view_func(instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator

