import json
import requests

from typing import List, Tuple, Union
from canoser import RustEnum, RustOptional
from json_rpc.views import AccountView, StateProofView, TransactionView, EventView, \
    BlockMetadataView, AccountStateWithProofView
from move_core_types.account_address import AccountAddress as Address
from lbrtypes.rustlib import ensure
from lbrtypes.transaction import SignedTransaction

class JsonRpcBatch():
    def __init__(self, requests: List[Tuple[str, List]]):
        self.requests = requests

    @classmethod
    def new(cls):
        object = cls.__new__(cls)
        object.requests = list()
        return object


    def json_request(self):
        request = list()
        for index, r in enumerate(self.requests):
            value = {
                "jsonrpc": "2.0",
                "method": r[0],
                "params": r[1],
                "id": index
            }
            request.append(value)
        return request

    def add_request(self, method_name: str, parameters: List):
        self.requests.append((method_name, parameters))


    def add_submit_request(self, transaction: SignedTransaction):
        tx = transaction.serialize()
        self.add_request("submit", [tx.hex()])

    def add_get_account_state_request(self, address: Union[str, bytes]):
        self.add_request("get_account_state", [Address.normalize_to_bytes(address).hex()])

    def add_get_metadata_request(self):
        self.add_request("get_metadata", [None])

    def add_get_transactions_request(self, start_version: int, limit: int, include_events: bool):
        self.add_request("get_transactions", [start_version, limit, include_events])

    def add_get_account_transaction_request(self, acccount: Union[str, bytes], sequence_number: int, include_events: bool):
        self.add_request("get_account_transaction", [Address.normalize_to_bytes(acccount).hex(), sequence_number, include_events])

    def add_get_events_request(self, event_key: str, start: int, limit: int):
        self.add_request("get_events", [event_key, start, limit])

    def add_get_state_proof_request(self, known_version: int):
        self.add_request("get_state_proof", [known_version])

    def add_get_account_state_with_proof_request(self, account: Union[str, bytes], version: int=None, ledger_version: int=None):
        self.add_request("get_account_state_with_proof", [Address.normalize_to_bytes(account).hex(), version, ledger_version])

class JsonRpcAsyncClient():
    def __init__(self, address: str):
        self.address = address

    @classmethod
    def new(cls, host: str, port: int):
        address = f"http://{host}:{port}"
        return cls(address)

    def get_accounts_state(self, accounts: List[Union[str, bytes]]):
        batch = JsonRpcBatch.new()
        for account in accounts:
            batch.add_get_account_state_request(account)
        exec_results = self.execute(batch)
        results = list()
        for exec_result in exec_results:
            ensure(exec_result.name == "AccountResponse", f"Unexpected response for get_accounts_state {exec_result}")
            results.append(exec_result.value)
        ensure(len(results) == len(accounts), f"Received unexpected number of JSON RPC responses ({len(results)}) for {len(accounts)} requests")
        return results

    def submit_transaction(self, txn: SignedTransaction):
        batch = JsonRpcBatch.new()
        batch.add_submit_request(txn)
        exec_result = self.execute(batch)
        assert len(exec_result) == 1

    def execute(self, batch: JsonRpcBatch):
        #TODO: async
        payload = batch.json_request()
        headers = {'content-type': 'application/json'}
        resp = requests.post(self.address, data=json.dumps(payload),headers=headers)
        ensure(resp.status_code == 200, f"Http error code {resp.status_code}")
        responses = resp.json()
        return process_batch_response(responses)

class OptionalAccountView(RustOptional):
    _type = AccountView

class OptionalTransactionView(RustOptional):
    _type = TransactionView

class JsonRpcResponse(RustEnum):
    _enums = [
        ("SubmissionResponse", None),
        ("AccountResponse", OptionalAccountView),
        ("StateProofResponse", StateProofView),
        ("AccountTransactionResponse", OptionalTransactionView),
        ("TransactionsResponse", [TransactionView]),
        ("EventsResponse", [EventView]),
        #TODO BlockMetadataResponse
        ("BlockMetadataResponse", BlockMetadataView),
        ("AccountStateWithProofResponse", AccountStateWithProofView),
        ("UnknownResponse", {})
    ]

    @classmethod
    def try_from(cls, method: str, value):
        if method == "submit":
            ensure(value == None, f"received unexpected payload for submit: {value}")
            return JsonRpcResponse("SubmissionResponse")
        if method == "get_account_state":
            if value is None:
                account_view = None
            else:
                account_view = AccountView.from_value(value)
            return JsonRpcResponse("AccountResponse",OptionalAccountView(account_view))
        if method == "get_events":
            events = [EventView.from_value(v) for v in value]
            return JsonRpcResponse("EventsResponse", events)
        if method == "get_metadata":
            metadata = BlockMetadataView.from_value(value)
            return JsonRpcResponse("BlockMetadataResponse", metadata)
        if method == "get_account_state_with_proof":
            account_with_proof = AccountStateWithProofView.from_value(value)
            return JsonRpcResponse("AccountStateWithProofResponse", account_with_proof)
        if method == "get_state_proof":
            state_proof = StateProofView.from_value(value)
            return JsonRpcResponse("StateProofResponse", state_proof)
        if method == "get_account_transaction":
            if value is None:
                txn = None
            else:
                txn = TransactionView.from_value(value)
            return JsonRpcResponse("AccountTransactionResponse", OptionalTransactionView(txn))

        if method == "get_transactions":
            txns = [TransactionView.from_value(v) for v in value]
            return JsonRpcResponse("TransactionsResponse", txns)

        return JsonRpcResponse("UnknownResponse", value)


def process_batch_response(batch: JsonRpcBatch, responses: List):
    result = batch.requests
    seen_ids = set()
    for response in responses:
        json_rpc_protocol = response.get("jsonrpc")
        ensure(json_rpc_protocol == "2.0", f"JSON RPC response with incorrect protocol: {json_rpc_protocol}")
        req_id = fetch_id(response)
        ensure(req_id not in seen_ids, "received JSON RPC response with duplicate response ID")
        seen_ids.add(req_id)
        if req_id < len(result):
            err_data = response.get("error")
            if err_data:
                #TODO: return
                result[req_id] = err_data
            else:
                data = response.get("result")
                method = batch.requests[req_id][0]
                result[req_id] = JsonRpcResponse.try_from(method, data)
    return result

def get_response_from_batch(index: int, batch: List[Union[JsonRpcResponse, str]]) -> Union[JsonRpcResponse, str]:
    ensure(index < len(batch), f"[JSON RPC client] response missing in batch at index {index}")
    return batch[index]

def fetch_id(response):
    ensure("id" in response, "request id is missing")
    return response["id"]
