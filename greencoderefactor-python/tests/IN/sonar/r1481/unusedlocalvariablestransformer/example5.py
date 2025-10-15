def complex_function(data):
    total = 0
    temp = 0
    count = 0
    unused_var = 99

    for item in data:
        intermediate = item * 2
        total += item
        count += 1

    average = total / count if count > 0 else 0

    if average > 10:
        flag = True
        unused_flag = False
    else:
        flag = False

    result = process_data(total, flag)

    return result

def process_data(value, flag):
    if flag:
        return value * 10
    return value
