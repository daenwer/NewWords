from collections import OrderedDict, namedtuple


Choice = namedtuple('Choise', ['code', 'name'])
_OrderedChoice = namedtuple('OrderedChoice', ['code', 'name', 'order'])


class OrderedChoice:
    def __new__(cls, code, name, order=0):
        return _OrderedChoice(code, name, order)


class Choices:
    @classmethod
    def get_all(cls, return_objects=False):
        result = []
        for element in dir(cls):
            if not element.startswith('_') and \
                    not callable(getattr(cls, element)):
                value = getattr(cls, element)
                if return_objects:
                    result.append(value)
                elif isinstance(value, Choice):
                    result.append([value.code, value.name, 0])
                elif isinstance(value, _OrderedChoice):
                    result.append([value.code, value.name, value.order])
                else:
                    result.append([value] * 3)
        return [
            value if return_objects else (value[0], value[1]) for value
            in sorted(
                result,
                key=lambda v: (v[2], v[1]) if len(v) > 2 else v[1]
            )
        ]

    @classmethod
    def get_list(cls):
        result = []
        for element in dir(cls):
            if not element.startswith('_') and \
                    not callable(getattr(cls, element)):
                value = getattr(cls, element)
                result.append(
                    value.code if isinstance(value, Choice) else value
                )
        return sorted(result)


class RepetitionRate(Choices):
    fast = Choice('fast', 'Fast')
    normal = Choice('normal', 'Normal')
