def is_str(value: object) -> bool:
    return isinstance(value, str)

def is_bytes(value: object) -> bool:
    return isinstance(value, bytes)


def final(func: object) -> object:
    def wrap(*args, **kwargs):
        pass
    return wrap
