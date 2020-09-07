from typing import Optional, Union
from libra_client import Client as LibraClient
from extypes.transaction.module import Module
from extypes.transaction.script import Script
from lbrtypes.transaction.transaction_argument import TransactionArgument
from extypes.bytecode import CodeType
from extypes.account_state import AccountState
from extypes.view import TransactionView
from extypes.bytecode import update_hash_to_type_map
from lbrtypes.rustlib import ensure
from extypes.exchange_resource import ReservesResource
from extypes.exchange_error import ExchangeError
from error import LibraError
from extypes.base import Base

class Client(LibraClient, Base):

    DEAD_LINE = 7258089600

    def swap_publish_contract(self, sender_account, is_blocking=True, **kwargs):
        module = Module.gen_module(CodeType.EXDEP,sender_account.address)
        self.submit_module(sender_account, module, is_blocking, **kwargs)
        module = Module.gen_module(CodeType.EXCHANGE,sender_account.address)
        return self.submit_module(sender_account, module, is_blocking, **kwargs)

    def swap_add_currency(self, exchange_account, currency_code, is_blocking=True, **kwargs):
        exchange_module_address = self.get_exchange_module_address()
        args = []
        ty_args = self.get_type_args(currency_code)
        script = Script.gen_script(CodeType.ADD_CURRENCY, *args, ty_args=ty_args, module_address=exchange_module_address)
        seq = self.submit_script(exchange_account, script, is_blocking, **kwargs)
        self.swap_update_registered_currencies()
        return seq

    def swap_add_liquidity(self, sender_account, currencyA, currencyB, amounta_desired, amountb_desired, amounta_min=None, amountb_min=None, is_blocking=True, **kwargs):
        exchange_module_address = self.get_exchange_module_address()
        if amounta_min is None:
            amounta_min = 0
        if amountb_min is None:
            amountb_min = 0
        indexA = self.swap_get_currency_index(currencyA)
        indexB = self.swap_get_currency_index(currencyB)
        if indexA > indexB:
            currencyA, currencyB = currencyB, currencyA
            amounta_desired, amountb_desired = amountb_desired, amounta_desired
            amounta_min, amountb_min = amountb_min, amounta_min

        ty_args = self.get_type_args(currencyA)
        ty_args.extend(self.get_type_args(currencyB))

        args = []
        args.append(TransactionArgument.to_U64(amounta_desired))
        args.append(TransactionArgument.to_U64(amountb_desired))
        args.append(TransactionArgument.to_U64(amounta_min))
        args.append(TransactionArgument.to_U64(amountb_min))

        script = Script.gen_script(CodeType.ADD_LIQUIDITY, *args, ty_args=ty_args, module_address=exchange_module_address)
        return self.submit_script(sender_account, script, is_blocking, **kwargs)

    def swap_initialize(self, module_account, is_blocking=True, **kwargs):
        exchange_module_address = module_account.address
        args = []
        ty_args = []

        script = Script.gen_script(CodeType.INITIALIZE, *args, ty_args=ty_args, module_address=exchange_module_address)
        return self.submit_script(module_account, script, is_blocking, **kwargs)

    def swap_remove_liquidity(self, sender_account, currencyA, currencyB, liquidity, amounta_min=0, amountb_min=0, is_blocking=True, **kwargs):
        exchange_module_address = self.get_exchange_module_address()
        indexA = self.swap_get_currency_index(currencyA)
        indexB = self.swap_get_currency_index(currencyB)
        if indexA > indexB:
            currencyA, currencyB = currencyB, currencyA
            amounta_min, amountb_min = amountb_min, amounta_min
        args = []
        args.append(TransactionArgument.to_U64(liquidity))
        args.append(TransactionArgument.to_U64(amounta_min))
        args.append(TransactionArgument.to_U64(amountb_min))

        ty_args = self.get_type_args(currencyA)
        ty_args.extend(self.get_type_args(currencyB))

        script = Script.gen_script(CodeType.REMOVE_LIQUIDITY, *args, ty_args=ty_args, module_address=exchange_module_address)
        return self.submit_script(sender_account, script, is_blocking, **kwargs)

    def swap(self, sender_account, currency_in, currency_out, amount_in, amount_out_min=0, receiver_address=None, is_blocking=True, data=None, **kwargs):
        exchange_module_address = self.get_exchange_module_address()
        indexA = self.swap_get_currency_index(currency_in)
        indexB = self.swap_get_currency_index(currency_out)
        if indexA > indexB:
            currency_in, currency_out = currency_out, currency_in
        path = self.get_index_max_output_path(indexA, indexB, amount_in)
        if receiver_address is None:
            receiver_address = sender_account.address
        args = []
        args.append(TransactionArgument.to_address(receiver_address))
        args.append(TransactionArgument.to_U64(amount_in))
        args.append(TransactionArgument.to_U64(amount_out_min))
        args.append(TransactionArgument.to_U8Vector(bytes(path)))
        args.append(TransactionArgument.to_U8Vector(data, hex=False))
        ty_args = self.get_type_args(currency_in)
        ty_args.extend(self.get_type_args(currency_out))

        script = Script.gen_script(CodeType.SWAP, *args, ty_args=ty_args, module_address= exchange_module_address)
        return self.submit_script(sender_account, script, is_blocking, **kwargs)

    def get_transaction(self, version, fetch_events:bool=True) -> Optional[TransactionView]:
        txs = self.get_transactions(version, 1, fetch_events)
        if len(txs):
            return txs[0]

    def get_transactions(self, start_version: int, limit: int, fetch_events: bool=True) -> [TransactionView]:
        txs = super().get_transactions(start_version, limit, fetch_events)
        return [TransactionView.new(tx) for tx in txs]

    def get_account_transaction(self, account_address: Union[bytes, str], sequence_number: int, fetch_events: bool=True) -> TransactionView:
        tx = super().get_account_transaction(account_address, sequence_number, fetch_events)
        if tx:
            return TransactionView.new(tx)

    def get_exchange_module_address(self, exchange_module_address=None):
        if exchange_module_address:
            return exchange_module_address
        if hasattr(self, "exchange_module_address"):
            return self.exchange_module_address
        ensure(False, "Not set exchange module address")

    def set_exchange_module_address(self, exchange_module_address):
        self.exchange_module_address = exchange_module_address
        update_hash_to_type_map(exchange_module_address)
        # self.swap_update_registered_currencies()

    def get_exchange_owner_address(self, exchange_owner_address=None):
        if exchange_owner_address:
            return exchange_owner_address
        if hasattr(self, "exchange_owner_address"):
            return self.exchange_owner_address
        if hasattr(self, "exchange_module_address"):
            return self.exchange_module_address
        ensure(False, "Not set exchange_owner_address")

    def set_exchange_owner_address(self, exchange_owner_address):
        self.exchange_owner_address = exchange_owner_address
        # self.swap_update_registered_currencies()

    def get_account_blob(self, account_address) -> Optional[AccountState]:
        blob = super().get_account_blob(account_address)
        if blob:
            state = AccountState.new(blob)
            if hasattr(self, "exchange_module_address"):
                state.set_exchange_module_address(self.exchange_module_address)
            return state

    def get_account_state(self, account_address) -> Optional[AccountState]:
        blob = super().get_account_blob(account_address)
        if blob:
            state = AccountState.new(blob)
            if hasattr(self, "exchange_module_address"):
                state.set_exchange_module_address(self.exchange_module_address)
            return state

    def swap_get_reserves_resource(self) -> Optional[ReservesResource]:
        exchange_module_address = self.get_exchange_module_address()
        exchange_owner_address = self.get_exchange_owner_address()
        blob = super().get_account_blob(exchange_owner_address)
        if blob:
            state = AccountState.new(blob)
            return state.swap_get_reserves_resource(exchange_module_address)
        return []

    def swap_get_liquidity_balances(self, liquidity_address):
        exchange_module_address = self.get_exchange_module_address()
        state = self.get_account_state(liquidity_address)
        if state:
            currencies = []
            reserves = self.swap_get_reserves_resource()
            resource = state.swap_get_tokens_resource(exchange_module_address)
            for token in resource.tokens:
                index = token.index
                value = token.value
                indexA = index >> 32
                indexB = index & 0xffffffff
                amounts = self.liquidity_to_coins(reserves, indexA, indexB, value)
                if amounts is not None:
                    codes = self.swap_get_currency_codes(indexA, indexB)
                    result = {
                        codes[0]: amounts[0],
                        codes[1]: amounts[1],
                        "liquidity":amounts[2]
                    }
                    currencies.append(result)
            return currencies

    def swap_get_swap_output_amount(self, currency_in, currency_out, amount_in):
        index_in = self.swap_get_currency_index(currency_in)
        index_out = self.swap_get_currency_index(currency_out)
        reserves = self.swap_get_reserves_resource()
        pairs = self.get_pairs(reserves)
        ret = self.best_trade_exact_in(reserves, pairs, index_in, index_out, amount_in, amount_in)
        assert len(ret) >= 1
        out_without_fee = self.get_output_amounts_without_fee(amount_in, ret[0][0])[-1]
        return ret[0][1], out_without_fee - ret[0][1]

    def swap_get_swap_input_amount(self, currency_in, currency_out, amount_out):
        index_in = self.swap_get_currency_index(currency_in)
        index_out = self.swap_get_currency_index(currency_out)
        reserves = self.swap_get_reserves_resource()
        pairs = self.get_pairs(reserves)
        ret = self.best_trade_exact_out(reserves, pairs, index_in, index_out, amount_out, amount_out)
        assert len(ret) >= 1
        out_without_fee = self.get_output_amounts_without_fee(ret[0][1], ret[0][0])[-1]
        return ret[0][1], out_without_fee - amount_out

    def swap_get_liquidity_out_amounts(self, currencyA, currencyB, liquidity_amount):
        indexA = self.swap_get_currency_index(currencyA)
        indexB = self.swap_get_currency_index(currencyB)
        reserves = self.swap_get_reserves_resource()
        amounts = self.liquidity_to_coins(reserves, indexA, indexB, liquidity_amount)
        return amounts[0], amounts[1]

    def swap_get_liquidity_output_amount(self, currency_in, currency_out, amount_in):
        index_in = self.swap_get_currency_index(currency_in)
        index_out = self.swap_get_currency_index(currency_out)
        reserves = self.swap_get_reserves_resource()
        reserve = self.get_reserve(reserves, index_in, index_out)
        return self.quote(amount_in, reserve.get_amountA(), reserve.get_amountB())

    def get_currency_max_output_path(self, currency_in, currency_out, amount_in):
        index_in = self.swap_get_currency_index(currency_in)
        index_out = self.swap_get_currency_index(currency_out)
        return self.get_index_max_output_path(index_in, index_out, amount_in)

    def get_currency_min_input_path(self, currency_in, currency_out, amount_out):
        index_in = self.swap_get_currency_index(currency_in)
        index_out = self.swap_get_currency_index(currency_out)
        return self.get_index_min_input_path(index_in, index_out, amount_out)

    '''.............................................Called internally.................................................................'''

    def get_index_max_output_path(self, index_in, index_out, amount_in):
        reserves = self.swap_get_reserves_resource()
        pairs = self.get_pairs(reserves)
        ret = self.best_trade_exact_in(reserves, pairs, index_in, index_out, amount_in, amount_in)
        assert len(ret) >= 1
        return ret[0][0]

    def get_index_min_input_path(self, index_in, index_out, amount_out):
        reserves = self.swap_get_reserves_resource()
        pairs = self.get_pairs(reserves)
        ret = self.best_trade_exact_out(reserves, pairs, index_in, index_out, amount_out, amount_out)
        assert len(ret) >= 1
        return ret[0][0]

    def get_reserve(self, reserves, indexA, indexB):
        min_index = min(indexA, indexB)
        max_index = max(indexA, indexB)
        for reserve in reserves:
            if min_index == reserve.coina.index and max_index == reserve.coinb.index:

                if indexA > indexB:
                    import copy
                    reserve_copy = copy.deepcopy(reserve)
                    reserve_copy.coina, reserve_copy.coinb = reserve.coinb, reserve.coina
                    return reserve_copy
                return reserve
        raise LibraError(data=ExchangeError.PAIR_ERROR, message=f"Can not find pair from {indexA} to {indexB}")

    
    def quote(self, amountA, reserveA, reserveB):
        assert reserveA > 0 and reserveB > 0
        amountB = int(amountA * reserveB / reserveA)
        if amountA * reserveB % reserveA != 0:
            amountB += 1
        return amountB

    def get_output_amount_without_fee(self, amount_in, reserve_in, reserve_out):
        amount_out = amount_in * reserve_out // (reserve_in + amount_in)
        return amount_out
    
    def get_output_amounts_without_fee(self, amount_in, path):
        amounts = []
        amounts.append(amount_in)
        reserves = self.swap_get_reserves_resource()
        for i in range(len(path) - 1):
            reserve = self.get_reserve(reserves, path[i], path[i + 1])
            reserve_in, reserve_out = reserve.get_amountA(), reserve.get_amountB()
            assert reserve_in > 0 and reserve_out > 0
            amount_out = self.get_output_amount_without_fee(amounts[i], reserve_in, reserve_out)
            amounts.append(amount_out)
        return amounts

    def get_output_amount(self, amount_in, reserve_in, reserve_out):
        assert reserve_in > 0 and reserve_out > 0
        amount_inWithFee = amount_in * 997
        numerator = amount_inWithFee * reserve_out
        denominator = reserve_in * 1000 + amount_inWithFee
        amount_out = numerator // denominator
        return amount_out

    def get_input_amount(self, amount_out, reserve_in, reserve_out):
        assert reserve_in > 0 and reserve_out > 0
        numerator = reserve_in * amount_out * 1000
        denominator = (reserve_out - amount_out) * 997
        amount_in = numerator // denominator + 1
        return amount_in

    def get_output_amounts(self, amount_in, path):
        amounts = []
        amounts.append(amount_in)
        reserves = self.swap_get_reserves_resource()
        for i in range(len(path) - 1):
            (reserve_in, reserve_out) = self.get_reserve(reserves, path[i], path[i + 1])
            assert reserve_in > 0 and reserve_out > 0
            amount_out = self.get_output_amount(amounts[i], reserve_in, reserve_out)
            amounts.append(amount_out)
        return amounts

    def get_input_amounts(self, amount_out, path):
        assert amount_out > 0 and len(path) >= 2
        amounts = [None] * len(path)
        amounts[len(path) - 1] = amount_out
        reserves = self.swap_get_reserves_resource()
        for i in range(len(path) - 1, 0, -1):
            (reserve_in, reserve_out) = self.get_reserve(reserves, path[i - 1], path[i])
            assert reserve_in > 0 and reserve_out > 0
            amounts[i - 1] = self.get_input_amount(amounts[i], reserve_in, reserve_out)
        return amounts

    def get_pairs(self, reserves):
        return [(reserve.coina.index, reserve.coinb.index) for reserve in reserves]

    def best_trade_exact_in(self, reserves, pairs, index_in, index_out, amount_in, original_amount_in, path=None, best_trades=None):
        assert len(pairs) > 0
        assert original_amount_in == amount_in or len(path) > 0
        if best_trades is None:
            best_trades = []
        if path is None:
            path = []
        if len(path) == 0:
            path.append(index_in)
        if len(path) > 3:
            return

        start_path = path[:]
        for i in range(0, len(pairs)):
            pair = pairs[i]
            if index_in == pair[0]:
                tmp_out = pair[1]
            elif index_in == pair[1]:
                tmp_out = pair[0]
            else:
                continue
            if tmp_out in path:
                continue
            reserve = self.get_reserve(reserves, index_in, tmp_out)
            reserve_in, reserve_out = reserve.get_amountA(), reserve.get_amountB()
            if reserve_in == 0 or reserve_out == 0:
                continue
            amount_out = self.get_output_amount(amount_in, reserve_in, reserve_out)
            if index_out == pair[0] or index_out == pair[1]:
                path.append(index_out)
                best_trades.append((path[:], amount_out))
                path = start_path[:]
            elif len(pairs) > 1:
                pairsExcludingThisPair = pairs[:]
                del (pairsExcludingThisPair[i])
                newPath = path + [tmp_out]
                self.best_trade_exact_in(reserves, pairsExcludingThisPair, tmp_out, index_out, amount_out, original_amount_in, newPath, best_trades)
        return sorted(best_trades, key=lambda k: k[1], reverse=True)

    def best_trade_exact_out(self, reserves, pairs, index_in, index_out, amount_out, original_amount_out, path=None, best_trades=None):
        assert len(pairs) > 0
        assert original_amount_out == amount_out or len(path) > 0
        if best_trades is None:
            best_trades = []
        if path is None:
            path = []
        if len(path) == 0:
            path.append(index_out)
        if len(path) > 3:
            return
        start_path = path[:]
        for i in range(0, len(pairs)):
            pair = pairs[i]
            if index_out == pair[0]:
                tmp_in = pair[1]
            elif index_out == pair[1]:
                tmp_in = pair[0]
            else:
                continue
            if tmp_in in path:
                continue
            reserve = self.get_reserve(reserves, tmp_in, index_out)
            reserve_in, reserve_out = reserve.get_amountA(), reserve.get_amountB()
            if reserve_in == 0 or reserve_out == 0:
                continue
            amount_in = self.get_input_amount(amount_out, reserve_in, reserve_out)
            if index_in in pair:
                path.insert(0, index_in)
                best_trades.append((path[:], amount_in))
                path = start_path[:]
            elif len(pairs) > 1:
                pairsExcludingThisPair = pairs[:]
                del (pairsExcludingThisPair[i])
                newPath = [tmp_in] + path
                self.best_trade_exact_out(reserves, pairsExcludingThisPair, index_in, tmp_in, amount_in, original_amount_out, newPath, best_trades)
        return sorted(best_trades, key=lambda k: k[1], reverse=False)

    def swap_get_registered_currencies(self, update=False):
        if update or not hasattr(self, "swap_currency_codes"):
            self.swap_update_registered_currencies()
        if hasattr(self, "swap_currency_codes"):
            return self.swap_currency_codes

    def swap_update_registered_currencies(self):
        exchange_module_address = self.get_exchange_module_address()
        exchange_owner_address = self.get_exchange_owner_address()
        state = self.get_account_state(exchange_owner_address)
        if state:
            registered_currencies = state.swap_get_registered_currencies(exchange_module_address)
            if registered_currencies:
                self.swap_currency_codes = registered_currencies.currency_codes
                return self.swap_currency_codes

    def swap_get_currency_index(self, currency_code):
        registered_currencies = self.swap_get_registered_currencies()
        ensure(registered_currencies is not None, "Registered_currencies is None")
        for index, code in enumerate(registered_currencies):
            if code == currency_code:
                return index
        self.swap_update_registered_currencies()
        for index, code in enumerate(registered_currencies):
            if code == currency_code:
                return index
        raise LibraError(data=ExchangeError.CURRENCY_NOT_REGISTERED, message=f"Currency {currency_code} not registered")

    def swap_get_currency_indexs(self, *args):
        ret = []
        for coin_name in args:
            ret.append(self.swap_get_currency_index(coin_name))
        return ret

    def swap_get_currency_code(self, id):
        registered_currencies = self.swap_get_registered_currencies()
        ensure(registered_currencies is not None, "Registered currencies is None")
        if len(registered_currencies) <= id:
            self.swap_update_registered_currencies()
        ensure(len(registered_currencies) > id, f"Registered currencies has no id {id}")
        return registered_currencies[id]

    def swap_get_currency_codes(self, *args):
        ret = []
        for id in args:
            ret.append(self.swap_get_currency_code(id))
        return ret

    def liquidity_to_coins(self, reserves, indexA, indexB, liquidity_amount):
        reserve = self.get_reserve(reserves, indexA, indexB)
        liquidity_total_supply = reserve.liquidity_total_supply
        amounta = liquidity_amount * reserve.get_amountA() // liquidity_total_supply
        amountb = liquidity_amount * reserve.get_amountB() // liquidity_total_supply
        return amounta, amountb, liquidity_amount




