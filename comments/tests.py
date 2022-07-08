from testing.testcases import TestCase


class CommentModelTest(TestCase):

    def test_comment(self):
        user = self.create_user('testUser')
        tweet = self.create_tweet(user)
        create_comment = self.create_comment(user, tweet)
        # create_comment 创建成功之后 什么都不会返回 -> None
        self.assertNotEqual(create_comment.__str__(), None)
