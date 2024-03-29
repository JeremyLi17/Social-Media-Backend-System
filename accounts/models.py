from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    # One2One field 会创建一个 unique index，确保不会有多个 UserProfile 指向同一个 User
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)

    # Django 还有一个 ImageField，但是尽量不要用，会有很多的其他问题，用 FileField 可以起到
    # 同样的效果。因为最后我们都是以文件形式存储起来，使用的是文件的 url 进行访问
    avatar = models.FileField(null=True)

    # 当一个 user 被创建之后，会创建一个 user profile 的 object
    # 此时用户还来不及去设置 nickname 等信息，因此设置 null=True
    nickname = models.CharField(null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.user, self.nickname)


# 定义一个profile的property方法，植入到User这个model里
# 这样当我们通过user的一个实例化对象访问profile的时候，即 user_instance.profile
# 就会在 UserProfile 中进行 get_or_create 来获得对应的 profile 的 object
# *** 如何给库函数增加功能 ***
def get_profile(user):
    # 如果有cached
    if hasattr(user, '_cached_user_profile'):
        # return user._cached_user_profile
        return getattr(user, '_cached_user_profile')

    # 没有...
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # 使用user对象的属性进行缓存(cache)，避免多次调用同一个user的profile时重复的对数据库进行查询
    setattr(user, '_cached_user_profile', profile)
    return profile


# 给User Model增加了一个profile的property方法用于快捷访问
# class User():
#     @property
#     def profile():
#       ...
User.profile = property(get_profile)
