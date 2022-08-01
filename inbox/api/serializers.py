from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = (
            'id',
            'actor_content_type',
            'actor_object_id',
            'verb',
            'action_object_content_type',
            'action_object_object_id',
            # 例如:给你的...(tweet/comment)点赞
            # tweet/comment -> content type
            'target_content_type',
            'target_object_id',
            'timestamp',
            'unread',
        )
