from friendships.models import Friendship


class FriendshipService(object):

    # 获得user的全部followers
    @classmethod
    def get_followers(cls, user):
        # 错误写法1:
        # Step1 获取全部to_user是user的friendship关系
        # friendships = Friendship.objects.filter(to_user=user)
        # Step2 针对每个friendship，将其from_user放入列表 -> 然后返回
        # return [friendship.from_user for friendship in friendships]
        # 会导致 N+1 Queries 问题 -> 在.from_user的时候 会再次产生一次Query
        # 最终会进行1次(查出全部的friendships)+N次(每次.from_user)查询

        # 错误写法2：预先加载 (针对上一种方法做出的修改，即知道要用到from_user，就先把它加载)
        # friendships = Friendship.objects.filter(
        #     to_user=user
        # ).select_related('from_user')
        # return [friendship.from_user for friendship in friendships]
        # 虽然使用select_related语句可以让return时.from_user可以直接获取到数据，即return时不会产生Query
        # 但select_related会被翻译成join语句 -> 复杂度上升，不实用

        # 正确写法1：一共2条Query
        # friendships = Friendship.objects.filter(to_user=user)
        # 注：.from_user_id不会产生新的Query 因为from_user_id在friendship里存了
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # 使用 id__in 将id转换成user 只有一句查询
        # followers = User.objects.filter(id__in=follower_ids)

        # 正确写法2(简洁-和1等价) -> 使用prefetch_related
        friendships = Friendship.objects.filter(
            to_user=user
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]
