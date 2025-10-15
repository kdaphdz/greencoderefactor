def test_function(x):
    if x == 0:
        print('Handled ErrorA or ErrorB')
    elif x == 1:
        print(f'Handled ErrorB or ErrorC')
    elif x == 2:
        print(f'Handled ErrorB or ErrorC')
    else:
        print('No error')
if __name__ == '__main__':
    for i in range(4):
        test_function(i)