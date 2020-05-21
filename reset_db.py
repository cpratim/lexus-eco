import os
from logistics import Logistics
from auth import Authentication

os.remove('auth.db')
os.remove('logistics.db')
print('deleted')
os.mknod('auth.db')
os.mknod('logistics.db')
print('created')

Authentication('auth.db', _init=True)
Logistics('logistics.db', _init=True)

print("Reset Complete")