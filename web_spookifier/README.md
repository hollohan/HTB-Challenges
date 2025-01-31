# Spookifier
- difficulty: very easy
- vulnerabilities: SSTI

## App Review
This app is extremely simple.  There is a single page with a single input field.  The user types some text into the input field and the app outputs the same text in 4 different fonts.

## Code Review

### Summary
- flask app
- single path with a single paramter, text
- the input text gets sent to the ```spookify``` function
- the ```spookify``` returns a valuse that then gets sent to a template, index.html, and rendered

### spookify()
The ```spookify``` function takes the text that was provided as an argument and sends it to the ```change_font``` function.  It then sends the result to the ```generate_render``` function.

### change_font()
The first thing that happens in the ```change_font``` function is that the ```text_list``` argument, which is the original user input string, gets converted into a list of characters.  A lambda function is then defined and assigned to ```add_font_to_list```.
```
add_font_to_list = lambda text,font_type : (
	[current_font.append(globals()[font_type].get(i, ' ')) for i in text], all_fonts.append(''.join(current_font)), current_font.clear()
	) and None
```
The lambda function takes 2 arguments, ```text``` and ```font_type```.  The lambda function essentially does these 2 things:
- iterates the characters in ```text``` and looks each one up in the corresponding ```font_type``` dict defined earlier in the code.
- appends the result into ```all_fonts```

The lambda function is called for each one of the fonts defined earlier in the code, providing the font type and the ```text_list``` argument.

### generate_render()
This is where things get interesting.  The ```generate_render``` function takes each one of the 4 fonts that were calculated in the ```change_font``` function and inputs them into a string, ```result```.  The result provided as an argument to ```mako.Template```.
```
Template(result).render()
```
The problem here is that the fonts, which were crafted from user input, are put directly into the template, before it is rendered.  This allows an attacker to provide specially crafted input that will be interpretted by the template engine.

## Attack
The first thing I like to do is confirm the vulnerability.  I can do this with a simple template injection that performs a math equation.  In this case I can provide the input ${4\*4}, which the Mako template engine will interpret the input as an expression substitution and return the result of 4\*4 which is 16.  Using the URL below, I can see 16 in the result which confirms that a SSTI vulnerability exists.
```
http://localhost:1337/?text=${4*4}
```
According to the Mako docs, 'The contents within the ${} tag are evaluated by Python directly' which means I should be able to drop in some python to read the flag.txt file and return its contents.
```
http://localhost:1337/?text=${open(%27/flag.txt%27,%27r%27).read()}
```
Using the URL above works as expected and the flag is revealed within the contents of the page.
## Mediation
In order to resolve this issue the template needs to be proplery formated with ${} tags and then sent to the template engine along with the arguments passed to the ```render``` function.  By doing this the arguments will not be interpretted as part of the template.  The updated ```generate_render``` below will prevent the issue from occurring.
```
def generate_render(converted_fonts):
	result = '''
		<tr>
			<td>${font0}</td>
		</tr>

		<tr>
			<td>${font1}</td>
		</tr>

		<tr>
			<td>${font2}</td>
		</tr>

		<tr>
			<td>${font3}</td>
		</tr>
	'''
	
	return Template(result).render(
		font0=converted_fonts[0],
		font1=converted_fonts[1],
		font2=converted_fonts[2],
		font3=converted_fonts[3]
	)
```