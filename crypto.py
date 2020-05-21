import hashlib

def hash_(plain):
	hash_object = hashlib.sha256(plain.encode('utf-8'))
	hex_dig = hash_object.hexdigest()
	return str(hex_dig)

