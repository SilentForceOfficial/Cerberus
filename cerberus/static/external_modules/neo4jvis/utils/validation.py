import re

# https://www.geeksforgeeks.org/how-to-validate-hexadecimal-color-code-using-regular-expression/
def validate_hex_color(str):
    ERROR_MSG = "Parameter must be a 6 digit hexadecimal color code preceded by '#' (e.g. \"#FF2400\"). Current value " \
                "is '{param}' "
    REGEX = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    p = re.compile(REGEX)
    # If the string is empty
    if (str == None):
        raise AttributeError(ERROR_MSG.format(param=str))
    # did not match the ReGex
    if not re.search(p, str):
        raise AttributeError(ERROR_MSG.format(param=str))

def validate_positive_integer(param):
    if not isinstance(param, int):
        raise AttributeError(f"Parameter must be of type 'int'. Current type is '{type(param)}'")
    if param <= 0:
        raise AttributeError(f"Parameter must be greater than 0. Current value is '{param}'")