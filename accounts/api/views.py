from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.api.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer



class AccountViewSet(viewsets.ViewSet):
    @action(methods=['GET'], detail=False)
    # method 指定只能用 GET 做请求,
    # detail=False 表示这不是定义在某个具体 object 上的动作, 而是整体的动作
    # 如果 detail=True时, 需要在login_status内增加以 pk 变量, 然后需要通过 api/accounts/1/login_status 指定在某个对象上的动作
    def login_status(self, request):
        data = {
            'has_logged_in': request.user.is_authenticated,
            'ip': request.META['REMOTE_ADDR'],
            }
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

