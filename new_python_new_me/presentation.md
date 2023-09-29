# NEW PYTHON NEW ME

## New Person Same Old Mistakes

A Python presentation about the past, the present, and the future of
concurrency and parallellism.

**Requirements**: This is an advanced topic and assumes a general awareness of
core Python language features and a basic understanding of concurrency and
parallellism.

**Will I Be Lost?**: Not really. We can delve a bit deeper, but understand that
this is just a surface-level explanation, and we are currently focused on
specific cases, so the complete picture won't be here. Consider it a thought
exercise of what was and what's coming.

### Starting

```python

# SOMETHING TO EXPLAIN IN THE FUTURE MAYBE
# task manager that send values into a pool (could be thread or process pool)
# and returns you the future result when it exists.

class Task:
    def __init__(self, gen: Generator):
        self._gen = gen

    def step(self, value=None):
        try:
            fut = self._gen.send(value)
            fut.add_done_callback(self._wakeup)
        except StopIteration as exc:
            pass

    def _wakeup(self, fut: Future):
        result = fut.result()
        self.step(result)
```

The fundamental problem that the core Python developers are trying to address
with all of these changes regarding the GIL is concurrency and parallellism.
The GIL, or the Global Interpreter Lock, is a mechanism used by the CPython
Interpreter to ensure that only one thread at a time executes Python bytecode,
simplifying the implementation and making the object model of CPython safe
against concurrent access.

This implementation, besides simplicity, gives us two main benefits: one is it
easier to create multithreaded programs, two its single-core, single-process
performance.

After all of this, we must ask ourselves, how do threads work then? If only one
can be executed at a time, how does Python manage them, and how is their
execution?

```python

from typing import Generator, List
from concurrent.futures._base import Future
import concurrent.futures
from contextlib import contextmanager
import time


@contextmanager
def time_it(func_name: str) -> Generator[None, None, None]:
    t0 = time.monotonic()
    try:
        yield
    finally:
        print(f"{func_name} took {time.monotonic() - t0}")


def fibonacci(n: int) -> int:
    return 1 if n <= 2 else (fibonacci(n-1) + fibonacci(n-2))
```

What we are going to do is to calculate the Fibonacci number, and with the
context manager, we are just going to time its execution.

```python

def main_single_thread(fib_number: int, callers: int) -> int:
    with time_it("** main_single_thread **"):
        for _ in range(callers):
            fib = fibonacci(fib_number)
            print(f"got {fib}")
    return 0


if __name__ == "__main__":

    FIBONACCI_NUMBER = 10
    NUMBER_OF_CALLERS = 1_000
    main_single_thread(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
```

Checking the results of the code

```log
** main_single_thread ** took 0.0041588750027585775
```

Let's see what would happen if we were to send that same work into more
threads.

```python

def main_threads(fib_number: int, callers: int) -> int:
    with time_it("** main_threads **"):
        with concurrent.futures.ThreadPoolExecutor() as pool:
            futures: List[Future[int]] = [
                pool.submit(fibonacci, fib_number)
                for _ in range(callers)
            ]

            for future in concurrent.futures.as_completed(futures):
                print(f"got {future.result()}")
    return 0
```

Checking the results of the execution:

```log

** main_threads ** took 0.012557791997096501
```

We can see that not only was the time not better, but it got worse. Shouldn't
threads allow you to do several tasks at the same time?

Let's change up the function to see what is really happening under the hood.

```python

from typing import Generator, List
from concurrent.futures._base import Future
import concurrent.futures
from contextlib import contextmanager
import inspect
import threading
import time


def fibonacci(n) -> int:
    # Who is calling the function
    caller_frame = inspect.stack()[1]
    caller_name = caller_frame[3]
    print("Caller: ", caller_name)
    # In what thread am I in
    current_thread_id = threading.get_ident()
    print("Current Thread ID: ", current_thread_id)
    return 1 if n <= 2 else (fibonacci(n-1) + fibonacci(n-2))
```

This will make the function drastically slower, but it will show us the context
of execution, and we will be able to see what is going on.

```python

if __name__ == "__main__":

    main_single_thread(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
    main_threads(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
```

and seeing the results from single thread

```log
.
.
.
Caller:  fibonacci
Current Thread ID:  8128077952
Caller:  fibonacci
Current Thread ID:  8128077952
Caller:  fibonacci
Current Thread ID:  8128077952
Caller:  fibonacci
Current Thread ID:  8128077952
Caller:  fibonacci
Current Thread ID:  8128077952
Caller:  fibonacci
Current Thread ID:  8128077952
Caller:  fibonacci
Current Thread ID:  8128077952
got 55
** main_single_thread ** took 14.36734866599727
```

and from multithreads

```log
.
.
.
Caller:  fibonacci
Current Thread ID:  6185463808
Caller:  fibonacci
Current Thread ID:  6320074752
Caller:  fibonacci
Current Thread ID:  6185463808
Caller:  fibonacci
Current Thread ID:  6269595648
Caller:  fibonacci
Current Thread ID:  6219116544
Caller:  fibonacci
Current Thread ID:  6269595648
Caller:  fibonacci
Current Thread ID:  6320074752
Caller:  fibonacci
Current Thread ID:  6185463808
Caller:  fibonacci
Current Thread ID:  6219116544
Caller:  fibonacci
Current Thread ID:  6269595648
got 55
Caller:  fibonacci
Current Thread ID:  6320074752
Caller:  fibonacci
Current Thread ID:  6219116544
got 55
.
.
.

** main_threads ** took 37.5095809159975
```

