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

from ethereum_dasm.evmdasm import EVMCode


class EthContractService:

    def __init__(self):
        self._evm_dasm = EVMCode()

    def get_function_sighashes(self, bytecode):
        disassembled_code = self._evm_dasm.disassemble(bytecode)
        basic_blocks = list(self._evm_dasm.basicblocks(disassembled_code))
        if basic_blocks and len(basic_blocks) > 0:
            init_block = basic_blocks[0]
            instructions = init_block.instructions
            push4_instructions = [inst for inst in instructions if inst.name == 'PUSH4']
            return sorted(list(set('0x' + inst.operand for inst in push4_instructions)))
        else:
            return []


# https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20.md
# Fuzzy matching either transfer(address,uint256) or transferFrom(address,address,uint256) for consistency
# with ERC721 (see below)
def is_erc20_contract(function_sighashes):
    c = ContractWrapper(function_sighashes)
    return c.implements('totalSupply()') and \
           c.implements('balanceOf(address)') and \
           c.implements_any_of('transfer(address,uint256)', 'transferFrom(address,address,uint256)')


# https://github.com/ethereum/EIPs/blob/master/EIPS/eip-721.md
# In the standard only transferFrom(address,address,uint256) is defined, but many contracts implement
# only transfer(address,uint256) so this function makes a fuzzy check.
def is_erc721_contract(function_sighashes):
    c = ContractWrapper(function_sighashes)
    return c.implements('ownerOf(uint256)') and \
           c.implements('balanceOf(address)') and \
           c.implements_any_of('transfer(address,uint256)', 'transferFrom(address,address,uint256)')


def get_function_sighash(signature):
    return '0x' + function_signature_to_4byte_selector(signature).hex()


class ContractWrapper:
    def __init__(self, sighashes):
        self.sighashes = sighashes

    def implements(self, function_signature):
        sighash = get_function_sighash(function_signature)
        return sighash in self.sighashes

    def implements_any_of(self, *function_signatures):
        result = False
        for function_signature in function_signatures:
            result = result or self.implements(function_signature)
            return result
