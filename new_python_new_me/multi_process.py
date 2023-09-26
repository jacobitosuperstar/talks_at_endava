"""Threads and multiprocessing Python before 3.12. Looking at the past.

@https://github.com/jacobitosuperstar
"""

from typing import Generator, List
from concurrent.futures._base import Future
import concurrent.futures
from contextlib import contextmanager
import inspect
import threading
import time


# SOMETHING TO EXPLAIN IN THE FUTURE MAYBE

# class Task:
#     def __init__(self, gen: Generator):
#         self._gen = gen
#
#     def step(self, value=None):
#         try:
#             fut = self._gen.send(value)
#             fut.add_done_callback(self._wakeup)
#         except StopIteration as exc:
#             pass
#
#     def _wakeup(self, fut: Future):
#         result = fut.result()
#         self.step(result)


@contextmanager
def time_it(func_name: str) -> Generator[None, None, None]:
    t0 = time.monotonic()
    try:
        yield
    finally:
        print(f"{func_name} took {time.monotonic() - t0}")


def fibonacci(n) -> int:
    with time_it("fibonacci"):
        # Who is calling the function
        caller_frame = inspect.stack()[1]
        caller_name = caller_frame[3]
        print("Caller: ", caller_name)
        # In what thread am I in
        current_thread_id = threading.get_ident()
        print("Current Thread ID: ", current_thread_id)
        return 1 if n <= 2 else (fibonacci(n-1) + fibonacci(n-2))
    # return 1 if n <= 2 else (fibonacci(n-1) + fibonacci(n-2))


def main_single_thread(fib_number: int, callers: int) -> int:
    with time_it("** main_single_thread **"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            futures: List[Future[int]] = [
                pool.submit(fibonacci, fib_number)
                for _ in range(callers)
            ]

            for future in concurrent.futures.as_completed(futures):
                print(f"got {future.result()}")
    return 0


def main_threads(fib_number: int, callers: int) -> int:
    with time_it("** main_threads **"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures: List[Future[int]] = [
                pool.submit(fibonacci, fib_number)
                for _ in range(callers)
            ]

            for future in concurrent.futures.as_completed(futures):
                print(f"got {future.result()}")
    return 0


def main_multiprocess(fib_number: int, callers: int) -> int:
    with time_it("** main_multiprocess **"):
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
            futures: List[Future[int]] = [
                pool.submit(fibonacci, fib_number)
                for _ in range(callers)
            ]

            for future in concurrent.futures.as_completed(futures):
                # future.result()
                print(f"got {future.result()}")
    return 0


if __name__ == "__main__":

    FIBONACCI_NUMBER = 0
    NUMBER_OF_CALLERS = 1000

    main_single_thread(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
    main_threads(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
    main_multiprocess(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
