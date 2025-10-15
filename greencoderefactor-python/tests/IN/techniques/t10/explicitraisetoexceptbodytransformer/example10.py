class ErrorA(Exception):
    def __init__(self, message):
        super().__init__(message)

try:
    if True:
        raise ErrorA()
except ErrorA:
    print("ErrorA")
