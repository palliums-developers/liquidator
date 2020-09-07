from typing import Optional, Union
from exchange_client import Client as ExchangeClient
from bank_client import Client as BankClient
from libra_client import Client as LibraClient
from vlstypes.account_state import AccountState
from vlstypes.view import TransactionView

class Client(ExchangeClient, BankClient, LibraClient):
    def get_account_state(self, account_address) -> Optional[AccountState]:
        state = LibraClient.get_account_state(self, account_address)
        if state is not None:
            return AccountState.new(state)

    def get_transaction(self, version, fetch_events:bool=True) -> Optional[TransactionView]:
        txs = self.get_transactions(version, 1, fetch_events)
        if len(txs):
            return txs[0]

    def get_transactions(self, start_version: int, limit: int, fetch_events: bool=True) -> [TransactionView]:
        txs = LibraClient.get_transactions(self, start_version, limit, fetch_events)
        return [TransactionView.new(tx) for tx in txs]

    def get_account_transaction(self, account_address: Union[bytes, str], sequence_number: int, fetch_events: bool=True) -> TransactionView:
        tx = LibraClient.get_account_transaction(self, account_address, sequence_number, fetch_events)
        if tx:
            return TransactionView.new(tx)