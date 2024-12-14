from ratelimit import limits, sleep_and_retry
from src.constants.constants import RATE_LIMITER_DEFAULT_WAIT_TIME_SECONDS
import time
import logging

class HTTPRateLimiter:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.logger = logging.getLogger(self.__class__.__name__)


    def call_api(self, api_call_lambda):
        """
        Calls an API using a lambda function. Retries based on headers if throttled.

        :param api_call_lambda: A lambda function that performs an API call and returns a response object.
        :return: The response object if successful.
        :raises Exception: If the API call fails after maximum retries.
        """
        retries = 0

        while retries < self.max_retries:
            self.logger.info(f"[APIRateLimiter] attempt {retries+1}/{self.max_retries}")
            response = api_call_lambda()

            # Check if the call was successful
            if response.status_code == 200:

                return response

            # Check for throttling
            if response.status_code == 429:  # Too Many Requests
                retry_after = int(response.headers.get("Retry-After", RATE_LIMITER_DEFAULT_WAIT_TIME_SECONDS))  # Default to 1 second if header missing
                self.logger.info(f"[APIRateLimiter] Throttled. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                retries += 1
            else:
                # If not a throttling error, break and raise
                api_failure_error_message = f"API call failed with status code {response.status_code}: {response.text}"
                self.logger.error(api_failure_error_message)
                raise Exception(api_failure_error_message)


        # Raise an exception if max retries are reached
        self.logger.error("Maximum retries reached - raising exception (Could not fetch data)")
        raise Exception("Maximum retries reached. Could not fetch data.")