import requests

import time

import json

import os


def get_config_data(file, key_1, key_2):
    """Функция получает из файла config.json
    значение заданных переменных."""

    with open(f'{file}') as f:
        data = json.load(f)
        return (data[key_1], data[key_2])


def get_user_friends(token, user_vk_id):
    """Функция принимает id-пользователя vk и токен авторизации.
    С помощью requests запрашивает данные о друзьях,
    пользователя. Возвращает json-объект.
    """

    print('Получение списка друзей...')
    response = requests.get("https://api.vk.com/method/friends.get",
                            params=dict(
                                access_token=token,
                                user_id=user_vk_id,
                                v='5.80'
                                )
                            )
    print('Успешно')
    return response.json()


def get_user_groups(token, user_vk_id):
    """Функция принимает id-пользователя vk и токен авторизации.
    С помощью requests запрашивает данные о группах,
    в которых состоит пользователь. Возвращает json-объект.
    """

    response = requests.get('https://api.vk.com/method/groups.get',
                            params=dict(
                                access_token=token,
                                user_id=user_vk_id,
                                v='5.80'
                                )
                            )
    return response.json()


def get_friends_groups(token, user_friends_list):
    """Функция принимает список id-пользователей VK, токен авторизации.
    Пробует получить данные методом requests. Возвращает общий список
    групп по всем пользователям из списка user_friends_list.
    """

    print('Получение списка групп друзей пользователя...', end='')
    friends_groups_lst = []
    print('прогресс:', end='')
    count_id = len(user_friends_list)
    for friend_id in user_friends_list:
        print(f'\rОсталось обработать {count_id} профилей', end='', flush=True)
        count_id -= 1
        try:
            for group_id in get_user_groups(token, friend_id)["response"]["items"]:
                friends_groups_lst.append(group_id)
            time.sleep(0.35)
        except KeyError:
            continue
    print('\nУспешно')
    print("Обработано {0} друзей, собрано {1} групп."
          .format(len(user_friends_list), len(friends_groups_lst)))
    return friends_groups_lst


def get_groups_info(groups_id, token):
    """Функция получает список id групп и токен,
    c помощью requests получает список данных по всем группам из groups_id.
    """

    print('Получение данных по секретным группам...')
    groups_lst = requests.get('https://api.vk.com/method/groups.getById',
                              params=dict(
                                  access_token=token,
                                  group_ids='{}'.format(",".join([str(gid) for gid in groups_id])),
                                  fields="members_count",
                                  v='5.80'
                                  )
                              )
    res_lst = []
    for group in groups_lst.json()['response']:
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


if __name__ == '__main__':
    print('********************************* START PROGRAMM *********************************\n'
          'Программа выяснит в каких группах, в которых состоит пользователь, нет его друзей.\n'
          '**********************************************************************************')
    # Получим config-данные ( токен, main_id
    TOKEN, main_id = get_config_data('valid_config.json', "token", "id")  # TODO: Изменить имя файла
    user_choise = ''
    while user_choise != 'quit' and user_choise != 'q':
        user_choise = input('Введите команду:\n'
                            'Начать подбор - введите "start"\n'
                            'Выйти - введите "quit" или "q"\n'
                            ).lower()
        if user_choise == 'start':
            # main_id = int(input('Введите идентификатор пользователя для подбора: '))  # Для ввода id с консоли

            user_friends_list = get_user_friends(TOKEN, main_id)["response"]["items"]
            print('Получение списка групп пользователя...')
            main_user_groups = get_user_groups(TOKEN, main_id)["response"]["items"]
            if main_user_groups:
                print('Успешно')

            secret_groups = set(main_user_groups) - set(get_friends_groups(TOKEN, user_friends_list))
            print('Кол-во обнаруженных секретных групп: {0}'.format(len(secret_groups)))
            secret_groups_info = get_groups_info(secret_groups, TOKEN)

            print('Сохранение данных...')
            with open('groups.json', 'w') as f:
                json.dump(secret_groups_info, f,
                          indent=4, ensure_ascii=False)
            if os.path.isfile("groups.json"):
                print('Данные успешно сохранены в файле groups.json')
            print('********************************* NEXT SELECTION *********************************')
