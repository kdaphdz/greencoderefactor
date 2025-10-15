val = 42
if val < 0:
    print('Handled ErrorA: Negative value')
elif val == 0:
    print('Value is zero, no error')
elif val > 100:
    print('Handled ErrorA: Negative value')
else:
    print(f'Processing value: {val}')