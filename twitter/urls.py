"""twitter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from accounts.api.views import UserViewSet, AccountViewSet
from comments.api.views import CommentsViewSet
from django.contrib import admin
from django.urls import include, path
from friendships.api.views import FriendshipViewSet
from newsfeeds.api.views import NewsFeedViewSet
from rest_framework import routers
from tweets.api.views import TweetViewSet

router = routers.DefaultRouter()   # 使用 rest_framework的 router 来注册 url
router.register(r'api/users', UserViewSet)  # 注册了 api/users页面, 使用 UserViewSet 来处理请求
router.register(r'api/accounts', AccountViewSet, basename='accounts')
router.register(r'api/tweets', TweetViewSet, basename='tweets')
router.register(r'api/friendships', FriendshipViewSet, basename='friendships')
router.register(r'api/newsfeeds', NewsFeedViewSet, basename='newsfeeds')
router.register(r'api/comments', CommentsViewSet, basename='comments')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),  # 引用 router, 来定义首页
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),  # restframe文档中, 要求配置
    path('__debug__/', include('debug_toolbar.urls')),  # 这是 debug tool bar 用的
]
