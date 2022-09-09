from functools import wraps
from time import sleep


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10, logger=None):
    """
    A function to re-execute the function after some time if an error occurs.
    Uses exponential growth of the repeat time up to the boundary sleep time

    Formula:
    t = start_sleep_time * 2^(n) if t < border_sleep_time else border_sleep_time

    :param logger: logger
    :param start_sleep_time: start repeat time
    :param factor: the exponent
    :param border_sleep_time: limit waiting time
    :return: function execution result
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time, n = start_sleep_time, 1
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if logger:
                        logger.info(f'During execution of '
                                    f'{func.__qualname__} function '
                                    f'the error occurred: \n {e}')
                    sleep(sleep_time)
                    sleep_time = (sleep_time * factor) \
                        if (sleep_time * factor) < border_sleep_time \
                        else border_sleep_time
        return inner

    return func_wrapper
