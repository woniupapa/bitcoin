#!/usr/bin/env python3
# Copyright (c) 2015-2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test p2p mempool message.

Test that nodes are disconnected if they send mempool messages when bloom
filters are not enabled.
"""

from test_framework.mininode import *
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import *

class TestNode(P2PInterface):
    def on_version(self, message):
        # Don't send a verack in response
        pass

class P2PMempoolTests(BitcoinTestFramework):
    def set_test_params(self):
        #这里作用
        self.setup_clean_chain = True
        #节点数量1
        self.num_nodes = 1
        #外部参数
        self.extra_args = [["-peerbloomfilters=0"]]

    def run_test(self):

        # Add a p2p connection
        #self.nodes[0].add_p2p_connection(P2PInterface())

        #直接使用P2PInterface来做连接

        testNode1 = P2PInterface()
        #testNode2 = P2PInterface()

        self.nodes[0].add_p2p_connection(testNode1)
        #self.nodes[0].add_p2p_connection(testNode2)

        network_thread_start()
        
        #等待P2PInterface()节点发送version 然后nodes[0]发送
        self.nodes[0].p2p.wait_for_verack()

        peerinfo = self.nodes[0].getpeerinfo()

        #request mempool nodes[0]发送了msg_mempool指令所有的节点都会被断开??
        # 
        self.nodes[0].p2p.send_message(msg_mempool())

        peerinfo = self.nodes[0].getpeerinfo()

        #
        self.nodes[0].p2p.wait_for_disconnect()

        #mininode must be disconnected at this point
        peerinfo = self.nodes[0].getpeerinfo()
        assert_equal(len(peerinfo), 0)
    
if __name__ == '__main__':
    P2PMempoolTests().main()
