class ErrorC(Exception):
    pass

def test_function(x):
    try:
        if x == 0:
            print('Handled ErrorA or ErrorB')
        elif x == 1:
            print('Handled ErrorA or ErrorB')
        elif x == 2:
            raise ErrorC('Error C occurred')
        else:
            print('No error')
    except ErrorC as exception:
        print(f'Handled ErrorB or ErrorC {exception}')
if __name__ == '__main__':
    for i in range(4):
        test_function(i)