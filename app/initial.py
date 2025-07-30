import re
import warnings
from functools import partial
from typing import Callable, Optional

command_syntax = re.compile(
    r"^(?P<command_name>[a-zA-Z0-9_]+)"  # Command name (at least one letter or number)
    r"(?:(?: +)-(?P<flags>[a-zA-Z0-9]+))?"  # Optional flags (space, '-', then letters/numbers)
    r"(?: +(?P<arguments>.*))?$"  # Optional arguments (space, then any characters until end of line)
)

# TODO fix the matching for nested brackets (allows only one level)
argument_syntax = re.compile(
    r"""
    '[^']*'                                 # Matches single quoted strings
    |"[^"]*"                                # Matches double quoted strings
    |\S+\((?:[^()]|\([^()]*\))*\)           # Matches a word followed by parentheses, allowing nested parentheses
    |\{(?:[^{}]|\{[^{}]*\})*\}              # Matches curly braces, allowing one level of nested curly braces
    |\[(?:[^\[\]]|\[[^\[\]]*\])*\]          # Matches square brackets, allowing one level of nested square brackets
    |\((?:[^()]|\([^()]*\))*\)              # Matches standalone parentheses, allowing one level of nested parentheses
    |\S+                                    # Matches any sequence of non-whitespace characters (fallback)
    """, re.VERBOSE
)

class BaseSession:
    def __init__(self, eval_function:Optional[Callable]=None):
        self.run= False
        self.init_commands()
        self.init_eval(eval_function)

    def init_commands(self):
        base_methods = ['__class__', '__delattr__', '__dict__', '__dir__',
                        '__doc__', '__eq__', '__firstlineno__', '__format__',
                        '__ge__','__getattribute__', '__getstate__', '__gt__',
                        '__hash__', '__init__', '__init_subclass__', '__le__',
                        '__lt__','__module__', '__ne__', '__new__',
                        '__reduce__','__reduce_ex__', '__repr__',
                        '__setattr__', '__sizeof__','__static_attributes__',
                        '__str__', '__subclasshook__','__weakref__',
                        'commands', 'execute_command', 'parse_command',
                        'start', 'init_commands', 'init_eval', 'set_eval']
        
        self._command_functions = {}
        obj_methods = dir(self)
        for method in obj_methods:
            if method not in base_methods and callable(getattr(self, method)):
                self._command_functions[method] = getattr(self, method)

    def init_eval(self, eval_function:Optional[Callable]):
        if eval_function:
            self.set_eval(eval_function)
        else:
            safe_globals = self._command_functions.copy()
            safe_globals['__builtins__'] = __builtins__
            safe_eval = partial(eval, globals=self._command_functions)
            self.set_eval(safe_eval)

    def set_eval(self, func:Callable):
        """
        set the eval function tha is used to parse the arguments of a command.
        """
        self._eval = func

    def start(self):
        """
        this command starts the interactive session
        """
        print('\rinteractive session started.', flush=True)
        self.run = True
        while self.run:
            input_line = input()
            command = self.parse_command(input_line)
            if command:
                self.execute_command(command)
                
        print('interactive session ended.')
            
    def exit(self):
        self.run = False

    def parse_command(self, input_line:str):
        """
        Parses a string that represents a command and returns a dict
        containing the command name, arguments (as a string) and flags.
        """
        command_match = re.match(command_syntax, input_line)
        # TODO commands that do not exist also match causing runtime errors
        if command_match:
            command_dic = command_match.groupdict()
            return command_dic
        else:
            warnings.warn(f"The command '{input_line}' uses an unsupported command name or an invalid syntax", SyntaxWarning)
    
    def parse_args(self, args:Optional[str]):
        if args:
            args = map(self._eval, argument_syntax.findall(args))
            return tuple(args)
        else:
            return None

    def execute_command(self, command_dic:dict):
        """
        This method takes the a command dictionary (dictionary containing the 
        command, its arguments and flags) then looks up the command in the 
        """
        # TODO flags are not well implemented yet
        command = command_dic.get('command_name')
        command_function:Callable = self._command_functions[command]
        args_string:str = command_dic.get('arguments',[])
        args = self.parse_args(args_string)
        flags:str = command_dic.get('flags','')
        
        if not args and not flags:
            return command_function()
        elif not args:
            return command_function(flags)
        elif not flags:
            return command_function(*args)
        else:
            return command_function(*args, flags)



if __name__ == '__main__':
    class session(BaseSession):
        def sum_numbers(self, *numbers):
            print(sum(numbers))

    inst = session()
    inst.start()
    pass