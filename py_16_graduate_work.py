import requests
import time
from urllib.parse import urlencode

TOKEN = '7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b7d9fb59859870658c4a0b8fdc4dd494db19099'
VK_URL = 'https://vk.com/'


if __name__ == '__main__':
    print('********** START PROGRAMM **********')
    # main_id = int(input('Введите идентификатор пользователя для подбора: '))  # Для ввода id с консоли
    main_id = 171691064
    params = {
        'access_token': TOKEN,
        'v': '5.80'
    }
    # Получим список друзей пользователя
    response = requests.get('https://api.vk.com/method/friends.get', params)
    # print(response.json()["response"])
    print('Всего друзей:', response.json()["response"]["count"])
    friends_id_list = response.json()["response"]["items"]
    print('Список ID друзей пользователя:\n', friends_id_list)

    print('===============')
    # Получим список групп пользователя
    params['user_id'] = main_id
    response = requests.get('https://api.vk.com/method/friends.get', params)
    print('Кол-во групп, в которых состоит пользователь: ', response.json()["response"]["count"])
    # print(response.json()["response"]["items"])
    groups_main_user = response.json()["response"]["items"]
    # print("Groups list: \n", groups_main_user)

    print('===============')
    # Получим список групп друзей пользователя
    сommon_list_of_friends_groups = []  # Задали список, в который будем сохранять все группы друзей
    for friend_id in friends_id_list[20:50]:  # Для отладки сделал срез 40 первый друзей
        params['user_id'] = friend_id
        print(' . ', end=' ')
        response = requests.get('https://api.vk.com/method/friends.get', params)
        time.sleep(0.35)
        # print(response.json())
        # ДОБАВИТЬ ПРОВЕРКУ существует ли вообще список групп, так решим проблему
        # с удаленными или заблокированными пользователями!!!!!
        if 'error' in response.json():
            continue
        elif response.json()["response"]["items"]:
            if len(response.json()["response"]["items"]) > 1:
                for group_id in response.json()["response"]["items"]:
                    сommon_list_of_friends_groups.append(group_id)
            else:
                сommon_list_of_friends_groups.append(response.json()["response"]["items"])
    # print('сommon_list_of_friends_groups', сommon_list_of_friends_groups)
    print("Собрали список всех групп, в которых состоят друзья пользователя.\n Кол-во групп: {0}".format(
         len(сommon_list_of_friends_groups)))
    print('Получим множество групп из общего списка.')
    common_set_groups = set(сommon_list_of_friends_groups)
    print('Всего групп: {0}'.format(len(common_set_groups)))
    # Узнаем в каких группах состоит только пользователь, но ни один из его друзей.
    # Преобразуем список групп пользователя во множество:
    main_user_groups_set = set(groups_main_user)
    print('main_user_groups_set', main_user_groups_set)
    print('Получим группы пользователя, в которых нет его друзей:\n {0}'.format(main_user_groups_set - common_set_groups))
    print('Кол-во групп: {0}'.format(len(main_user_groups_set - common_set_groups)))
    res_group_lst = list(main_user_groups_set - common_set_groups)
    print('Сделали из множества список длинной: {0} элемента.'.format(len(res_group_lst)))
    # Далее по списку проходимся и делаем запрос для получения информации о группе:
    # (Название, идентификаор, кол-во участников)
    











