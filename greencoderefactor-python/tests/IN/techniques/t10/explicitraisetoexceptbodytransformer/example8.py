class MyException(Exception):
    def __init__(self, message):
        super().__init__(message)

print("test")
try:
    print("a")
    print("b")
    raise MyException("x is not 1")
except MyException:
    print("Handled ErrorA: Negative value")
