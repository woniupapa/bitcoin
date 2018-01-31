#从blockchain API中获得未花费的输出
import json
import requests

#样例地址
address='1Cdid9KFAaatwczBwBttQcwXYCpvK8h7FK'

resp = requests.get('https://blockchain.info/unspent?active=%s' % address)
utxo_set = json.loads(resp.text)['unspent_outputs']

for utxo in utxo_set:
    print("%s:%d - %ld stoshis" % (utxo['tx_hash'], utxo['tx_output_n'], utxo['value']))