# NEW PYTHON NEW ME

## New Person Same Old Mistakes

Python presentation, about the past, the present and the future for
concurrency.

**Requirements**: This is an advanced topic and it assumes general awarness of
core Python language features and basic understanding of concurrency and
parallellism.

**Will I Be Lost?**: Not really, we can go a bit deeper, but understand that
this is just a surface level explanation and we are currently focused on
specific cases so the complete picture won't be in here. Take as a though
excersice of what it was and whats comming.

### Starting

The fundamental problem that the core python developers are trying to address
with all of this changes regarding the GIL is concurrency and parallellism. The
GIL or the global interpreter lock is a mechanism used by the CPython
Interpreter to assure that only one thread at a time executes Python bytecode,
simplifiying the implementation and making the object model of CPython safe
against concurrent access.

This implementation besides simplicity, gives us two main benefits, one, is it
easier to create multithreaded programs, two, single core single process
performance.

After all of this, we must ask ourselves, how threads work then, if only one
can be executed at a time, how does python manage them, and how is their
execution.

```python

from typing import Generator, List
from concurrent.futures._base import Future
import concurrent.futures
from contextlib import contextmanager
import inspect
import threading
import time


@contextmanager
def time_it(func_name: str) -> Generator[None, None, None]:
    t0 = time.monotonic()
    try:
        yield
    finally:
        print(f"{func_name} took {time.monotonic() - t0}")


def fibonacci(n: int) -> int:
    with time_it("fibonacci"):
        # Who is calling the function
        caller_frame = inspect.stack()[1]
        caller_name = caller_frame[3]
        print("Caller: ", caller_name)
        # In what thread am I in
        current_thread_id = threading.get_ident()
        print("Current Thread ID: ", current_thread_id)
        return 1 if n <= 2 else (fibonacci(n-1) + fibonacci(n-2))
```

What we are going to do, is to calculate the Fibonacci number and with the
context manager, we are just going to time its execution, and we are going to
create a function that even tho will use two threads, the main execution thread
and the concurrent.futures thread, is going to be called single threaded,
because for all intents and purposes we are just going to generate one worker
that will do all the calculations and the main thread will just send the jobs.

```python

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


if __name__ == "__main__":

    FIBONACCI_NUMBER = 10
    NUMBER_OF_CALLERS = 1000
    main_single_thread(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)

```

Checking the results of the code

```log
.
.
.
Caller:  run
Current Thread ID:  6174011392
Caller:  fibonacci
Current Thread ID:  6174011392
Caller:  fibonacci
Current Thread ID:  6174011392
Caller:  fibonacci
Current Thread ID:  6174011392
Caller:  fibonacci
Current Thread ID:  6174011392
Caller:  fibonacci
Current Thread ID:  6174011392
Caller:  fibonacci
Current Thread ID:  6174011392
Caller:  fibonacci
Current Thread ID:  6174011392
Caller:  fibonacci
Current Thread ID:  6174011392
fibonacci took 0.000337416997354012
Caller:  fibonacci
Current Thread ID:  6174011392
fibonacci took 0.000338707999617327
fibonacci took 0.0010033329963334836
Caller:  fibonacci
Current Thread ID:  6174011392
fibonacci took 0.0002764589953585528
fibonacci took 0.0014007499994477257
fibonacci took 0.0044409160036593676
.
.
.

** main_single_thread ** took 22.205854708001425
```

What we can see, is a glipmse into the main problem that Python has with
threads. We are constantly switching the context of the execution, between the
sender of the job and the executor of the job.

Lets see what would happen if we were to send that same work, but into more
threads.

```python

def main_threads(fib_number: int, callers: int) -> int:
    with time_it("** main_threads **"):
        # with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            futures: List[Future[int]] = [
                pool.submit(fibonacci, fib_number)
                for _ in range(callers)
            ]

            for future in concurrent.futures.as_completed(futures):
                print(f"got {future.result()}")
    return 0

if __name__ == "__main__":
    main_threads(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)

```

Checking the results of the execution

```log
.
.
.
Caller:  fibonacci
Current Thread ID:  6258143232
Caller:  fibonacci
Current Thread ID:  6207664128
Caller:  fibonacci
Current Thread ID:  6174011392
Caller:  fibonacci
Current Thread ID:  6342275072
fibonacci took 0.0018045839970000088
fibonacci took 0.007808833004673943
fibonacci took 0.027563333002035506
fibonacci took 0.08748895899771014
fibonacci took 0.26857920800102875
Caller:  fibonacci
Current Thread ID:  6291795968
fibonacci took 0.0035573749992181547
Caller:  fibonacci
Current Thread ID:  6359101440
fibonacci took 0.0022504169974126853
Caller:  fibonacci
Current Thread ID:  6258143232
Caller:  fibonacci
Current Thread ID:  6190837760
Caller:  fibonacci
Current Thread ID:  6342275072
Caller:  fibonacci
Current Thread ID:  6207664128
Caller:  fibonacci
Current Thread ID:  6308622336
Caller:  fibonacci
Current Thread ID:  6174011392
Caller:  fibonacci
Current Thread ID:  6359101440
fibonacci took 0.0022661249968223274
fibonacci took 0.00666116699721897
fibonacci took 0.025756208997336216
fibonacci took 0.08154754200222669
.
.
.

** main_threads ** took 38.50530683300167
```

It is even more complex. Looks like the threads are fighting for the
Interpreter to calculate the fibonacci number. And as we can see, that fighting
over the interpreter has a cost. The main threaded process took longer, even
tho the calculation took the same ammount of time.

Is there a way then, to side step all of this problems, so that our code can
run in parallel and pass the limitations of the Interpreter that locks us into
a single core execution?
