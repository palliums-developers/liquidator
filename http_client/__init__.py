import typing
import time
import requests

from dataclasses import dataclass


DEFAULT_CONNECT_TIMEOUT_SECS: float = 5.0
DEFAULT_TIMEOUT_SECS: float = 30.0

class StaleResponseError(Exception):
    pass

class InvalidServerResponse(Exception):
    pass


@dataclass
class Retry:
    max_retries: int
    delay_secs: float
    exception: typing.Type[Exception]

    def execute(self, fn: typing.Callable):  # pyre-ignore
        tries = 0
        while tries < self.max_retries:
            tries += 1
            try:
                return fn()
            except self.exception as e:
                if tries < self.max_retries:
                    # simplest backoff strategy: tries * delay
                    time.sleep(self.delay_secs * tries)
                else:
                    raise e

class Client:
    def __init__(
        self,
        server_url: str,
        session: typing.Optional[requests.Session] = None,
        timeout: typing.Optional[typing.Tuple[float, float]] = None,
        retry: typing.Optional[Retry] = None,
    ) -> None:
        self._url: str = server_url
        self._session: requests.Session = session or requests.Session()
        self._timeout: typing.Tuple[float, float] = timeout or (DEFAULT_CONNECT_TIMEOUT_SECS, DEFAULT_TIMEOUT_SECS)
        self._retry: Retry = retry or Retry(5, 0.2, StaleResponseError)

    def send_request(
        self,
        request: typing.Dict[str, typing.Any]
    ) -> typing.Dict[str, typing.Any]:
        response = self._session.get(url=self._url, params=request, timeout=self._timeout)
        response.raise_for_status()
        try:
            json = response.json()
        except ValueError as e:
            raise InvalidServerResponse(f"Parse response as json failed: {e}, response: {response.text}")
        return json

    def try_create_child_vasp_account(self, account):
        request = {
            "address": account.address_hex,
            "auth_key_perfix": account.auth_key_prefix.hex(),
        }
        result = self.send_request(request)
        if result.get("code") != 2000:
            raise InvalidServerResponse(f"error message: f{result.get('message')}")

if __name__ == "__main__":
    from violas_client import Wallet

    wallet = Wallet.new()
    a1 = wallet.new_account()

    client = Client()
    request = {
        "address": a1.address_hex,
        "auth_key_perfix": a1.auth_key_prefix.hex(),
    }
    result = client.send_request(request)
