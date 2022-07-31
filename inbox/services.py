from comments.models import Comment
from tweets.models import Tweet
from django.contrib.contenttypes.models import ContentType
from notifications.signals import notify


class NotificationService(object):

    @classmethod
    def send_like_notification(cls, like):
        # target -> like的对象GenericForeignKey
        target = like.content_object

        # check if: 自己点赞自己
        if like.user == target.user:
            return

        # 点赞tweet
        # 获取Model -> ContentType.objects.get_for_model(Model)
        if like.content_type == ContentType.objects.get_for_model(Tweet):
            notify.send(
                like.user,
                recipient=target.user,
                verb='liked your tweet',
                target=target,
            )

        # 点赞comment
        if like.content_type == ContentType.objects.get_for_model(Comment):
            notify.send(
                like.user,
                recipient=target.user,
                verb='liked your comment',
                target=target,
            )

    @classmethod
    def send_comment_notification(cls, comment):
        if comment.user == comment.tweet.user:
            return
        notify.send(
            comment.user,
            recipient=comment.tweet.user,
            verb='liked your comment',
            target=comment.tweet,
        )