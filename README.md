# CLI engine

This is an small python project in which I developed an small engine to create interactive CLIs for your programs quickly

The package works due to the session object.

to create your own interface just create an object that inherits from the `BaseSession` object and add your commands as methods of the object. Then create an instance of the object and execute the method `BaseSession.start()` and the interactive CLI should start.
The commands are set to be the names of the methods you added to the object. Whatever you pass after the method name are the arguments that your method will receive:

```Python
from CLIengine import BaseSession

class session(BaseSession):
    def sum_numbers(self, *numbers):
        print(sum(numbers))

instance = session()
instance.start()
```

```CMD
interactive session started.
>>> sum_numbers 1 2 3 4.5 7
17.5
>>>
```

The engine parses automatically the arguments for the commands as python objects using a safer version the eval function (has as globals the commands available and the built in functions).

you can change the eval function for one that suits better your program.

```Python
instance.set_eval(my_eval_function):
```

The parser works decently for most python expressions but still presents some issues to be fixed in future versions:

- The parser does not work correctly for operations that include spaces outside of `{}`,`()`,`[]` or `""` symbols like `1 - 2` or `A or B`. Using expressions like those should raise a `SyntaxError` because the program would apply the `eval` function to each character or group of characters separated by spaces.
- you can put python expressions as arguments but they only work with one level of nesting.
