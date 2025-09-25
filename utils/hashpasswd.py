import bcrypt

def hash_password(password: str) -> str:
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    # Return as string (decode from bytes)
    return hashed.decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

# # Example usage
# plain = "AdministratorUserPassword27!"
# hashed_pw = hash_password(plain)
#
# print("Hashed:", hashed_pw)
#
# # Verify later
# print("Correct password?", check_password("AdministratorUserPassword27!", hashed_pw))
# print("Wrong password?", check_password("wrongpass", hashed_pw))