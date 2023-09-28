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

What we are going to do, is to calculate the Fibonacci number and with the
context manager, we are just going to time its execution, and we are going to
create a function that even tho will use two threads, the main execution thread
and the concurrent.futures thread, is going to be called single threaded,
because for all intents and purposes we are just going to generate one worker
that will do all the calculations and the main thread will just send the jobs.

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

Lets see what would happen if we were to send that same work, but into more
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

Checking the results of the execution

```log
** main_threads ** took 0.012557791997096501
```

We can see that not only, the time wasn't better, but it got worse. Shouldn't
threads allow you to do several tasks at the same time?

Let's change up the function to see what is really happenning under the hood.

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

This will make the function drasticly slower, but it will show us the context
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
interpreter is constantly switching the context of the execution, between the
sender of the job and the executor of the job, looking like the threads are
constantly fighing for the interpreter to calculate the fibonacci number and
that context switching has a high cost.

Is there a way then, to side step all of this problems, so that our code can
run in parallel and pass the limitations of the Interpreter that locks us into
a single core execution?

Yes, the multiprocessing library.

The multiprocessing library allows us to side step the GIL by starting a fresh
Python interpreter process. This is done throught the use of the operatin
system api calls,

**spawn**, default in MacOs and Windows, where the child process just inherits
the resources necesary to run the object's `run()` method.

**fork**, default in all the POSIX systems except MacOs, where the child
process has all the context and resources than the parent process has.

What this allows us is to have a new Python interpreter for each process,
erasing the issue of the multiple thread context fighting.

changing the code to use multiprocessing,

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

Even tho we could achieve **True** parallellism, there is still the issue of
all of this context created for the different processes, because it takes time
to create. But if we bump up the calculations, we can strat to see the
advantages.

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
time takes to create the different context for the interpreters. The downsides
of doing this is that we create a big memory overhead, because of the
interpreter and the context of the function has to be copied several times for
each of the processes which may cause some problems.

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
at once. Meaning that the threads are great for just waiting around asyncronous
responses.

### WHY ALL OF THIS

The idea was to show how Python dealt with concurrency and parallellism and how
it is trying to change that approach into the future.

With Python@3.12 there is a new change in the C_API for the threading module,
where a new field can be added, that field is the per thread interpreter. This
will allow each thread to have it's own GIL and its own interpreter, making it
possible to use them for parallel work, not only concurrent.

This means, that even tho there will be still a high memory cost to run things
in parallel, the memory requirement is lower because a new process is more
expensive, the complexity is suddently lower, because we don't have to spawn
a new process and the speed of spawning them compared to the processes will be
faster.

What is aimed into the future, is the deprecation of the multiprocessing
module, create bettter threads and move a step forward into removing the GIL.
