from rest_framework import viewsets, status
from django.contrib.auth.models import User  # 注意这里经常容易引用错！
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    FriendshipSerializerForCreate,
)
from friendships.models import Friendship

"""
实现四个接口API
1. 展示我关注的人的列表(GET)  2. 展示关注我的人的列表(GET)
3. 关注别人 动作(POST)       4. 取关 动作(POST)
"""


class FriendshipViewSet(viewsets.GenericViewSet):
    # 我们希望POST /api/friendship/1/follow 是去关注 user_id=1 的用户
    # 因此这里 queryset 需要是 User.objects.all()

    # 如果是用 Friendship.objects.all() 的话就会出现 404 Not Found
    # 因为 detail=True 的 actions 会默认先去调用 get_object()
    # 即调用 queryset.filter(pk=1) 查询一下这个 Object(User) 在不在
    # 因为在创建任何关注关系前 表单始终为空 因此永远查询不到 -> 即永远会返回404
    queryset = User.objects.all()
    # 当有POST请求的时候，需要指定serializer_class去显示网页上的表单
    serializer_class = FriendshipSerializerForCreate

    # 所有 detail=True 的 action，都要传入一个pk参数
    # permission_classes -> 许可访问的 AllowAny -> 任何人都允许访问
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        # API地址 -> api/friendships/1(用户的pk)/followings/
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')  # 倒叙排列:后关注的在前
        # 把查询出来的数据放入serializer，多条数据用many=True
        serializer = FollowingSerializer(friendships, many=True)
        return Response({
            'followings': serializer.data
        }, status=status.HTTP_200_OK,)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(to_user=pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response({
            'followers': serializer.data,
        }, status=status.HTTP_200_OK)

    # permission_class -> IsAuthenticated 必须是已经登陆的用户
    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # 根据ok去取object -> 取不到: 抛出404
        self.get_object()

        # API URL: /api/friendships/<pk>/follow

        # 这里需要特殊判断一下 重复点击follow的情况 -> 比如前端猛点击好几次follow
        # 应该做静默处理，不报错 -> 因为这类操作可能是因为网络延迟等原因 -> 因此应返回201, 但用duplicate标记
        # 这类request, pk代表user去请求关注pk对应的user -> 因此from_user=request.user, to_user=pk
        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
            return Response({
                "success": True,
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)
        serializer = FriendshipSerializerForCreate(data={
            # 通过request.user.id获取其id
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })

        # 输入不合规
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'error': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        instance = serializer.save()
        return Response(
            FollowingSerializer(instance).data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        # return 404 if there is no user whose id=pk
        self.get_object()

        # 注意pk的类型是str! 所以要做类型转换
        # unfollow自己 -> 400
        if request.user.id == int(pk):
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)

        # Queryset的 delete操作返回两个值，一个是删了多少数据，一个是具体每种类型删了多少
        # 为什么会出现多种类型数据的删除？因为可能因为foreign key设置了cascade出现级联删除
        # 也就是比如A model的某个属性是B model的foreign key，并且设置了 on_delete=models.CASCADE
        # 那么当B的某个数据被删除的时候，A中的关联也会被删除。
        # 所以CASCADE是很危险的，一般最好不要用，而是用 on_delete=models.SET_NULL
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=pk,
        ).delete()
        # deleted：一共删除了多少数据 后一个参数是一个哈希表
        return Response({
            'success': True,
            'deleted': deleted
        })

    # 只有定义了list方法，才能在API Home(localhost)看到
    # 如果要用带参数 -> ？to_user_id = xx 就需要重写list方法
    def list(self, request):
        return Response({'message': 'This is the friendships homepage'})


"""
关于MySQL:
1. 不要用JOIN: -> O(n^2) -> 效率太低
2. 不要有cascade
3. drop foreignKey constraint -> 把foreignKey变成自己的数据类型
"""