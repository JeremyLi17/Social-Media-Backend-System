from accounts.models import UserProfile
from testing.testcases import TestCase


class UserProfileTests(TestCase):

    def test_profile_property(self):
        test_user = self.create_user('test_user')
        self.assertEqual(UserProfile.objects.count(), 0)
        p = test_user.profile
        self.assertEqual(isinstance(p, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)