What we can see is the main problem that Python has with threads. The
interpreter is constantly switching the context of the execution between the
sender of the job and the executor of the job, looking like the threads are
constantly fighting to hold the interpreter and calculate the Fibonacci number.

With the high cost of the context switching, and the blocking nature of a
single threaded process, Is there a way then to sidestep all of these problems
so that our code can run in parallel and pass the limitations of the
Interpreter that locks us into a single block execution environment?

Yes, the **multiprocessing** library.

The multiprocessing library allows us to sidestep the GIL by starting a fresh
Python interpreter process. This is done through the use of operating system
API calls.

**spawn** is the default in MacOS and Windows, where the child process just
inherits the resources necessary to run the object's run() method. Is slower
than other methods (like fork), but more consistent in execution.

**fork** is the default in all the POSIX systems except MacOS, where the child
process has all the context and resources that the parent process has. Is
faster than **spawn**, but is prone to crashes in multiprocess and
multithreaded environments.

What this allows us to do is to have a new Python interpreter for each process,
eliminating the issue of multiple thread contexts fighting.

Changing the code to use multiprocessing:

```python

def fibonacci(n: int) -> int:
    return 1 if n <= 2 else (fibonacci(n-1) + fibonacci(n-2))

def main_multiprocess(fib_number: int, callers: int) -> int:
    with time_it("** main_multiprocess **"):
        with concurrent.futures.ProcessPoolExecutor() as pool:
            futures: List[Future[int]] = [
                pool.submit(fibonacci, fib_number)
                for _ in range(callers)
            ]

            for future in concurrent.futures.as_completed(futures):
                # future.result()
                print(f"got {future.result()}")
    return 0

if __name__ == "__main__":

    main_multiprocess(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
```

Checking the results of the execution,

```log
** main_multiprocess ** took 0.1447971250017872
```

Even though we could achieve **True** parallellism, there is still the issue of
all of these contexts being created for the different processes. They take time
and memory to create, and is not until we bump up the calculations, that we can
strat to see the advantages.

```python

if __name__ == "__main__":

    FIBONACCI_NUMBER = 20
    NUMBER_OF_CALLERS = 1_000

    main_single_thread(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
    main_threads(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
    main_multiprocess(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
```

```log
** main_single_thread ** took 0.39971687500656117
** main_threads ** took 0.41029400000115857
** main_multiprocess ** took 0.21206420799717307
```

```python

if __name__ == "__main__":

    FIBONACCI_NUMBER = 25
    NUMBER_OF_CALLERS = 1_000

    main_single_thread(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
    main_threads(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
    main_multiprocess(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
```

```log
** main_single_thread ** took 4.478854541986948
** main_threads ** took 4.450871249995544
** main_multiprocess ** took 0.9804444589972263
```

Because we could achieve **True** parallellism, the time was actually cut in
the proportion that your computer has cores if we don't take into account the
time takes to create the different context for the interpreters, and we must
not forget the extra memory spended, that could cause unexpected loads that can
be problematic.

But after all of this, what is the usefullness of threads if they cannot run on
parallel and if you have several of them, they cannot stop fighting each other?

let's try chaning the ammount of work that each thread has to do with the
fibonacci calculations, and the ammount of callers that are calling the
function.

```python

if __name__ == "__main__":

    FIBONACCI_NUMBER = 0
    NUMBER_OF_CALLERS = 10_000

    main_single_thread(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
    main_threads(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
    main_multiprocess(fib_number=FIBONACCI_NUMBER, callers=NUMBER_OF_CALLERS)
```

```log
** main_single_thread ** took 0.0027001670096069574
** main_threads ** took 0.05031700000108685
** main_multiprocess ** took 0.7957916659943294
```

Even tho the single thread execution is still faster for light work, the
threads allows to have concurrent work. Which means threads allows us to deal
with a lot of stuff at once, even tho they don't allow us to do a lot of things
at once, making threads are way to execute code that needs to just waiting
around asyncronous responses.

In the context of servers, the speed of a single process is completely negated
by the fact that only one client can be served a quick request at a time,
making the non blocking nature and the speed of creation of threads a better
alternative **(DO NOT SPEAK TO ME ABOUT ASYNCIO, YET)**.

### WHY ALL OF THIS

The idea was to show how Python dealt with concurrency and parallellism and how
it is trying to change that approach into the future.

With Python@3.12 there is a new change within the C_API, where a new isolated
interpreter can be easily created with its own GIL, and threads can run in it,
but still to achieve **True** parallellism, each thread has to have its own
isolated interpreter with its own GIL.

It's not until Python@3.13 that the Python API to create threads with their own
interpreter will be out. The idea for the moment (still in debate and can
change the implementation in the future) is to add a new object, the
`Interpreter` object.

With that, we will create a new `Interpreter` object and then create threads
inside it.

As an example (This code is just an interpretation of what it may look like to
run a thread inside a new interpreter):

```python

from typing import Generator
from contextlib import contextmanager
import interpreters
import threading


@contextmanager
def new_interpreter(thread: threading.Thread) -> Generator[None, None, None]:
    try:
        interp = interpreter.create()
        yield from interp.run(thread(func, args))
    finally:
        interp.close()
```

What the implementation could be, is to create an interpreter, run a thread
inside it and yield the result, then close the interpreter as the result from
the thread is collected.

At the end of the day the aim is to create a more complete language, asyncio
is a more efficient alternative to threads (not really, because you have to go
all the way in into corutines and have all of your code change to fit it, but
you can't go around and create 20 thousand threads for 20 thousand processes)
and to make threads a more efficient alternative to multiprocessing, while the
core devs move forward with the deletion of the GIL.
