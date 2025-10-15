val = 42
if val < 0:
    print('Handled ErrorA: Negative value')
elif val == 0:
    print('Value is zero, no error')
elif val > 100:
    print('Handled ErrorB: Value too large')
else:
    if val == 42:
        print('Handled ErrorC: Forbidden value 42')
    print(f'Processing value: {val}')