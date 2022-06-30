from django.contrib.auth.models import User
from django.test import TestCase
from tweets.models import Tweet
from datetime import timedelta
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def test_hours_to_now(self):
        # 创建测试用户
        testuser = User.objects.create_user(username='testuser')
        # 创建Tweet
        tweet = Tweet.objects.create(user=testuser, content='I will have a good job!')
        # 人为修改created_at的时间
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        # 查看测试结果
        self.assertEqual(tweet.hours_to_now, 10)
