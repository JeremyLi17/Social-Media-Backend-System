from django.contrib.auth.models import User
from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


# 可以通过source='to_user'去指定访问每个model instance的 to_user 方法
# 即 通过model_instance.to_user获得数据
class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')
    # 注：这里可以不写created_at -> 因为如果这里没有 field会去model里找
    # created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        # fields会先去👆找是否有对应的field
        # serializer里没有的情况下才会去model里找
        fields = ('user', 'created_at')


class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='from_user')
    created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


# 注意：POST请求的serializer是希望前端提供的信息 -> 与Get请求不一样
class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, data):
        # 判断自己关注自己
        if data['from_user_id'] == data['to_user_id']:
            # 在validate里出现的错误都是raise ValidationError
            # 写法跟response类似
            raise ValidationError({
                'message': 'You cannot follow yourself',
            })

        # 由于在外部做过处理，因此validate部分不再处理
        # if Friendship.objects.filter(
        #     from_user_id=data['from_user_id'],
        #     to_user_id=data['to_user_id'],
        # ).exists():
        #     ...

        # 判断想要关注的用户是否存在
        # 这个和viewSet中用self.get_object()是相同的功能 -> 但这个抛出400
        if not User.objects.filter(id=data['to_user_id']).exists():
            raise ValidationError({
                'message': 'The to_user_id does not exist'
            })

        return data

    # create方法要传入validated_data
    def create(self, validated_data):
        return Friendship.objects.create(
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id'],
        )

