class ErrorA(Exception):
    pass

class ErrorB(Exception):
    pass

class ErrorC(Exception):
    pass

try:
    val = 42
    if val < 0:
        raise ErrorA("Negative value error")
    elif val == 0:
        print("Value is zero, no error")
    elif val > 100:
        raise ErrorB("Value too large")
    else:
        if val == 42:
            raise ErrorC("Value cannot be 42")
        print(f"Processing value: {val}")
except ErrorA:
    print("Handled ErrorA: Negative value")
except ErrorB:
    print("Handled ErrorB: Value too large")
except ErrorC:
    print("Handled ErrorC: Forbidden value 42")
