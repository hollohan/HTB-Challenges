# WayWitch
- difficulty: very easy
- vulnerabilities: harcoded secret

## App Review
This web app consists of a single form and a couple of API endpoints.  The form is used for submitting tickets and has 2 fields, name and description.  A privileged user may access the /tickets API endpoint to view all tickets that have been submitted.

## Code Review
The first thing I generally like to look at is where the flag is.  In this case I can see that it is being input into the tickets table of the db.

```
// filename src/database.js

let flag;
    fs.readFile("/flag.txt", "utf8", function (err, data) {
      flag = data;
    });

// ...snip

await this.db.exec(`
          INSERT INTO tickets (name, username, content) VALUES
          ('John Doe', 'guest_1234', 'I need help with my account.'),
          ('Jane Smith', 'guest_5678', 'There is an issue with my subscription.'),
          ('Admin', 'admin', 'Top secret: The Halloween party is at the haunted mansion this year. Use this code to enter ${flag}'),
          ('Paul Blake', 'guest_9012', 'Can someone assist with resetting my password?'),
          ('Alice Cooper', 'guest_3456', 'The app crashes every time I try to upload a picture.');
      `);
```

Following the code, I can see that the /tickets API endpoint shows all submitted tickets to a privileged user.  A user is deemed privileged if the username obtained from the session_token cookie is 'admin'.  When a user access the /tickets API endpoint the session_token cookie is sent to the ```getUsernameFromToken``` function for verification.  The jwt verification function is configured to use a hardcoded secret 'halloween-secret'.
```
// filename: src/utils.js

function getUsernameFromToken(token) {
  const secret = "halloween-secret";

  try {
    const decoded = jwt.verify(token, secret);
    return decoded.username;
  } catch (err) {
    throw new Error("Invalid token: " + err.message);
  }
}
```
The next question is whether or not the live target is using the same secret.  To confirm this I fired up the live target, crafted an HS256 JWT token with a secret 'halloween-secret', included the username admin within its data, and sent it to the /tickets API endpoint.  Sure enough, the cookie was accepted and all tickets were sent back, including the ticket containing the flag.

## Attack
Craft an HS256 JWT token using the secret 'halloween-secret' with the data ```{"username":"admin"}```.  Send a request to the /tickets API endpoint and the flag will be revealed in the response.

## Mediation
Ideally the app would want to make sure to use a hard to guess secret that is not hard coded.  I commonly see this accomplished by generating a random secret at runtime.  Another common approach is to generate or store a secret outside ot the scope of the app and feed it to the app via environment variables.  It's also a good idea to explicitly state the algorithm in the verify(and encode) function.  In this case 'HS256'.
```
const crypto = require('crypto');
crypto.randomBytes(32).toString('hex');
```