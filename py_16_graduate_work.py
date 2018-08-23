import requests

import time

import json


def do_api_call(method_name, **request_params):
    """Функция производит обращение к api vk и возвращает
    результат запроса. Согласно декоратору делается 3
    попытки запроса с ожиданием между ними.
    """

    request_params['access_token'] = TOKEN
    request_params['v'] = '5.80'
    while True:
        res = requests.get("https://api.vk.com/method/{0}".format(method_name), params=request_params)
        try:
            if res.json()["response"]:
                return res
        except KeyError:
            if res.json()['error']['error_code'] == 6:
                time.sleep(0.33)
                continue
            elif res.json()['error']['error_code'] == 18:
                return res


def get_user_friends(user_vk_id):
    """Функция принимает id-пользователя vk и токен авторизации.
    Вызывает функцию do_api_call для получения данных от api vk
    методом friends.get и возвращает json-объект.
    """

    print('Получение списка друзей...')
    method_name = "friends.get"
    request_params = dict(user_id=user_vk_id)
    friends = do_api_call(method_name, **request_params)

    return friends.json()


def get_user_groups(user_vk_id):
    """Функция принимает id-пользователя vk и токен авторизации.
    Вызывает функцию do_api_call для получения данных от api vk
    методом groups.get и возвращает json-объект.
    """

    method_name = 'groups.get'
    request_params = dict(user_id=user_vk_id)
    groups = do_api_call(method_name, **request_params)

    return groups.json()


def get_friends_groups(friends_list):
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
            friends_groups_lst.extend(get_user_groups(friend_id)["response"]["items"])
        except KeyError:
                continue
    print('\nУспешно')
    print("Обработано {0} друзей, собрано {1} групп."
          .format(len(friends_list), len(friends_groups_lst)))

    return friends_groups_lst


def get_groups_info(groups_id):
    """Функция получает список id групп и токен.
    Вызывает функцию do_api_call для осуществления
    запроса с методом groups.getById к api vk с
    целью получения данных о группах.
    """

    print('Получение данных по секретным группам...')
    method_name = 'groups.getById'
    request_params = dict(group_ids='{}'.format(",".join([str(gid) for gid in groups_id])),
                          fields="members_count")
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


def get_config_data(file_name):
    """Функция получает из config-файла
    значение переменных для
    авторизации в api vk."""

    with open(f'{file_name}') as f:
        data = json.load(f)
        return data


if __name__ == '__main__':
    print('********************************* START PROGRAMM *********************************\n'
          'Программа выяснит в каких группах, в которых состоит пользователь, нет его друзей.\n'
          '**********************************************************************************')
    config_data = get_config_data('config.json')
    TOKEN, main_id = config_data["token"],  config_data["id"]

    user_choise = ''
    while user_choise != 'quit' and user_choise != 'q':
        user_choise = input('Введите команду:\n'
                            'Начать подбор - введите "start"\n'
                            'Выйти - введите "quit" или "q"\n'
                            ).lower()
        if user_choise == 'start':
            user_info = get_user_friends(main_id)
            user_friends_list = user_info["response"]["items"]
            print('У пользователя {0} друзей.'.format(user_info["response"]["count"]))
            print('Получение списка групп пользователя...')
            main_user_groups = get_user_groups(main_id)["response"]["items"]
            if main_user_groups:
                print('Успешно')

            secret_groups = set(main_user_groups) - set(get_friends_groups(user_friends_list))
            print('Кол-во обнаруженных секретных групп: {0}'.format(len(secret_groups)))
            secret_groups_info = get_groups_info(secret_groups)

            print('Сохранение данных...')
            with open('groups.json', 'w') as gr:
                json.dump(secret_groups_info, gr,
                          indent=4, ensure_ascii=False)
            print('Данные успешно сохранены в файле groups.json')
            print('********************************* NEXT SELECTION *********************************')
