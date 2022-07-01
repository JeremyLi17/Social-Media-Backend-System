from django.contrib.auth.models import User
from django.db import models
from tweets.models import Tweet


class NewsFeed(models.Model):
    # user -> 谁可以看见这条Tweet！(不是谁发的这条tweet
    # tweet -> tweet主体
    # created_at -> 主要用于排序(建index)
    # 因此: 假设用户A被用户1,2,3关注 那当用户A发帖时 -> 会创建3条记录，分别是:
    # 用户1可以看到这条帖子，用户2可以看到这条帖子，用户3可以看到这条帖子
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        unique_together = (('user', 'tweet'),)
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.created_at} inbox of {self.user}: {self.tweet}'