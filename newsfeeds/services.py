from newsfeeds.models import NewsFeed
from friendships.services import FriendshipService


class NewsFeedServices(object):

    # fanout - 扇出,分发
    # 给每个关注了发布tweet的用户在newsfeed中加一条数据
    @classmethod
    def fanout_to_followers(cls, tweet):
        # 错误方法：
        # 1. 获取所有关注了发布这篇tweet的人
        # followers = FriendshipService.get_followers(tweet.user)
        # for-loop + Query --> 严厉禁止，一定非常慢
        # for follower in followers:
        #     NewsFeed.objects.create(
        #         user=follower,
        #         tweet=tweet,
        #     )

        # 正确方法：bulk_create 把insert语句合成一条
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        # 自己也可以看到自己发的
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        # bulk_create -> 批量创建(insert)
        NewsFeed.objects.bulk_create(newsfeeds)
