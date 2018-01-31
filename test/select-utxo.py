# 实用贪心算法从UTXO列表中选择输出

from sys import argv

class OutputInfo:
    def __init__(self, tx_hash, tx_index, value):
        self.tx_hash = tx_hash
        self.tx_index = tx_index
        self.value = value

    def __repr__(self):
        return "<%s:%s with %s bitc>"%(self.tx_hash, self.tx_index,self.value)

def select_outputs_greedy(unspent, min_value):
    if not unspent: return None

    lessers = [utxo for utxo in unspent if utxo.value < min_value]
    greaters = [utxo for utxo in unspent if utxo.value >= min_value]
    key_func = lambda utxo: utxo.value

    if greaters:
        min_greater = min(greaters)
        change = min_greater.value - min_value
        return [min_greater], change

    lessers.sort(key=key_func, reverse=True)
    result = []
    accum = 0

    for utxo in lessers:
        result.append(utxo)
        accum += utxo.value
        if accum >= min_value:
            change = accum - min_value
            return result, "Change:%d Satoshis" % change
    
    return None, 0

def main():
    unspent = [
        OutputInfo("f2c245c38672a5d8fba5a5caa44dcef277a52e916a0603272f91286f2b052706",1,8450000),
        OutputInfo("0365fdc169b964ea5ad3219e12747e9478418fdc8abed2f5fe6d0205c96def29",0,100000),
        OutputInfo("d9717f774daab8d3dd470853204394c82e3c01097479575d6d2ee97d7b3bdfa1",0,1000000),
        OutputInfo("3f1df69df90d097981ca9c97ad8b6a32daed345565a433f8c8e472b2dab2ac79",1,719787),
        OutputInfo("417bdb6f5db3e830407f94d1a82d1667e738b19da3679b7263ebfb913394efdd",0,10000),
        OutputInfo("d049d6039f9d1cb2625bac294d7465b4b1077bd5bc0e30e01e02b184db524c1f",0,11100),
        OutputInfo("b8a6470c7a38d0983effed00a3f75c74ba371da1387352f35d1df155851ea8d1",0,10000),
        OutputInfo("a2b9570e26e3991fc999c42dc8c6eea7b06514b61814da1a71b56c6ba2ae651c",0,10000),
        OutputInfo("05230cb8cd8c6a3788ed41433dfdd68a1a608cc8feb3bc1c29d97ce84bec070e",0,10000),

    ]

    if len(argv) > 1:
        target = int(argv[1])
    else:
        target = 55000000

    print("For transaction amount %d Satoshis (%f bitcoin) use: "%(target, target/ 10.0**8))
    print(select_outputs_greedy(unspent, target))

if __name__ == '__main__':
    main()