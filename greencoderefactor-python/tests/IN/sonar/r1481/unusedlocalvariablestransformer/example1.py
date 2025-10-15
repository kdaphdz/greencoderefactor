def calculate_total(prices):
    total = 0  # Se usa, correcto

    for price in prices:
        temp = price * 0.9  # Asignación no usada: 'temp' nunca se usa
        total += price

    unused_var = 42  # Nunca se usa en el código

    return total
