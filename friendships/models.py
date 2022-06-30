from django.db import models
from django.contrib.auth.models import User


class Friendships(models.Model):
    # 用户实例可以通过user1.following_friendship_set.all()获得user1全部的关注
    # 当一个Model只有一个foreignKey的时候related_name可以不设置
    # 可以直接通过user1.friendships.all()访问
    # 当有两个以上的foreignKey的是相同的model的时候必须设置
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='following_friendship_set',
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='follower_friendship_set',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Friendships表的一些属性 -> 联合索引，唯一性约束...
    class Meta:
        # 联合索引在Model中不需要标明正/倒叙，在order_by的时候再标正/倒叙
        index_together = (
            # 获取我关注的人 -> 时间顺序排列
            ('from_user', 'created_at'),
            # 关注我的人
            ('to_user', 'created_at'),
        )
        unique_together = (('from_user', 'to_user'),)

    def __str__(self):
        # 等价形式 -> '{} followed {}'.format(self.from_user, self.to_user)
        return f'{self.from_user} followed {self.to_user}'
