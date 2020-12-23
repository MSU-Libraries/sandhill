from sandhill.processors import general


def test_random_number():
    num = general.random_number({})
    assert isinstance(num, int)
    assert general.random_number({}) != num

    num2 = general.random_number({})
    assert isinstance(num2, int)
    assert general.random_number({'some':'dict'}) != num
    assert general.random_number([]) != num2
    assert num != num2

