import requests

import time

import json

import os

from retrying import retry


@retry(stop_max_attempt_number=3, wait_fixed=350)
def do_api_call(method_name, **request_params):
    """Функция производит обращение к api vk и возвращает
    результат запроса. Согласно декоратору делается 3
    попытки запроса с ожиданием между ними.
    """
    time.sleep(0.33)
    return requests.get("https://api.vk.com/method/{0}".format(method_name), params=request_params)


def get_user_friends(token, user_vk_id):
    """Функция принимает id-пользователя vk и токен авторизации.
    Вызывает функцию do_api_call для получения данных от api vk
    методом friends.get и возвращает json-объект.
    """

    print('Получение списка друзей...')
    method_name = "friends.get"
    request_params = dict(access_token=token, user_id=user_vk_id, v='5.80')
    friends = do_api_call(method_name, **request_params)

    return friends.json()


def get_user_groups(token, user_vk_id):
    """Функция принимает id-пользователя vk и токен авторизации.
    Вызывает функцию do_api_call для получения данных от api vk
    методом groups.get и возвращает json-объект.
    """
    method_name = 'groups.get'
    request_params = dict(access_token=token, user_id=user_vk_id, v='5.80')
    groups = do_api_call(method_name, **request_params)
    return groups.json()


def get_friends_groups(token, friends_list):
    """Функция принимает список id-пользователей VK и токен авторизации.
    В цикле вызывает функцию get_user_groups для получения данных о группах.
    Если у пользователя более 1000 групп, то берется только 1000.
    Если полученный от функции get_user_groups ответ содержит ключ "response",
    то результат добавляется в общий список групп по всем пользователям из списка
    friends_list.
    """

    print('Получение списка групп друзей пользователя...')
    friends_groups_lst = []
    count_id = len(friends_list)
    for friend_id in friends_list:
        print(f'\rОсталось обработать {count_id} профилей.', end='', flush=True)
        count_id -= 1
        try:
            for group_id in get_user_groups(token, friend_id)["response"]["items"][:1000]:
                friends_groups_lst.append(group_id)
        except KeyError:
                continue
    print('\nУспешно')
    print("Обработано {0} друзей, собрано {1} групп."
          .format(len(friends_list), len(friends_groups_lst)))
    return friends_groups_lst


def get_groups_info(groups_id, token):
    """Функция получает список id групп и токен.
    Вызывает функцию do_api_call для осуществления
    запроса с методом groups.getById к api vk с
    целью получения данных о группах.
    """

    print('Получение данных по секретным группам...')
    method_name = 'groups.getById'
    request_params = dict(access_token=token, group_ids='{}'.format(",".join([str(gid) for gid in groups_id])),
                          fields="members_count", v='5.80')
    groups_info = do_api_call(method_name, **request_params)

    res_lst = []
    for group in groups_info.json()['response']:
        group_data = {}
        try:
            group_data['name'] = group['name']
        except KeyError:
            group_data['name'] = 'not available'
        try:
            group_data['gid'] = group['id']
        except KeyError:
            group_data['gid'] = 'not available'
        try:
            group_data['members_count'] = group['members_count']
        except KeyError:
            group_data['members_count'] = 'not available'
        res_lst.append(group_data)
    print('Успешно')
    return res_lst


def get_config_data(file_name, key_1, key_2):
    """Функция получает из config-файла
    значение заданных переменных для
    авторизации в api vk."""

    with open(f'{file_name}') as f:
        data = json.load(f)
        return data[key_1], data[key_2]


if __name__ == '__main__':
    print('********************************* START PROGRAMM *********************************\n'
          'Программа выяснит в каких группах, в которых состоит пользователь, нет его друзей.\n'
          '**********************************************************************************')
    TOKEN, main_id = get_config_data('config.json', "token", "id")

    user_choise = ''
    while user_choise != 'quit' and user_choise != 'q':
        user_choise = input('Введите команду:\n'
                            'Начать подбор - введите "start"\n'
                            'Выйти - введите "quit" или "q"\n'
                            ).lower()
        if user_choise == 'start':
            # main_id = int(input('Введите идентификатор пользователя для подбора: '))  # Для ввода id с консоли
            user_info = get_user_friends(TOKEN, main_id)
            user_friends_list = user_info["response"]["items"]
            print('У пользователя {0} друзей.'.format(user_info["response"]["count"]))
            print('Получение списка групп пользователя...')
            main_user_groups = get_user_groups(TOKEN, main_id)["response"]["items"][:1000]
            if main_user_groups:
                print('Успешно')

            secret_groups = set(main_user_groups) - set(get_friends_groups(TOKEN, user_friends_list))
            print('Кол-во обнаруженных секретных групп: {0}'.format(len(secret_groups)))
            secret_groups_info = get_groups_info(secret_groups, TOKEN)

            print('Сохранение данных...')
            with open('groups.json', 'w') as gr:
                json.dump(secret_groups_info, gr,
                          indent=4, ensure_ascii=False)
            if os.path.isfile("groups.json"):
                print('Данные успешно сохранены в файле groups.json')
            print('********************************* NEXT SELECTION *********************************')
