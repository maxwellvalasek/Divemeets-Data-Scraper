import time
from functools import wraps
import atexit

class ExecutionInfo:
    def __init__(self, func):
        wraps(func)(self)
        self.num_calls = 0
        self.total_time = 0

    def __call__(self, *args, **kwargs):
        start_time = time.time()
        result = self.__wrapped__(*args, **kwargs)
        end_time = time.time()
        self.num_calls += 1
        self.total_time += end_time - start_time
        return result

    def print_info(self):
        print(f"Function {self.__name__} took {self.total_time:.5f} seconds in total to execute.")
        print(f"Function {self.__name__} was called {self.num_calls} times in total.")

def execution_info(func):
    info = ExecutionInfo(func)
    atexit.register(info.print_info)
    return info