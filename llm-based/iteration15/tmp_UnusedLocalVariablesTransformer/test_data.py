import pytest
from process_data import process_data
from itertools import product

xs = [0, 1, 2, 3, 4, 5]
data_sizes = [10**6, 10**7]

@pytest.mark.parametrize("x,data_size", list(product(xs, data_sizes)))
def test_process_data_benchmark(benchmark, x, data_size):
    data = list(range(data_size))
    benchmark(process_data, x, data)