import math


class Base():
        
    def getPairs(self):
        pass

    def getCurrencys(self):
        pass    
    
    def get_reserve(self, CoinA, CoinB):
        pass
    
    def quote(self, amountA, reserveA, reserveB):
        assert amountA > 0 and reserveA > 0 and reserveB > 0
        amountB = amountA * reserveB // reserveA
        return amountB

    def getOutputAmountWithoutFee(self, amountIn, reserveIn, reserveOut):
        assert amountIn > 0 and reserveIn > 0 and reserveOut
        amountOut = amountIn * reserveOut // (reserveIn + amountIn);
        return amountOut

    def getOutputAmountsWithoutFee(self, amountIn, path):
        assert amountIn > 0 and len(path) >= 2
        amounts = []
        amounts.append(amountIn)
        for i in range(len(path) - 1):
            (reserveIn, reserveOut) = self.get_reserve(path[i], path[i + 1])
            assert reserveIn > 0 and reserveOut > 0
            amountOut = self.getOutputAmountWithoutFee(amounts[i], reserveIn, reserveOut)
            amounts.append(amountOut)
        return amounts
    
    def getOutputAmount(self, amountIn, reserveIn, reserveOut):
        assert amountIn > 0 and reserveIn > 0 and reserveOut
        amountInWithFee = amountIn * 997;
        numerator = amountInWithFee * reserveOut;
        denominator = reserveIn * 1000 + amountInWithFee;
        amountOut = numerator // denominator;
        return amountOut

    def getInputAmount(self, amountOut, reserveIn, reserveOut):
        assert amountOut > 0 and reserveIn > 0 and reserveOut
        numerator = reserveIn * amountOut * 1000;
        denominator = (reserveOut - amountOut) * 997;
        amountIn = numerator // denominator + 1;
        return amountIn

    def getOutputAmounts(self, amountIn, path):
        assert amountIn > 0 and len(path) >= 2
        amounts = []
        amounts.append(amountIn)
        for i in range(len(path) - 1):
            (reserveIn, reserveOut) = self.get_reserve(path[i], path[i + 1])
            assert reserveIn > 0 and reserveOut > 0
            amountOut = self.getOutputAmount(amounts[i], reserveIn, reserveOut)
            amounts.append(amountOut)
        return amounts

    def getInputAmounts(self, amountOut, path):
        assert amountOut > 0 and len(path) >= 2
        amounts = [None] * len(path)
        amounts[len(path) - 1] = amountOut
        for i in range(len(path) - 1, 0, -1):
            (reserveIn, reserveOut) = self.get_reserve(path[i - 1], path[i])
            assert reserveIn > 0 and reserveOut > 0
            amounts[i - 1] = self.getInputAmount(amounts[i], reserveIn, reserveOut)
        return amounts

    def bestTradeExactIn(self, pairs, idIn, idOut, amountIn, originalAmountIn, path=[], bestTrades=[]):
        assert len(pairs) > 0
        assert originalAmountIn == amountIn or len(path) > 0
        if len(path) == 0:
            path.append(idIn)
        for i in range(0, len(pairs)):
            pair = pairs[i]
            (reserveIn, reserveOut) = self.get_reserve(pair[0], pair[1])
            if pair[0] != idIn and pair[1] != idIn:
                continue
            if reserveIn == 0 or reserveOut == 0:
                continue
            amountOut = self.getOutputAmount(amountIn, reserveIn, reserveOut)
            newIdIn = pair[1] if idIn == pair[0] else pair[0]
            if idOut == pair[0] or idOut == pair[1]:
                path.append(idOut)
                bestTrades.append((path, amountOut))
            elif len(pairs) > 1:
                pairsExcludingThisPair = pairs[:]
                del (pairsExcludingThisPair[i])
                newPath = path + [newIdIn]
                self.bestTradeExactIn(pairsExcludingThisPair, newIdIn, idOut, amountOut, originalAmountIn, newPath, bestTrades)
    
        return sorted(bestTrades, key=lambda k: k[1], reverse=True)
    
    
    def bestTradeExactOut(self, pairs, idIn, idOut, amountOut, originalAmountOut, path=[], bestTrades=[]):
        assert len(pairs) > 0
        assert originalAmountOut == amountOut or len(path) > 0
        if len(path) == 0:
            path.append(idOut)
        for i in range(0, len(pairs)):
            pair = pairs[i]
            (reserveIn, reserveOut) = self.get_reserve(pair[0], pair[1])
            if pair[0] != idOut and pair[1] != idOut:
                continue
            if reserveIn == 0 or reserveOut == 0:
                continue
            amountIn = self.getInputAmount(amountOut, reserveIn, reserveOut)
            newIdOut = pair[1] if idOut == pair[0] else pair[0]
            if idIn == pair[0] or idIn == pair[1]:
                path.insert(0, idIn)
                bestTrades.append((path, amountIn))
            elif len(pairs) > 1:
                pairsExcludingThisPair = pairs[:]
                del (pairsExcludingThisPair[i])
                newPath = [newIdOut] + path
                self.bestTradeExactOut(pairsExcludingThisPair, idIn, newIdOut, amountIn, originalAmountOut, newPath, bestTrades)
    
        return sorted(bestTrades, key=lambda k: k[1], reverse=True)