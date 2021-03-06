'''   
    copyright 2018 to the roll_up Authors

    This file is part of roll_up.

    roll_up is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    roll_up is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with roll_up.  If not, see <https://www.gnu.org/licenses/>.
'''

import sys
import os

sys.path.insert(0, '/root/roll_up/pythonWrapper')
sys.path.insert(0, '/root/roll_up/contracts')
sys.path.insert(0, '/root/rpyc')
sys.path.insert(0, '/signer')

from wallet import Wallet
from prover import generate_witness, generate_transfer_proof
from contract_deploy import contract_deploy

from classes import SignedTransferTransaction
from utils import createLeaf, hashPadded
from SparseMerkleTree import SparseMerkleTree
 
nWallets = 4
alice = [ os.environ['ALICE_PK_X'], os.environ['ALICE_PX_Y'] ]
bob = [ os.environ['BOB_PK_X'], os.environ['BOB_PX_Y'] ]
RHS_LEAF = os.environ['RHS_LEAF']
TREE_DEPTH = ops.environ['TREE_DEPTH']

if __name__ == "__main__":
    # give nft 2 to alice and 3 to bob
    leaves = { 2: createLeaf(alice, rhs_leaf), 3: createLeaf(bob, rhs_leaf) }
    tree = SparseMerkleTree(2, leaves)
    root = tree.root
    old_leaf = []
    new_leaf = []
    roll_up = contract_deploy(
            TREE_DEPTH,
            "../depends/roll_up/keys/vk.json", 
            root,
            "../depends/roll_up/contracts",
            )

    # Wallet array
    wallets = []
    txs = []

    for i in range(nWallets):
        wallets.append(Wallet())

    # Iterate over transactions
    for j in range(nWallets-1):

        # New wallet
        wallet = wallets[j]
        
        # The old leaf is previous pubkey + previous message
        old_leaf.append(createLeaf(wallet.public_key, rhs_leaf))
        
        # The new leaf is current pubkey with current message
        new_leaf.append(createLeaf(wallets[j+1].public_key, rhs_leaf))
        
        # The message to sign is the previous leaf with the new leaf
        message = hashPadded(old_leaf[j], new_leaf[j])
        
        # Remove '0x' from byte
        message = message[2:]

        # Obtain Signature 
        r,s = wallet.sign(message)

        # Tx object
        txs.append(SignedTransferTransaction(wallet.public_key, wallet.secret_key, 1, r, s))

        print(txs[j])
    
    # # Get zk proof and merkle root
    proof, _root = generate_transfer_proof(txs)

    proof["a"] = hex2int(proof["a"])
    proof["a_p"] = hex2int(proof["a_p"])
    proof["b"] = [hex2int(proof["b"][0]), hex2int(proof["b"][1])]
    proof["b_p"] = hex2int(proof["b_p"])
    proof["c"] = hex2int(proof["c"])
    proof["c_p"] = hex2int(proof["c_p"])
    proof["h"] = hex2int(proof["h"])
    proof["k"] = hex2int(proof["k"])
    proof["input"] = hex2int(proof["input"])

    # #root , merkle_tree = utils.genMerkelTree(TREE_DEPTH, leaves[0])

    # TODO do the rest of the testing :)
