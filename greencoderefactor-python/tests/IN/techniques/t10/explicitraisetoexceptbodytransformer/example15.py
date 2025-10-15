class ErrorA(Exception):
    pass

class ErrorB(Exception):
    pass

class ErrorC(Exception):
    pass

def test_function(x):
    try:
        if x == 0:
            raise ErrorA("Error A occurred")
        elif x == 1:
            raise ErrorB("Error B occurred")
        elif x == 2:
            raise ErrorC("Error C occurred")
        else:
            print("No error")
    except (ErrorA, ErrorB):
        print("Handled ErrorA or ErrorB")
    except (ErrorB, ErrorC):
        print(f"Handled ErrorB or ErrorC")

if __name__ == "__main__":
    for i in range(4):
        test_function(i)
