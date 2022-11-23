# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from eth_utils import function_signature_to_4byte_selector

from ethereum_dasm.evmdasm import EvmCode, Contract


class EthContractService:

    def get_function_sighashes(self, bytecode):
        bytecode = clean_bytecode(bytecode)
        if bytecode is not None:
            evm_code = EvmCode(contract=Contract(bytecode=bytecode), static_analysis=False, dynamic_analysis=False)
            evm_code.disassemble(bytecode)
            basic_blocks = evm_code.basicblocks
            if basic_blocks and len(basic_blocks) > 0:
                push4_instructions = set()
                for block in basic_blocks:
                    instructions = block.instructions
                    block_push4_instructions = [inst for inst in instructions if inst.name == 'PUSH4']
                    push4_instructions.update(block_push4_instructions)
                
                return sorted(list({'0x' + inst.operand for inst in push4_instructions}))
            else:
                return []
        else:
            return []

    # https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20.md
    # https://github.com/OpenZeppelin/openzeppelin-solidity/blob/master/contracts/token/ERC20/ERC20.sol
    def is_erc20_contract(self, function_sighashes):
        c = ContractWrapper(function_sighashes)
        return all([
            c.implements('totalSupply()'),
            c.implements('balanceOf(address)'),
            c.implements('transfer(address,uint256)'),
            c.implements('transferFrom(address,address,uint256)'),
            c.implements('approve(address,uint256)'),
            c.implements('allowance(address,address)')
        ])

    # https://github.com/ethereum/EIPs/blob/master/EIPS/eip-721.md
    # https://github.com/OpenZeppelin/openzeppelin-solidity/blob/master/contracts/token/ERC721/ERC721Basic.sol
    # CryptoKitties contracts doesn't strictly implement erc721 interface
    # so we have to check for it's sighashes explicitly
    def is_erc721_contract(self, function_sighashes):
        c = ContractWrapper(function_sighashes)
        return all([
            c.implements('balanceOf(address)'),
            c.implements('ownerOf(uint256)'),
            c.implements_any_of('transfer(address,uint256)', 'transferFrom(address,address,uint256)'),
            c.implements('approve(address,uint256)'),
            c.implements('getApproved(uint256)'),
            c.implements('setApprovalForAll(address,bool)'),
            c.implements('isApprovedForAll(address,address)'),
            c.implements('transferFrom(address,address,uint256)'),
            c.implements('safeTransferFrom(address,address,uint256)'),
            c.implements('safeTransferFrom(address,address,uint256,bytes)'),
        ]) or self.is_crypto_kitties_contract(function_sighashes) 

    # https://etherscan.io/address/0x06012c8cf97bead5deae237070f9587f8e7a266d#code#L52
    def is_crypto_kitties_contract(self, function_sighashes):
        return function_sighashes == [
            '0x01ffc9a7', '0x0519ce79', '0x0560ff44', '0x05e45546', '0x06fdde03', '0x095ea7b3','0x0a0f8168',
            '0x0d9f5aed', '0x0e583df0', '0x14001f4c', '0x18160ddd', '0x183a7947', '0x1940a936', '0x19c2f201',
            '0x21717ebf', '0x23b872dd', '0x24e7a38a', '0x27d7874c', '0x27ebe40a', '0x2ba73c15', '0x3d7d3f5a',
            '0x3f4ba83a', '0x454a2ab3', '0x46116e6f', '0x46d22c70', '0x481af3d3', '0x4ad8c938', '0x4b85fd55',
            '0x4dfff04f', '0x4e0a3379', '0x54c15b82', '0x56129134', '0x5663896e', '0x5c975abb', '0x5fd8c710',
            '0x6352211e', '0x680eba27', '0x6af04a57', '0x6fbde40d', '0x70a08231', '0x71587988', '0x76190f8f',
            '0x7a7d4937', '0x8456cb59', '0x8462151c', '0x85b86188', '0x88c2a0bf', '0x91876e57', '0x95d89b41',
            '0x9d6fac6f', '0xa45f4bfc', '0xa9059cbb', '0xb047fb50', '0xb0c35c05', '0xbc4006f5', '0xc3bea9af',
            '0xc55d0f56', '0xcb4799f2', '0xd3e6f49f', '0xdefb9584', '0xe17b25af', '0xe6cbe351', '0xe98b7f4d',
            '0xeac9d94c', '0xed60ade6', '0xf1ca9410', '0xf2b47d52', '0xf7d8c883', '0xffffffff'
        ]


def clean_bytecode(bytecode):
    if bytecode is None or bytecode == '0x':
        return None
    elif bytecode.startswith('0x'):
        return bytecode[2:]
    else:
        return bytecode


def get_function_sighash(signature):
    return '0x' + function_signature_to_4byte_selector(signature).hex()


class ContractWrapper:
    def __init__(self, sighashes):
        self.sighashes = sighashes

    def implements(self, function_signature):
        sighash = get_function_sighash(function_signature)
        return sighash in self.sighashes

    def implements_any_of(self, *function_signatures):
        return any(self.implements(function_signature) for function_signature in function_signatures)
