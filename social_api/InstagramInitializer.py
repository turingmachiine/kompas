from instagram_private_api import Client

import numpy as np
import numpy.lib.recfunctions as recfunctions

from kompas.settings import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD


class InstagramInitializer(object):

    def get_friends(self, nickname):
        user_name = INSTAGRAM_USERNAME
        password = INSTAGRAM_PASSWORD

        api = Client(user_name, password)
        results = api.username_info(nickname)
        id = results['user']['pk']
        followings = self.get_followings(id, api)
        followers = self.get_followers(id, api)
        if (len(followings) == 0 and len(followers) == 0 and results['user']['is_private'] == True):
            print('Account is private. Follow to account')
            # api.friendships_create(id)  #подписывается на приватный аккаунт, чтобы получить доступ в будущем
            return None, id
        friend_list = list(set(followings) & set(followers))
        return friend_list

    def get_followings(self, id, api):
        token = api.generate_uuid()
        followers = api.user_following(id, token)
        follow_list = []
        for i in range(len(followers['users'])):
            follow_list.append(followers['users'][i]['pk'])
        return follow_list

    def get_followers(self, id, api):
        token = api.generate_uuid()
        followers = api.user_followers(id, token)
        follow_list = []
        for i in range(len(followers['users'])):
            follow_list.append(followers['users'][i]['pk'])
        return follow_list
