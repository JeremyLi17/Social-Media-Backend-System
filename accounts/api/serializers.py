from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework import exceptions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class UserSerializerForTweet(serializers.ModelSerializer):
    """
    Serializer for tweets return
    """

    class Meta:
        model = User
        fields = ['id', 'username']


class UserSerializerForFriendship(UserSerializerForTweet):
    """
    Serializer for friendships return
    这种继承 + 什么都不写 + pass -> 相当于别名
    """
    pass


class LoginSerializer(serializers.Serializer):
    # Verify两个都不为空
    username = serializers.CharField()
    password = serializers.CharField()


class SignupSerializer(serializers.ModelSerializer):
    # 用ModelSerializer的话save的时候可以把用户实际的创建出来
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    # will be called when is_valid is called
    def validate(self, data):
        # 存储username的时候，就存储成小写
        # User.objects.filter(username__iexact=data['username']).exists()
        # 👆命令可以起到相同的效果 -> iexact 表示忽略大小写；效率非常低
        if User.objects.filter(username=data['username'].lower()).exists():
            # username已经存在 ->
            raise exceptions.ValidationError({
                'message': 'This username has been occupied.'
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'This email address has been occupied.'
            })
        return data

    #
    def create(self, validated_data):
        # 存储的时候用小写存储
        # 如果一定要保留大写展示，可以保存为两项username & display_name
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']

        # 初了创建用户，其他的创建对象用create(...)
        # create_user帮user设置了一些属性，并且把password变为密文
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        return user
