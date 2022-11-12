from rest_framework import viewsets
from rest_framework import permissions
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.api.serializers import (
    UserSerializer,
    LoginSerializer,
    SignupSerializer,
)

from django.contrib.auth import (
    logout as django_logout,
    login as django_login,
    authenticate as django_authenticate,
)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class AccountViewSet(viewsets.ViewSet):

    serializer_class = LoginSerializer  # 如果这边加了一行, 则会在页面看到一个表单,

    @action(methods=['GET'], detail=False)
    # method 指定只能用 GET 做请求,
    # detail=False 表示这不是定义在某个具体 object 上的动作, 而是整体的动作
    # 如果 detail=True时, 需要在login_status内增加以 pk 变量, 然后需要通过 api/accounts/1/login_status 指定在某个对象上的动作
    def login_status(self, request):
        data = {
            'has_logged_in': request.user.is_authenticated,  # 如果是匿名用户, 默认是返回 False
            'ip': request.META['REMOTE_ADDR'],
            }
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data  # 把用户传给 Serializer, .data把 Serializer 对象变为数据
        return Response(data)  # 返回值都是 Response(data)

    # 如果需要在首页看到所有的动作, 比如上面的 login_status需要在写一个 list的 action

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({
            'success': True
        })

    @action(methods=['POST'], detail=False)
    def login(self, request):

        # 1. validate user input by serializer
        login_serializer = LoginSerializer(data=request.data)
        if not login_serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                "errors": login_serializer.errors,
            }, status=400)

        username = login_serializer.validated_data['username']
        password = login_serializer.validated_data['password']

        # 2. authenticate by django
        user = django_authenticate(request, username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "Username and password does not match.",
            }, status=400)
        # 3. login by django
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        }, status=200)

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        # 1. 验证用户输入
        signup_serializer = SignupSerializer(data=request.data) # 注意这里必须用data=, 因为默认是传入 instance
        if not signup_serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": signup_serializer.errors
            }, status=400)

        # 2. 创建用户, 用户登录, 返回结果
        user = signup_serializer.save()

        django_login(request, user)



        return Response({
            'success': True,
            'user': UserSerializer(user).data,
        }, status=201)





