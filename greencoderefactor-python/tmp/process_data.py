from operations import operate

def process_data(x, data):
    result = [0] * len(data)
    for i in range(len(data)):
        if x == 1:
            result[i] = data[i] * 2
        else:
            result[i] = data[i] * 3
    operate()
    return result