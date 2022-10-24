"""
ENDAVA 2022
Threads Async and Python

found at:
github.com/jacobitosuperstar/...
"""


def fibonacci(number:int) -> int:
    """
    :type n => int
    :params n => número al que le vamos a hacer factorial

    Devuelve el número de fibonacci
    """
    if number <= 2:
        return 1
    return fibonacci(number-1) + fibonacci(number-2)
