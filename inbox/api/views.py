from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from notifications.models import Notification
from inbox.api.serializers import (
    NotificationSerializer,
    NotificationSerializerForUpdate,
)
from utils.decorators import required_params


class NotificationViewSet(
    viewsets.GenericViewSet,
    # 作用是它里面实现了一个list方法, 自带翻页 -> 会去找到settings里的Pagenation
    viewsets.mixins.ListModelMixin,
):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    # 能用于filter的项
    filterset_fields = ('unread',)

    # 要么用get_queryset 要么写默认的query_set
    def get_queryset(self):
        # return self.request.user.notifications.all()
        return Notification.objects.filter(recipient=self.request.user)

    # url_path -> 修改url_path into
    @action(methods=['GET'], detail=False, url_path='unread-count')
    def unread_count(self, request, *args, **kwargs):
        # /api/notifications/unread-count/
        count = self.get_queryset().filter(unread=True).count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='mark-all-as-read')
    def mark_all_as_read(self, request, *args, **kwargs):
        # /api/notifications/mark-all-as-read

        # update方法: SQL中的UPDATE语法 -> 返回被更新了几个
        updated_count = self.get_queryset().update(unread=False)
        return Response({'marked_count': updated_count}, status=status.HTTP_200_OK)

    # method = POST -> 去request.data取params,  method = get -> 去query_params里取
    @required_params(method='PUT', params=['unread'])
    def update(self, request, *args, **kwargs):
        # PUT /api/notifications/<id>/
        """
        用户可以标记一个 notification 为已读或者未读。标记已读和未读都是对 notification
        的一次更新操作，所以直接重载 update 的方法来实现。另外一种实现方法是用一个专属的 action：
            @action(methods=['POST'], detail=True, url_path='mark-as-read')
            def mark_as_read(self, request, *args, **kwargs):
                ...
            @action(methods=['POST'], detail=True, url_path='mark-as-unread')
            def mark_as_unread(self, request, *args, **kwargs):
                ...
        两种方法都可以，更偏好重载 update，因为更通用更 rest 一些, 而且 mark as unread 和
        mark as read 可以公用一套逻辑。
        """
        # 必须是传入instance,save才能调用update
        # 找不着会raise 404
        serializer = NotificationSerializerForUpdate(
            # self.get_object -> 会取出this notification
            instance=self.get_object(),
            data=request.data,
        )

        if not serializer.is_valid():
            # 如果没有自定义validate -> 执行每个field的validate
            return Response({
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # save会去调用SerializerForUpdate的update方法
        notification = serializer.save()

        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK,
        )
