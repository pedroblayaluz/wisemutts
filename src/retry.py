"""Retry logic with exponential backoff for resilient API calls."""

import asyncio
import time
from typing import TypeVar, Callable, Any
from functools import wraps

T = TypeVar('T')

MAX_RETRIES = 10  # Maximum 10 attempts
BASE_DELAY = 1  # Start with 1 second
MAX_DELAY = 60  # Cap delay at 60 seconds per attempt
TOTAL_TIMEOUT = 600  # 10 minutes total timeout


class RetryExhaustedError(Exception):
    """Raised when retry attempts are exhausted."""

    pass


def retry_with_backoff(
    max_retries: int = MAX_RETRIES,
    base_delay: float = BASE_DELAY,
    max_delay: float = MAX_DELAY,
    total_timeout: float = TOTAL_TIMEOUT,
    backoff_multiplier: float = 2.0
):
    """
    Decorator for retrying a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        total_timeout: Total timeout for all retries in seconds
        backoff_multiplier: Multiplier for exponential backoff

    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            last_exception = None
            delay = base_delay

            for attempt in range(1, max_retries + 1):
                try:
                    elapsed = time.time() - start_time
                    if elapsed >= total_timeout:
                        raise RetryExhaustedError(
                            f"Total timeout ({total_timeout}s) exceeded after {attempt - 1} attempts"
                        )

                    result = await func(*args, **kwargs)

                    if attempt > 1:
                        print(f"✅ Succeeded on attempt {attempt}")

                    return result

                except Exception as e:
                    last_exception = e
                    elapsed = time.time() - start_time
                    remaining = total_timeout - elapsed

                    if attempt >= max_retries:
                        raise RetryExhaustedError(
                            f"Max retries ({max_retries}) exhausted. Last error: {str(e)}"
                        ) from e

                    if remaining <= 0:
                        raise RetryExhaustedError(
                            f"Total timeout ({total_timeout}s) exceeded. Last error: {str(e)}"
                        ) from e

                    # Calculate next delay with exponential backoff
                    next_delay = min(delay * backoff_multiplier, max_delay)
                    wait_time = min(next_delay, remaining)

                    print(f"⚠️  Attempt {attempt}/{max_retries} failed: {str(e)}")
                    print(f"⏳ Retrying in {wait_time:.1f}s... (elapsed: {elapsed:.1f}s/{total_timeout}s)")

                    await asyncio.sleep(wait_time)
                    delay = next_delay

            # Should not reach here, but just in case
            raise RetryExhaustedError(
                f"Unexpected: All retries exhausted. Last error: {str(last_exception)}"
            ) from last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            last_exception = None
            delay = base_delay

            for attempt in range(1, max_retries + 1):
                try:
                    elapsed = time.time() - start_time
                    if elapsed >= total_timeout:
                        raise RetryExhaustedError(
                            f"Total timeout ({total_timeout}s) exceeded after {attempt - 1} attempts"
                        )

                    result = func(*args, **kwargs)

                    if attempt > 1:
                        print(f"✅ Succeeded on attempt {attempt}")

                    return result

                except Exception as e:
                    last_exception = e
                    elapsed = time.time() - start_time
                    remaining = total_timeout - elapsed

                    if attempt >= max_retries:
                        raise RetryExhaustedError(
                            f"Max retries ({max_retries}) exhausted. Last error: {str(e)}"
                        ) from e

                    if remaining <= 0:
                        raise RetryExhaustedError(
                            f"Total timeout ({total_timeout}s) exceeded. Last error: {str(e)}"
                        ) from e

                    # Calculate next delay with exponential backoff
                    next_delay = min(delay * backoff_multiplier, max_delay)
                    wait_time = min(next_delay, remaining)

                    print(f"⚠️  Attempt {attempt}/{max_retries} failed: {str(e)}")
                    print(f"⏳ Retrying in {wait_time:.1f}s... (elapsed: {elapsed:.1f}s/{total_timeout}s)")

                    time.sleep(wait_time)
                    delay = next_delay

            # Should not reach here, but just in case
            raise RetryExhaustedError(
                f"Unexpected: All retries exhausted. Last error: {str(last_exception)}"
            ) from last_exception

        # Return the appropriate wrapper based on whether func is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
