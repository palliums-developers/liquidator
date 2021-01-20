def new_mantissa(a, b):
    c = a << 64
    d = b << 32
    e = c // d
    return int(e)


def mantissa_div(a, b):
    c = a << 32
    d = c // b
    return int(d)


def mantissa_mul(a, b):
    c = a * b
    d = c >> 32
    return int(d)


def safe_sub(a, b):
    if a < b:
        return 0
    return a - b
