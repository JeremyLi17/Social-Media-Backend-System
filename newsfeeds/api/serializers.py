from rest_framework import serializers
from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetSerializerForNewsFeed


class NewsFeedSerializer(serializers.ModelSerializer):
    tweet = TweetSerializerForNewsFeed()

    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'user', 'tweet')