val = 42
if val < 0:
    print('Handled ErrorA')
elif val == 0:
    print('Value is zero, no error')
elif val > 100:
    print('Handled ErrorA')
else:
    print(f'Processing value: {val}')