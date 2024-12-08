from ratelimit import limits, sleep_and_retry
import time


class APIRateLimiter:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries

    def call_api(self, api_call_lambda):
        """
        Calls an API using a lambda function. Retries based on headers if throttled.

        :param api_call_lambda: A lambda function that performs an API call and returns a response object.
        :return: The response object if successful.
        :raises Exception: If the API call fails after maximum retries.
        """
        retries = 0

        while retries < self.max_retries:
            print(f"[APIRateLimiter] attempt {retries+1}/{self.max_retries}")
            response = api_call_lambda()

            # Check if the call was successful
            if response.status_code == 200:

                return response

            # Check for throttling
            if response.status_code == 429:  # Too Many Requests
                retry_after = int(response.headers.get("Retry-After", 1))  # Default to 1 second if header missing
                print(f"[APIRateLimiter] Throttled. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                retries += 1
            else:
                # If not a throttling error, break and raise
                raise Exception(f"API call failed with status code {response.status_code}: {response.text}")

        # Raise an exception if max retries are reached
        raise Exception("Maximum retries reached. Could not fetch data.")