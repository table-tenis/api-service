import argon2
from argon2.exceptions import VerifyMismatchError
class HashPassword:
    argon2Hasher = argon2.PasswordHasher(
        time_cost=3, # number of iterations
        memory_cost=64 * 1024, # 64mb
        parallelism=1, # how many parallel threads to use
        hash_len=32, # the size of the derived key
        salt_len=16 # the size of the random generated salt in bytes
        )
    def create_hash(self, password: str):
        return self.argon2Hasher.hash(password)

    def verify_hash(self, plain_password: str, hashed_password: str):
        try:
            res = self.argon2Hasher.verify(hashed_password, plain_password)
            return res
        except VerifyMismatchError as e:
            return False
        