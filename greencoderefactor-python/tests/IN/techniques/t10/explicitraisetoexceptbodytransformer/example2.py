N = 10000000
data = [i for i in range(N)]

class MyException(Exception):
    def __init__(self, message):
        super().__init__(message)

def process_data(x, data):
    result = [0] * len(data)
    for i in range(len(data)):
        try:
            if x == 1:
                result[i] = data[i] * 2
            else:
                raise MyException("x is not 1")
        except MyException:
            result[i] = data[i] * 3
    return result

if __name__ == "__main__":
    process_data(2, data)
