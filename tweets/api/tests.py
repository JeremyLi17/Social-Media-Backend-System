from rest_framework.test import APIClient
from testing.testcases import TestCase
from tweets.models import Tweet


# 要测试的API的URL -> 结尾一定要加"/" 不然会返回301 redirect
TWEET_LIST_API = '/api/tweets/'
TWEET_CREATE_API = '/api/tweets/'


# 用自己重写过带有create_user和create_tweet的TestCase类
class TweetApiTests(TestCase):

    # setUp是在每一个Unit test被执行之前会被执行的 -> 准备阶段
    def setUp(self):
        # 默认APIClient是未登陆(匿名)用户
        self.anonymous_client = APIClient()

        # 创建登陆用户
        self.user1 = self.create_user('user1')
        # 这种用法就是创建一个长度为3的list
        # 每个元素都是self.create_tweet(self.user1)
        self.tweets1 = [
            self.create_tweet(self.user1)
            for i in range(3)
        ]
        self.user1_client = APIClient()
        # 用force_authenticate -> 用user1的信息去访问
        self.user1_client.force_authenticate(self.user1)

        # 另一个测试用户 -> 用于检测user1是否能访问user2发的帖子
        self.user2 = self.create_user('user2')
        self.tweets2 = [
            self.create_tweet(self.user2)
            for i in range(2)
        ]

    # 测试1 ：list API
    def test_list_api(self):
        # 用list API必须带user_id, 否则400
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, 400)

        # 正常 request
        # 1. 匿名用户访问
        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweets']), 3)
        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.user2.id})
        self.assertEqual(len(response.data['tweets']), 2)
        # 检测排序是否按照新创建的在前面的顺序来的 -> 倒叙
        self.assertEqual(response.data['tweets'][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data['tweets'][1]['id'], self.tweets2[0].id)

    # 测试2: create API
    def test_create_api(self):
        # 发布内容必须登录, 否则403
        response = self.anonymous_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 403)

        # 发布内容必须带content, 否则400
        response = self.user1_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 400)

        # 发布内容content不能太短或太长 min_length到max_length之间
        response = self.user1_client.post(TWEET_CREATE_API, {'content': '1'})
        self.assertEqual(response.status_code, 400)
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': '0' * 141
        })
        self.assertEqual(response.status_code, 400)

        # 正常发帖
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is my first tweet!'
        })
        """
        1. 先判断是否发布成功 -> status是否是201 (注意不是200)
        2. 发帖的信息是否正确 user的id
        3. tweet的总数是否+1
        """
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)
