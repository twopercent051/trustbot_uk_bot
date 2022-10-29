import asyncio


async def user_name_checker(name):
    flag = True
    if name.count(' ') != 1:
        flag = False
    alphabet = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя ')
    for c in name.lower():
        if c not in alphabet:
            flag = False
            break
    for word in name.split(' '):
        if word.istitle() == False:
            flag = False
    return flag


async def user_phone_checker(phone):
    flag = True
    if len(phone) != 12:
        flag = False
        print(1)
    if phone[0:2] != '+7':
        flag = False
        print(2)
    if phone[2:].isdigit() == False:
        flag = False
        print(3)
    return flag

