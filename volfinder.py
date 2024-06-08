''' Импорт библиотек '''

import requests
import random
import string
import secrets


''' Определение функций '''

# Устанавливает переменную в true если она не равна нулю (или false, если равна)


def convert_to_boolean(variable):
    return not not variable


# Генерирует случайную строку, включающую в себя любые символы


def randstr(length):
    symbols = string.ascii_letters + string.digits + \
        string.punctuation + string.whitespace
    return ''.join(random.choice(symbols) for _ in range(length))


# Проверяет сайт на уязвимость к sql инъекциям, сравнивая коды ответа до и после


def sql_injection_check(default_req, login_field, password_field):
    injected_req = requests.post(default_req.url, data={
        login_field: "' OR 1=1--", password_field: "' OR 1=1--"})
    return default_req.status_code != injected_req.status_code


# Посылает на сайт случайные данные в области логина и пароля


def phaser(failure_req, amount, login_field, password_field):
    # Максимальная длинна логина и пароля (в некоторых стандартах минимальный пароль это 15 символов)
    max_length = 15
    first_status_code = failure_req.status_code

    while failure_req.status_code == first_status_code and amount > 0:
        phased_login = randstr(secrets.randbelow(max_length))
        phased_password = randstr(secrets.randbelow(max_length))
        failure_req = requests.post(failure_req.url,  data={
            login_field: phased_login,
            password_field: phased_password
        })
        amount -= 1

    print(f"#[PHASER]: \
            Status code = {failure_req.status_code} \
            random_login = {phased_login}  \
            random_passsword = {phased_password}")
    return convert_to_boolean(amount)


'''Определение переменных'''

url = input("Please, input login url: ")  # Ссылка на страницу аутентификации
# Имя заголовка, в котором хранится логин
login_field = input("Input login field: ")
# Имя заголовка, в котором хранится пароль
password_field = input("Input password field: ")
phaser_tries = int(input(
    "How much random data injects you want to do? Type 0 if you don't want to: "))  # Количество итераций фазера
# (если ввести 0 или меньше, то фазер не будет работать)

# Заведомо неверные идентификационные данные
wrong_login, wrong_passsword = "hello", "world"
req = requests.post(url, data={  # Запрос на сайт, с использованием этих данных
    login_field: wrong_login,
    password_field: wrong_passsword
})


''' Выполнение кода '''

# В случае успешного прохождения аунтентификации сайт не имеет должных требований к сложности пароля
if req.status_code == 200:
    print("The site lacks sufficient password security.")

# В случае выдачи внутренней ошибки, пользователь ввёл неверные названия заголовков
elif 500 <= req.status_code <= 599:
    print("Entered data is incorrect")

# Проверка на уязвимость к sql инъекциям
if sql_injection_check(req, login_field, password_field):
    print("Site have a sql-injection vulnerability")

# Фазинг сайта
if phaser_tries > 0 and phaser(req, phaser_tries, login_field, password_field):
    print("Site is vulnerable for phasing")
