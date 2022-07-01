from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate
from tweets.models import Tweet
from newsfeeds.services import NewsFeedServices


class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    """
    继承自GenericViewSet, 和两个混入(两个混入可以不加)
    """
    # 设置queryset -> 调用self.get_queryset的时候会call到
    queryset = Tweet.objects.all()
    # 创建时表单的样子
    serializer_class = TweetSerializerForCreate

    def list(self, request, *args, **kwargs):
        # 必须要求指定 user_id 作为筛选条件
        # 如果没有 user_id -> 400
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)

        # 取出该用户所有的Tweets
        # request.query_params -> 请求的data
        user_id = request.query_params['user_id']
        # order_by -> 根据created_at 倒序拍
        tweets = Tweet.objects.filter(user_id=user_id).order_by('-created_at')

        # Serializer传入的是QuerySet
        # 如果many=True 则表示传入的是list of dict
        serializer = TweetSerializer(tweets, many=True)

        # 约定俗成 -> JSON的最外层默认是一个dict,一般不直接返回list
        return Response({'tweets': serializer.data})

    def create(self, request, *args, **kwargs):
        # 因为在创建tweet的时候需要用到发布者(User)的信息
        # 一般直接把request传给serializer/ "user": request.user
        # 这个serializer就是最终的tweet体
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={"request": request},
        )

        # 类似的验证过程 - 验证输入是否valid 以后创建也是类似
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)

        # 创建tweet对象
        # call create method in TweetSerializerForCreate
        tweet = serializer.save()

        # 发送tweet之后 - 在newsfeed表中给发布者每个follower添加数据
        NewsFeedServices.fanout_to_followers(tweet)

        # TweetSerializer(tweet).data本身就是一个dict了 就不用加{}了
        return Response(TweetSerializer(tweet).data, status=201)

    # 权限管理
    def get_permissions(self):
        # self.action -> 对应是调用的方法名(create, list...)
        if self.action == 'list':
            # 允许任何人都能访问
            return [AllowAny()]
        # 必须登陆
        return [IsAuthenticated()]
