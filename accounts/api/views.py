from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response # 返回的数据格式
from accounts.api.serializers import (
    UserSerializer,
    LoginSerializer,
    SignupSerializer
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
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class AccountViewSet(viewsets.ViewSet):
    serializer_class = SignupSerializer

    # 查看登陆状态的API
    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        # 返回的数据，用哈希表存储
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        # 用Django自带的logout功能；注：需要rename
        django_logout(request)
        return Response({'success': True})

    """
    1. 从request中获取用户信息 (username, password)
       判断用户信息是否合规 (是否有空值) 空 -> 400
    2. Login, 检查username和password是否能对应上
            if 信息匹配上 -> 登陆
            else 信息没匹配上 -> 密码或用户名错误 -> 400
    """
    @action(methods=['POST'], detail=False)
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            # 输入不合规 400 - 数据有误
            # 只要调用了is_valid()，如果有误：errors就会有内容
            return Response({
                "success": False,
                "message": "Please check input.",
                "error": serializer.errors,
            }, status=400)

        # 用validated_data可以进行类型转换。这里都是字符串，也可以直接用data
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # 判断username是否存在
        if not User.objects.filter(username=username).exists():
            return Response({
                "success": False,
                "message": "User does not exist.",
            }, status=400)

        # 输入合规，login (注：必须是authenticate过的user才能login)
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            # user是匿名用户说明信息匹配错误，登陆失败
            return Response({
                "success": False,
                "message": "Username and password does not match.",
            }, status=400)

        # 匹配成功 -> 登陆
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(user).data,
        })

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        # 注：这里必须是data=，不然默认会把request.data当成参数instance
        serializer = SignupSerializer(data=request.data)
        # call SignupSerializer的validate方法
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                "error": serializer.errors,
            }, status=400)

        # 创建用户
        # 注：如果serializer传入已有的user，则会更新user -> 调用update()
        #                  传入的是数据     则创建user -> 调用create()
        user = serializer.save()

        # 创建后登陆
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
        }, status=201)
