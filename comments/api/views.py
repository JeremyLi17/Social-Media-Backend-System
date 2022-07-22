from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from comments.api.serializers import (
    CommentSerializerForCreate,
    CommentSerializer,
    CommentSerializerForUpdate,
)
from comments.models import Comment
from comments.api.permissions import IsObjectOwner


# 通用的做法：继承GenericViewSet
from utils.decorators import required_params


class CommentViewSet(viewsets.GenericViewSet):
    """
    实现：list, create, update, destroy
    不实现retrieve -> 查询单个comment的请求
    """
    # serializer_class -> 当用django rest-framework的UI的时候
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',)

    # POST /api/comments/ -> create
    # GET /api/comments/?tweet_id=1  -> list
    # GET /api/comments/1/ -> retrieve
    # DELETE /api/comments/1/ -> destroy
    # PATCH /api/comments/1/ -> partial_update
    # PUT /api/comments/1/ -> update (一般是用update)

    # POST -> 数据在request.data里
    # GET -> 数据在query_params里

    # 以上的预先定义的method -> 用get_permission进行权限判断
    def get_permissions(self):
        # 注意要加() 用的是AllowAny()/IsAuthenticated()
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'destroy']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    # create comment API
    def create(self, request, *args, **kwargs):
        # 首先会通过get_permission进行权限判断

        # 1. 构建data object
        data = {
            # 通过request获取id
            "user_id": request.user.id,
            # 通过request获取tweet_id
            "tweet_id": request.data.get("tweet_id"),
            "content": request.data.get("content"),
        }
        # 2. 将数据传入SerializerForCreate
        serializer = CommentSerializerForCreate(data=data)
        # 3.调用is_valid(serializer的)method判断数据是否规范
        if not serializer.is_valid():
            # validate过程出错 -> return 400
            return Response({
                'message': 'Please check your input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # 通过save调用serializer里的create方法
        comment = serializer.save()

        # 创建成功 -> 返回 201 (返回的信息用CommentSerializer展示)
        return Response(
            CommentSerializer(comment, context={"request": request}).data,
            status=status.HTTP_201_CREATED
        )

    # list传入的是request
    @required_params(params=['tweet_id'])
    def list(self, request, *args, **kwargs):
        # list要做的是list出某一id的tweet的所有评论

        # [用decorator简化了这一部分的判断]
        # if 'tweet_id' not in request.query_params:
        #     return Response({
        #         'message': 'missing tweet_id in request',
        #         'success': False,
        #     }, status=status.HTTP_400_BAD_REQUEST)

        # filter approach 1 -> use objects.filter
        # tweet_id = request.query_params['tweet_id']
        # comments = Comment.objects.filter(tweet_id=tweet_id)

        # approach 2: 3rd party lib django-filter
        # 注：settings里的名字是django_filters
        # 注意：安装第三方库(大部分)都要在settings里更新！
        queryset = self.get_queryset()
        # filter_queryset -> 用到filterset_fields
        comments = self.filter_queryset(queryset).order_by('created_at')
        serializer = CommentSerializer(
            comments,
            context={'request': request},
            many=True,
        )

        return Response({
            'comments': serializer.data,
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        # 既要传入instance，也要传入data
        serializer = CommentSerializerForUpdate(
            # get_object是DRF包装的一个函数，会在找不到的时候 raise 404 error
            # 所以这里无需做额外判断
            instance=self.get_object(),
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
               'message': 'Please check you input',
            }, status=status.HTTP_400_BAD_REQUEST)

        # 因为在构建serializer的时候传入了instance, 所以会call update()
        comment = serializer.save()
        return Response(
            CommentSerializer(comment, context={"request": request}).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()

        # DRF 里默认 destroy 返回的是 status code = 204 no content
        # 这里 return 了 success=True 更直观的让前端去做判断，所以 return 200 更合适
        return Response({'success': True}, status=status.HTTP_200_OK)
