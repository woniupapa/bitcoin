#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test various fingerprinting protections.

If an stale block more than a month old or its header are requested by a peer,
the node should pretend that it does not have it to avoid fingerprinting.
"""

import time

from test_framework.blocktools import (create_block, create_coinbase)
from test_framework.mininode import (
    CInv,
    P2PInterface,
    msg_headers,
    msg_block,
    msg_getdata,
    msg_getheaders,
    network_thread_start,
    wait_until,
)
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import (
    assert_equal,
)

import urllib.parse
import subprocess

class P2PFingerprintTest(BitcoinTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 1

    # Build a chain of blocks on top of given one
    def build_chain(self, nblocks, prev_hash, prev_height, prev_median_time):
        blocks = []
        for _ in range(nblocks):
            coinbase = create_coinbase(prev_height + 1)
            block_time = prev_median_time + 1
            block = create_block(int(prev_hash, 16), coinbase, block_time)
            block.solve()

            blocks.append(block)
            prev_hash = block.hash
            prev_height += 1
            prev_median_time = block_time
        return blocks

    # Send a getdata request for a given block hash
    # 通过getdata给某个hash的单个区块
    def send_block_request(self, block_hash, node):
        msg = msg_getdata()
        msg.inv.append(CInv(2, block_hash))  # 2 == "Block"
        node.send_message(msg)

    # Send a getheaders request for a given single block hash
    # 发送getheaders给某个hash的单个区块
    def send_header_request(self, block_hash, node):
        msg = msg_getheaders()
        msg.hashstop = block_hash
        node.send_message(msg)

    # Check whether last block received from node has a given hash
    # 检测是否从node接收到上个区块的hash是否相等
    def last_block_equals(self, expected_hash, node):
        block_msg = node.last_message.get("block")
        return block_msg and block_msg.block.rehash() == expected_hash

    # Check whether last block header received from node has a given hash
    # 检测是否上个区块头是否等于hash
    def last_header_equals(self, expected_hash, node):
        headers_msg = node.last_message.get("headers")
        return (headers_msg and
                headers_msg.headers and
                headers_msg.headers[0].rehash() == expected_hash)

    # Checks that stale blocks timestamped more than a month ago are not served
    # by the node while recent stale blocks and old active chain blocks are.
    # This does not currently test that stale blocks timestamped within the
    # last month but that have over a month's worth of work are also withheld.
    def run_test(self):
        
        #logfilePath = self.options.tmpdir + '/test_framework.log'

        #self.log.info(logfilePath)

        #subprocess.call(['open', '-W', '-a', 'Terminal.app', 'tail', '-f', logfilePath])
        #subprocess.call(['tail', '-f', logfilePath])

        #nodetest = P2PInterface();
        #node0表示测试节点  self.nodes[0]表示bitcoin实际节点
        node0 = self.nodes[0].add_p2p_connection(P2PInterface())

        #节点信息这里是指连上bitcoin实际节点的节点信息
        #networkinfo = self.nodes[0].getnetworkinfo()
        #self.log.info(networkinfo)

        #url = urllib.parse.urlparse(self.nodes[0].url)
        #self.log.info(url)


        network_thread_start()
        node0.wait_for_verack()

        # Set node time to 60 days ago
        # 将时间调整到2个月之前
        mocktime = int(time.time()) - 60 * 24 * 60 * 60
        self.nodes[0].setmocktime(mocktime)

        #nblocks=10
        nblocks = 5

        # Generating a chain of 10 blocks
        #生成10个区块链
        block_hashes = self.nodes[0].generate(nblocks)

        #for hash in block_hashes:
        #    self.log.info(' Node: [%d]:%s' % (i, hash))

        #for i in range(block_hashes):
        #    self.log.info(' Node: [%d]:%s' % (i, block_hashes[i]))

        for i, hash in enumerate(block_hashes):
            self.log.info('[notice] [%d]:%s' % (i, hash))
            #self.log.info('%d:%s'% (i,int(hash, 16)))

        self.log.info('[notice] generate node %d' % len(block_hashes))
        

        # 在regnet情况下创世块的hash是0f9188f13cb7b2c71f2a335e3a4fc328bf5beb436012afca590b1a11466e2206
        #getblockhash0 = self.nodes[0].getblockhash(0)

        
        # Create longer chain starting 2 blocks before current tip
        height = len(block_hashes) - 2
        block_hash = block_hashes[height - 1]

        self.log.info('[notice] starting %d:%s' % (height , block_hash))

        # median time 中位时间
        block_time = self.nodes[0].getblockheader(block_hash)["mediantime"] + 1
        
        new_blocks = self.build_chain(5, block_hash, height, block_time)

        for i, hash in enumerate(new_blocks):
            self.log.info('[notice] n [%d]:%s' % (i, hash.hash))
            #self.log.info('%d'% (int(hash.hash, 16)))

        # Force reorg to a longer chain
        # 向self.nodes[0]实际节点发送headers消息告诉它最新的节点数据
        node0.send_message(msg_headers(new_blocks))
        node0.wait_for_getdata()
        for block in new_blocks:
            node0.send_and_ping(msg_block(block))

        #blockcount = self.nodes[0].getblockcount()

        # Check that reorg succeeded
        # 检测self.nodes[0]该节点上区块数量
        assert_equal(self.nodes[0].getblockcount(), 13)

        #取出block_hashes里面最后一条hash数据并且将它转化成16进制
        stale_hash = int(block_hashes[-1], 16)

        # Check that getdata request for stale block succeeds
        # 检测getdata请求发送陈旧的块的hash给self.nodes[0]
        self.send_block_request(stale_hash, node0)
        test_function = lambda: self.last_block_equals(stale_hash, node0)
        wait_until(test_function, timeout=3)

        # Check that getheader request for stale block header succeeds
        self.send_header_request(stale_hash, node0)
        test_function = lambda: self.last_header_equals(stale_hash, node0)
        wait_until(test_function, timeout=3)

        # Longest chain is extended so stale is much older than chain tip
        self.nodes[0].setmocktime(0)
        tip = self.nodes[0].generate(nblocks=1)[0]
        assert_equal(self.nodes[0].getblockcount(), 14)

        # Send getdata & getheaders to refresh last received getheader message
        block_hash = int(tip, 16)
        self.send_block_request(block_hash, node0)
        self.send_header_request(block_hash, node0)
        node0.sync_with_ping()

        # Request for very old stale block should now fail
        self.send_block_request(stale_hash, node0)
        time.sleep(3)
        assert not self.last_block_equals(stale_hash, node0)

        # Request for very old stale block header should now fail
        self.send_header_request(stale_hash, node0)
        time.sleep(3)
        assert not self.last_header_equals(stale_hash, node0)

        # Verify we can fetch very old blocks and headers on the active chain
        block_hash = int(block_hashes[2], 16)
        self.send_block_request(block_hash, node0)
        self.send_header_request(block_hash, node0)
        node0.sync_with_ping()

        self.send_block_request(block_hash, node0)
        test_function = lambda: self.last_block_equals(block_hash, node0)
        wait_until(test_function, timeout=3)

        self.send_header_request(block_hash, node0)
        test_function = lambda: self.last_header_equals(block_hash, node0)
        wait_until(test_function, timeout=3)

if __name__ == '__main__':
    P2PFingerprintTest().main()
