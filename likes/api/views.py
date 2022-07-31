from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from inbox.services import NotificationService
from likes.api.serializers import (
    LikeSerializerForCreate,
    LikeSerializer,
    LikeSerializerForCancel,
)
from likes.models import Like
from utils.decorators import required_params


class LikeViewSet(viewsets.GenericViewSet):
    # 一般需要有这三个
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializerForCreate

    # must have content_type and object_id
    # create 是 post, request_attr用data
    @required_params(method='POST', params=['content_type', 'object_id'])
    def create(self, request, *args, **kwargs):
        serializer = LikeSerializerForCreate(
            data=request.data,
            context={'request': request},
        )

        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # 避免重复发送
        instance, created = serializer.get_or_create()
        if created:
            # send notification
            NotificationService.send_like_notification(instance)

        return Response(
            LikeSerializer(instance).data,
            status=status.HTTP_201_CREATED,
        )

    # detail = False -> 不需要对应的ID
    @action(methods=['POST'], detail=False)
    @required_params(method='POST', params=['content_type', 'object_id'])
    def cancel(self, request, *args, **kwargs):
        # 自定义API -> 需要import rest_framework的action
        serializer = LikeSerializerForCancel(
            data=request.data,
            context={'request': request},
        )

        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'error': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # 实现cancel方法完成取消点赞的功能
        serializer.cancel()
        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)
