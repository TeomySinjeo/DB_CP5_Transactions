import psycopg2
from psycopg2 import Extras
import random

DB_CONFIG = {
    "dbname": "postgres", # Имя БД
    "user": "postgres",   # Нужно вписать ваш логин
    "password": "your_password", # И пароь для Postgres'а
    "host": "localhost",
    "port": "5432"
}

current_user_id = None
current_user_name = None
current_account_id = None
current_account_num = None

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def register():
    print("\nСоздать аккаунт")
    name = input("Введите имя: ")
    phone = input("Введите номер телефона: ")
    password = input("Введите пароль: ")
    account_num = "ACC" + str(random.randint(10000, 99999))

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, phone_number, password) VALUES (%s, %s, %s) RETURNING id;",
            (name, phone, password)
        )
        user_id = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO accounts (user_id, account_number, balance) VALUES (%s, %s, 1000.00);",
            (user_id, account_num)
        )
        
        conn.commit()
        print(f"Создан счет! {account_num}. Бесплатно начислено 1000 руб за создания нового аккаунта!")
    except Exception as e:
        conn.rollback()
        print("Ошибка, возможно такой телефон уже зарегестрирован", e)
    finally:
        cursor.close()
        conn.close()

def login():
    global current_user_id, current_user_name, current_account_id, current_account_num
    print("\nВход в аккаунт")
    phone = input("Введите свой номер телефона: ")
    password = input("Введите пароль: ")

    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT u.id, u.name, a.id, a.account_number 
        FROM users u
        JOIN accounts a ON u.id = a.user_id
        WHERE u.phone_number = %s AND u.password = %s;
    """
    cursor.execute(query, (phone, password))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if result:
        current_user_id, current_user_name, current_account_id, current_account_num = result
        main_page()
    else:
        print("Неверный телефон или пароль!")

def get_balance():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM accounts WHERE id = %s;", (current_account_id,))
    balance = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return balance

def make_transfer():
    print("\nТранзакции")
    receiver_num = input("Введите номер счета получателя: ")
    try:
        amount = float(input("Введите сумму перевода: "))
        if amount <= 0:
            print("Нельзя отправлять отрицательные числа >:(")
            return
    except ValueError:
        print("Некорректная сумма")
        return

    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT balance FROM accounts WHERE id = %s FOR UPDATE;", (current_account_id,))
        sender_balance = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM accounts WHERE account_number = %s FOR UPDATE;", (receiver_num,))
        receiver_res = cursor.fetchone()
        
        if not receiver_res:
            print("Получатель не найден!")
            return
        
        receiver_account_id = receiver_res[0]

        if sender_balance < amount:
            cursor.execute(
                "INSERT INTO transactions (sender_account_id, receiver_account_id, amount, status_id) VALUES (%s, %s, %s, 2);",
                (current_account_id, receiver_account_id, amount)
            )
            conn.commit()
            print("Недостаточно средств на вашем банковском аккаунте")
            return

        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s;", (amount, current_account_id))
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s;", (amount, receiver_account_id))
        cursor.execute(
            "INSERT INTO transactions (sender_account_id, receiver_account_id, amount, status_id) VALUES (%s, %s, %s, 1);",
            (current_account_id, receiver_account_id, amount)
        )
        
        conn.commit()
        print("Успешно!")
        
    except Exception as e:
        conn.rollback()
        print("Ошибка транзакции:", e)
    finally:
        cursor.close()
        conn.close()

def main_page():
    while True:
        print(f"\nДобро день, {current_user_name}! ")
        print(f"Ваш счет: {current_account_num}")
        print(f"Текущий баланс: {get_balance()} рублей")
        print("1) Перевести деньги")
        print("2) Выйти в главное меню")
        
        choice = input("Выберите действие: ")
        if choice == "1":
            make_transfer()
        elif choice == "2":
            break

def auth_menu():
    while True:
        print("\nTEO_BANK")
        print("1) Войти")
        print("2) Создать аккаунт")
        print("3) Выйти (из приложения)")
        
        choice = input("Выберите действие: ")
        if choice == "1":
            login()
        elif choice == "2":
            register()
        elif choice == "3":
            print("Хорошего дня!")
            break

if __name__ == "__main__":
    auth_menu()