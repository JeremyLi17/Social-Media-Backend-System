from rest_framework import serializers
from accounts.api.serializers import UserSerializerForComments
from comments.models import Comment
from tweets.models import Tweet
from rest_framework.exceptions import ValidationError


# Note: 一般SerializerForCreate要重写create方法
class CommentSerializerForCreate(serializers.ModelSerializer):
    # 手动添加user_id和tweet_id 默认只能添加user和tweet
    user_id = serializers.IntegerField()
    tweet_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ('id', 'user_id', 'tweet_id', 'content')

    # call validated_data 和 is_valid()时候会调用
    # 入参是data -> return validated_data
    def validate(self, data):
        # comment里用到validate的地方：
        # 如果tweet不存在 -> raise error

        tweet_id = data['tweet_id']
        # 判断id是否存在用 filter().exist()
        # 注！！！filter里是id=... 不是tweet_id=...
        if not Tweet.objects.filter(id=tweet_id).exists():
            # validate过程出现的异常都raise ValidationError
            # 要从rest_framework.exceptions里import, 返回的是object
            raise ValidationError({"message": "the tweet is not exist"})
        return data

    # 在SerializerForCreate里调用objects.create方法
    def create(self, validated_data):
        return Comment.objects.create(
            user_id=validated_data['user_id'],
            tweet_id=validated_data['tweet_id'],
            content=validated_data['content'],
        )


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializerForComments()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'tweet_id', 'content', 'created_at', 'updated_at')


class CommentSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'id',
            'user',
            'tweet_id',
            'content',
            'updated_at',
        )

    # 这个serializer只有Update时会用到，因此只实现update方法就可以
    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()
        # update方法要求返回更新后的instance
        return instance
