from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User
from likes.models import Like
from utils.time_helpers import utc_now

"""
user: 这篇Tweet是谁发的
content: Tweet内容 -> 只有文本
create_at: 创建时间
"""


class Tweet(models.Model):
    # User是foreignKey -> on_delete一定要设为SET_NULL
    # 然后因为设置了SET_NULL，那null要设置为True -> 表示可以为空
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Who post this Tweet",
    )
    # 设置CharField必须要设置max_length
    content = models.CharField(max_length=255)
    # auto_now_add -> 创建的时候自动去计算创建时间
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 联合索引 compound(composite ) index
        index_together = (('user', 'created_at'),)
        # QuerySet默认排序，不会对数据库造成影响和改变
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        # 减法之后会得到 timedelta-时间差 类型，然后返回小时
        # 出现的问题 前者没有时区信息，后者有时区信息
        # return (datetime.now() - self.created_at).seconds // 3600

        # 解决方案 -> 构建helper_function
        return (utc_now() - self.created_at).seconds // 3600

    def __str__(self):
        # 执行print(tweet instance)时会展示的内容 - 等于JAVA的toString方法
        return f'{self.created_at}, {self.user}, {self.content}'

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')
