import re

PARAM_REGEX = re.compile("{([a-zA-Z_][a-zA-Z0-9_]*)(:[a-zA-Z_][a-zA-Z0-9_]*)?}")
PATH = "/user/{user_name:str}"

for match in PARAM_REGEX.finditer(PATH):
    param_name, _type = match.groups("str")  # this returns a tuple
    print(param_name, _type)
