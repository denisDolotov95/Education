import memory_profiler

# манипуляция количеством циклов
RANGE = 100000
# манипуляция количеством данных
MULTIPLY = 10000
# путь для хранения логов
PATH = "./logs"


@memory_profiler.profile(stream=open(f"{PATH}/test_memory_dict.log", "w+"))
def test_memory_dict():
    """Как выделяется память и утилизируется
    в генераторах словарей в python3
    """

    # создаем итератор словарей
    _data = {i: f"{i}" * MULTIPLY for i in range(RANGE)}

    print(type(_data))
    for i in _data:
        pass


@memory_profiler.profile(stream=open(f"{PATH}/test_memory_set.log", "w+"))
def test_memory_set():
    """Как выделяется память и утилизируется
    в генераторах множеств в python3
    """

    # создаем итератор множества
    _data = {f"{i}" * MULTIPLY for i in range(RANGE)}

    print(type(_data))
    for i in _data:
        pass


@memory_profiler.profile(stream=open(f"{PATH}/test_memory_list.log", "w+"))
def test_memory_list():
    """Как выделяется память и утилизируется
    в генераторах списка в python3
    """

    # создаем итератор списков
    _data = [f"{i}" * MULTIPLY for i in range(RANGE)]

    print(type(_data))
    for i in _data:
        pass


@memory_profiler.profile(stream=open(f"{PATH}/test_memory_tuple.log", "w+"))
def test_memory_tuple():
    """Как выделяется память и утилизируется
    под кортежи в python3
    """

    # создаем итератор кортежей
    _data = tuple(f"{i}" * MULTIPLY for i in range(RANGE))

    print(type(_data))
    for i in _data:
        pass


@memory_profiler.profile(stream=open(f"{PATH}/test_memory_gen.log", "w+"))
def test_memory_gen():
    """Как выделяется память и утилизируется
    под генераторы в python3
    """

    # # создаем генератор
    # def _data():
    #     for i in range(RANGE):
    #         yield "3" * (MULTIPLY)

    # создаем генератор
    _data = (f"{i}" * MULTIPLY for i in range(RANGE))

    print(type(_data))
    # итерируем по генератору
    for i in _data:
        pass


if __name__ == "__main__":

    test_memory_tuple()
    test_memory_list()
    test_memory_dict()
    test_memory_set()
    test_memory_gen()
