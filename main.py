from bank.bank import Bank
import copy
bank = Bank()
b = copy.deepcopy(bank)
bank.height = 1
print(b.height)