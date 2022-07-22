from rest_framework import serializers
from comments.api.serializers import CommentSerializer
from likes.api.serializers import LikeSerializer
from likes.services import LikeService
from tweets.models import Tweet
from accounts.api.serializers import UserSerializerForTweet


class TweetSerializer(serializers.ModelSerializer):
    # 如果不写这个，下面field中展示user只会以user_id的形式展示
    # 用这个的话，user会被深入解析 -> 每个field也可以是serializer()
    user = UserSerializerForTweet()
    # 返回通过计算后得到的数据 -> 定义field后还要定义get方法
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Tweet  # 展示的model类型
        # 展示的field
        fields = (
            'id',
            'user',
            'created_at',
            'content',
            'comments_count',
            'likes_count',
            'has_liked',
        )

    def get_comments_count(self, obj):
        # comment_set是django帮忙定义的
        return obj.comment_set.count()

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_has_liked(self, obj):
        # obj: 当前的Tweet object
        # 需要获得当前登陆用户是否点赞 -> 当前登陆用户:
        # self.context['request'].user
        return LikeService.has_liked(self.context["request"].user, obj)


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model = Tweet
        # 那些field是可以写进去的 -> 在发布tweet的时候只填content
        fields = ('content',)

    def create(self, validated_data):
        # 获得请求的user
        user = self.context['request'].user
        # 获取content -> validated_data里获取
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet


class TweetSerializerForDetail(TweetSerializer):
    # 用source
    comments = CommentSerializer(source='comment_set', many=True)
    likes = LikeSerializer(source='like_set', many=True)

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'comments',
            'created_at',
            'content',
            'likes',
            'comments',
            'likes_count',
            'comments_count',
            'has_liked',
        )


# class TweetSerializerForNewsFeed(serializers.ModelSerializer):
#
#     """
#     Serializer for NewsFeed return
#     """
#
#     class Meta:
#         model = Tweet  # 展示的model类型
#         fields = ('id', 'content')  # 展示的field
