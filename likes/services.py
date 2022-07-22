from likes.models import Like
from django.contrib.contenttypes.models import ContentType


class LikeService(object):

    @classmethod
    def has_liked(cls, user, target):
        if user.is_anonymous:
            return False

        return Like.objects.filter(
            # .__class__获得contentType
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user,
        ).exists()
