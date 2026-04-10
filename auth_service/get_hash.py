import bcrypt
password = input("Пароль: ").encode()
print(bcrypt.hashpw(password, bcrypt.gensalt()).decode())