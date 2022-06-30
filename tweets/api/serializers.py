from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializerForTweet


class TweetSerializer(serializers.ModelSerializer):
    # 如果不写这个，下面field中展示user只会以user_id的形式展示
    # 用这个的话，user会被深入解析 -> 每个field也可以是serializer()
    user = UserSerializerForTweet()

    class Meta:
        model = Tweet # 展示的model类型
        fields = ('id', 'user', 'created_at','content') # 展示的field


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
