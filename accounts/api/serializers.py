from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework import exceptions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class UserSerializerForTweet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

# 写了一个别名
class UserSerializerForFriendship(UserSerializerForTweet):
    pass

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data['username'].lower()

        if not User.objects.filter(username=username).exists():
            raise exceptions.ValidationError({
                "username": "User does not exists."
            })
        data['username'] = username
        return data

class SignupSerializer(serializers.ModelSerializer):
    # ModelSerializer的用处在于, 当我们使用serializer.save()的时候, 会自动创建一个对象.
    # 因为要创建对象所以要引入 Meta class
    # 因为要创建用户, 最少需要检验三个内容, username, password, email
    username = serializers.CharField(min_length=6, max_length=20)
    password = serializers.CharField(min_length=6, max_length=20)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def validate(self, attrs): # 这里用来验证post 的参数, 在 serializer.is_valid()时调用
        username = attrs['username'].lower()
        email = attrs['email'].lower()
        if User.objects.filter(username=username).exists():
            raise exceptions.ValidationError({
                'username': 'This username has been occupied.'
            })

        if User.objects.filter(email=email).exists():
            raise exceptions.ValidationError({
                'email': 'This email address has been occupied'
            })
        attrs['username'] = username
        attrs['email'] = email
        return attrs

    def create(self, validated_data):  # 这是在 serializer.save()是调用的
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()  # 这里都要保存为小写
        password = validated_data['password']
        # 要用create_user方法, 不能直接用 create, 因为 django 在后台对password 做了处理, 变成密文
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return user  # create方法必须返回被创建的对象
