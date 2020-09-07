import copy
from typing import Optional
from lbrtypes.account_state import AccountState as LibraAccountState
from extypes.exchange_resource import ReservesResource, RegisteredCurrenciesResource, TokensResource
from extypes.exdep_resource import BalanceResource
from move_core_types.language_storage import StructTag, TypeTag
from error import get_exception

class AccountState(LibraAccountState):
    @classmethod
    def new(cls, account_state: LibraAccountState):
        ret = copy.deepcopy(account_state)
        ret.__class__ = cls
        return ret

    @get_exception
    def swap_get_balance(self, currency_code, exchange_module_address=None) -> Optional[BalanceResource]:
        type_tag = TypeTag("Struct", StructTag.new(currency_code))
        resource = self.get(BalanceResource.resource_path_for(type_tag, module_address=self.get_exchange_module_address(exchange_module_address)))
        return BalanceResource.deserialize(resource).value

    @get_exception
    def swap_get_reserves_resource(self, exchange_module_address=None) -> Optional[ReservesResource]:
        resource = self.get(ReservesResource.resource_path(module_address=self.get_exchange_module_address(exchange_module_address)))
        return ReservesResource.deserialize(resource).reserves

    @get_exception
    def swap_get_tokens_resource(self, exchange_module_address=None) -> Optional[TokensResource]:
        resource = self.get(TokensResource.resource_path(module_address=self.get_exchange_module_address(exchange_module_address)))
        return TokensResource.deserialize(resource)

    @get_exception
    def swap_get_registered_currencies(self, exchange_module_address=None) -> Optional[RegisteredCurrenciesResource]:
        resource = self.get(RegisteredCurrenciesResource.resource_path(module_address=self.get_exchange_module_address(exchange_module_address)))
        return RegisteredCurrenciesResource.deserialize(resource)

    def set_exchange_module_address(self, address):
        if address:
            self.exchange_module_address = address

    def get_exchange_module_address(self, address=None):
        if address:
            return address
        if hasattr(self, "exchange_module_address"):
            return self.exchange_module_address




