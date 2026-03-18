import hashlib
import secrets
import bcrypt

texte = "coucoudu13"

hash_object = hashlib.sha512(texte.encode())
print(hash_object.hexdigest())

salt = secrets.token_hex(16)
password = input("")
