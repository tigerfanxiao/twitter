from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from accounts.models import UserProfile


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']


class UserSerializerWithProfile(UserSerializer):
    # 如果我丢给给 Serializer 的 obj 是 User, 那么就会通过 user.profile.nickname来获取nickname
    nickname = serializers.CharField(source='profile.nickname')
    avatar_url = serializers.SerializerMethodField()  # method_field对应的方法就是 get_avatar_url

    def get_avatar_url(self, obj):
        if obj.profile.avatar:
            return obj.profile.avatar.url
        return None

    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'avatar_url')


class UserProfileSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('nickname', 'avatar')


class UserSerializerForTweet(UserSerializerWithProfile):
    pass

class UserSerializerForFriendship(UserSerializerWithProfile):
    # 这种别名的写法, 方便在后面如果要修改的时候, 只要在这里修改, 不因为修改 UserSerializer影响了所有被继承的类
    pass


class UserSerializerForComment(UserSerializerWithProfile):
    pass


class UserSerializerForLike(UserSerializerWithProfile):
    pass


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data['username'].lower()

        if not User.objects.filter(username=username).exists():
            raise ValidationError({
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

    def validate(self, attrs):  # 这里用来验证post 的参数, 在 serializer.is_valid()时调用
        username = attrs['username'].lower()
        email = attrs['email'].lower()
        if User.objects.filter(username=username).exists():
            raise ValidationError({
                'username': 'This username has been occupied.'
            })

        if User.objects.filter(email=email).exists():
            raise ValidationError({
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

        # 在用户完成注册后创建 UserProfile
        user.profile
        return user  # create方法必须返回被创建的对象