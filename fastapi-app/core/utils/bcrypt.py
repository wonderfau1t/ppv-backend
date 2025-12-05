import bcrypt


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()


def check_password(password: str, hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), hash.encode())
