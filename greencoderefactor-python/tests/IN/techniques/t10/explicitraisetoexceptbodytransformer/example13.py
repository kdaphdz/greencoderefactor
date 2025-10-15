class ErrorA(Exception):

    def __init__(self, message):
        super().__init__(message)

try:
    val = 42
    if val < 0:
        raise ErrorA("Negative value error")
    elif val == 0:
        print("Value is zero, no error")
    elif val > 100:
        raise ErrorA("Value too large")
    else:
        print(f"Processing value: {val}")
except ErrorA as exception:
    print("Handled ErrorA: Negative value")
