from ratelimit import limits, sleep_and_retry
from src.constants.constants import RATE_LIMITER_DEFAULT_WAIT_TIME_SECONDS
import time
import logging

class HTTPCallRetrier:
    '''
        Retries HTTP Calls against errors and throttling
    '''
    def __init__(self, max_retries=3, exponential_backoff_rate = 2, initial_wait_time_seconds = 1):
        self.max_retries = max_retries
        self.initial_wait_time_seconds = initial_wait_time_seconds
        self.exponential_backoff_rate = exponential_backoff_rate
        self.logger = logging.getLogger(self.__class__.__name__)

    def call_api(self, api_call_lambda, namespace):
        """
        Calls an API using a lambda function. Retries based on headers if throttled.

        :param api_call_lambda: A lambda function that performs an API call and returns a response object.
        :return: The response object if successful.
        :raises Exception: If the API call fails after maximum retries.
        """
        retries = 0
        self.logger.info(f"[{namespace}] Calling HTTP API with up to {self.max_retries} retries")
        last_response_text = ""
        wait_time = self.initial_wait_time_seconds
        while retries < self.max_retries:
            self.logger.info(f"[{namespace}] Attempt : {retries+1}/{self.max_retries}")
            response = api_call_lambda()

            # Check if the call was successful
            if response.status_code == 200:
                self.logger.info(f"[{namespace}] Http call completed - returning response")
                return response

            # Check for throttling
            if response.status_code == 429:  # Too Many Requests
                retry_after = int(response.headers.get("Retry-After", RATE_LIMITER_DEFAULT_WAIT_TIME_SECONDS))  # Default to 1 second if header missing                
                self.logger.info(f"[{namespace}] Throttled. Retrying after header: {retry_after} seconds...")
                wait_time = retry_after
            else:
                # If not a throttling error, break and raise
                last_response_text = f"StatusCode={response.status_code}, Response={response.text}]"
                api_failure_error_message = f"[{namespace}]API call failed: {last_response_text}"
                self.logger.error(api_failure_error_message)

            retries += 1

            if retries < self.max_retries:
                self.logger.info(f"Waiting {wait_time} seconds until another attempt")
                time.sleep(wait_time)
                wait_time *= self.exponential_backoff_rate

        # Raise an exception if max retries are reached
        error_message = f"[{namespace}] Maximum retries reached - raising exception (Could not fetch data) - last response: {last_response_text}"
        self.logger.error(error_message)
        raise Exception(error_message)