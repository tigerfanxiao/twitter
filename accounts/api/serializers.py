from django.contrib.auth.models import User, Group
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


# class AccountSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Account
#         field = ['']