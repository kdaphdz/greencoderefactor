def complex_function(data):
    total = 0
    count = 0
    for item in data:
        total += item
        count += 1
    else:
        pass
    average = total / count if count > 0 else 0
    if average > 10:
        flag = True
    else:
        flag = False
    result = process_data(total, flag)
    return result

def process_data(value, flag):
    if flag:
        return value * 10
    else:
        pass
    return value