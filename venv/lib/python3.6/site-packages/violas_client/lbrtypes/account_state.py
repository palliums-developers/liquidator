from typing import Optional
from lbrtypes.account_config import *
from lbrtypes.on_chain_config import ConfigurationResource
from lbrtypes.validator_config import ValidatorConfigResource
from lbrtypes.libra_timestamp import LibraTimestampResource
from lbrtypes.on_chain_config.validator_set import ValidatorSet
from lbrtypes.block_metadata import LibraBlockResource
from lbrtypes.access_path import AccessPath


class AccountState(Struct):
    _fields = [
        ("ordered_map", {bytes: bytes})
    ]

    def exists(self):
        if isinstance(self.ordered_map, dict):
            return True
        return False

    def get_sequence_number(self):
        resource = self.get_account_resource()
        if resource:
            return resource.get_sequence_number()
        return 0

    def get_balance(self, currency_code=None, currency_module_address=None):
        balance_resource = self.get_balance_resource(currency_code, currency_module_address)
        if balance_resource:
            return balance_resource.get_coin()

    def get_account_address(self):
        account_resource = self.get_account_resource()
        if account_resource:
            return account_resource.sent_events.get_creator_address()

    def is_published(self, currency_code=None, currency_module_address=None):
        return self.get_balance_resource(currency_code, currency_module_address) is not None

    def get_code(self, currency_code):
        currency_module_address = self.get_account_address()
        if currency_module_address is None:
            currency_module_address = CORE_CODE_ADDRESS
        key = ModuleId(currency_module_address, currency_code)
        path = AccessPath.code_access_path_vec(key)
        return self.ordered_map.get(path)

    def get_registered_currencies(self):
        from lbrtypes.on_chain_config.registered_currencies import RegisteredCurrencies
        registered_currencies_resource = self.get(RegisteredCurrencies.resource_path().path)
        if registered_currencies_resource:
            return RegisteredCurrencies.deserialize(registered_currencies_resource).currency_codes

    def get_account_resource(self) -> Optional[AccountResource]:
        if self.exists():
            resource = self.get(AccountResource.resource_path())
            if resource:
                return AccountResource.deserialize(resource)

    def get_balance_resource(self, currency_code=None, currency_module_address=None) -> Optional[BalanceResource]:
        account_resource = self.get_account_resource()
        if account_resource:
            if currency_code is None:
                currency_code = LBR_NAME
            currency_type_tag = type_tag_for_currency_code(currency_code, currency_module_address)
            resource = self.get(BalanceResource.access_path_for(currency_type_tag))
            if resource:
                return BalanceResource.deserialize(resource)

    def get_configuration_resource(self) -> Optional[ConfigurationResource]:
        configuration_resource = self.get(ConfigurationResource.resource_path())
        if configuration_resource:
            return ConfigurationResource.deserialize(configuration_resource)

    def get_libra_timestamp_resource(self) -> Optional[LibraTimestampResource]:
        libra_timestamp_resource = self.get(LibraTimestampResource.resource_path())
        if libra_timestamp_resource:
            return LibraTimestampResource.deserialize(libra_timestamp_resource)

    def get_validator_config_resource(self) -> Optional[ValidatorConfigResource]:
        validator_config_resource = self.get(ValidatorConfigResource.resource_path())
        if validator_config_resource:
            return ValidatorConfigResource.deserialize(validator_config_resource)

    def get_currency_info_resource(self, currency_code) -> Optional[CurrencyInfoResource]:
        resource = self.get(CurrencyInfoResource.access_path_for(currency_code))
        if resource:
            return CurrencyInfoResource.deserialize(resource)

    def get_validator_set(self) -> Optional[ValidatorSet]:
        resource = self.get(ValidatorSet.CONFIG_ID.access_path().path)
        if resource:
            return ValidatorSet.deserialize(resource)

    def get_libra_block_resource(self) -> Optional[LibraBlockResource]:
        resource = self.get(LibraBlockResource.resource_path())
        if resource:
            return LibraBlockResource.deserialize(resource)

    def get_event_handle_by_query_path(self, query_path):
        from lbrtypes.block_metadata import NEW_BLOCK_EVENT_PATH
        if self.exists():
            if ACCOUNT_RECEIVED_EVENT_PATH == query_path:
               return  self.get_account_resource().get_received_events()
            elif ACCOUNT_SENT_EVENT_PATH == query_path:
                return self.get_account_resource().get_sent_events()
            elif NEW_BLOCK_EVENT_PATH == query_path:
                return self.get_libra_block_resource()

    def get(self, key):
        if self.exists():
            return self.ordered_map.get(key)

    def is_empty(self):
        return not self.exists()

    def __str__(self):
        import json
        amap = self.to_json_serializable()
        account_resource = self.get_account_resource()
        libra_timestamp = self.get_libra_timestamp_resource()
        validator_config = self.get_validator_config_resource()
        validator_set = self.get_validator_set()
        configuration = self.get_configuration_resource()
        libra_block = self.get_libra_block_resource()
        if account_resource:
            amap["AccountResource"] = account_resource.to_json_serializable()
        if libra_timestamp:
            amap["LibraTimestamp"] = libra_timestamp.to_json_serializable()
        if validator_config:
            amap["ValidatorConfig"] = validator_config.to_json_serializable()
        if validator_set:
            amap["ValidatorSet"] = validator_set.to_json_serializable()
        if configuration:
            amap["Configuration"] = configuration.to_json_serializable()
        if libra_block:
            amap["LibraBlock"] = libra_block.to_json_serializable()
        return json.dumps(amap, sort_keys=False, indent=2)

    def get_resource(self, tag, accesses=[]):
        path = AccessPath.resource_access_vec(tag, accesses)
        return self.get(path)


    def get_item_counts(self):
        if self.exists():
            return len(self.ordered_map)