import os

import vk
from django.conf import settings


class ConfigAPI(object):
    __token = None
    api = None

    # Стартовый обработчик. Подключает TOKEN VK API к приложению
    def init(self): # токен обрабатывается на ошибки в этом методе
        self.__vk_api_on()  # подключение VK API к системе

    # def __get_token_by_link(self, str):
    #     arr = str.split('=')
    #     if (len(arr) >= 2):
    #         arr2 = arr[1].split('&')
    #         token = arr2[0]
    #         print(token)
    #         self.__token = token
    #     else:
    #         print('ссылка повреждена, попробуйте еще раз!')
    #         print(' ')
    #         self.init()

    def __vk_api_on(self):
        token = settings.VK_API_TOKEN
        try:
            if (token != None):
                session = vk.Session(token)
                self.api = vk.API(session, v=5.103)
        except Exception:
            print('Токен недействителен или поврежден, попробуйте еще раз')
