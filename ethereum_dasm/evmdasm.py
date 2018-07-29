#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Author : <github.com/tintinweb>
# from future import print_function
"""
Verbose EthereumVM Disassembler

OPCODES taken from:
    https://github.com/ethereum/go-ethereum/blob/master/core/vm/opcodes.go
    https://github.com/ethereum/yellowpaper/blob/master/Paper.tex
"""

import logging
import sys
import os
import itertools
import time
import requests

try:
    import ethereum_input_decoder
except ImportError:
    ethereum_input_decoder = None


logger = logging.getLogger(__name__)


def hex_decode(s):
    try:
        return bytes.fromhex(s).decode('ascii')
    except (NameError, AttributeError):
        return s.decode("hex")
    except (UnicodeDecodeError):
        return ''  #invalid


def is_ascii_subsequence(s, min_percent=0.51):
    if len(s) == 0:
        return False
    return [128 > ord(c) > 0x20 for c in s].count(True) / float(len(s)) >= min_percent


cache_lookup_function_signature = {}  # memcache for lookkup_function_signature


def lookup_function_signature(sighash):
    if not ethereum_input_decoder:
        return []
    cache_hit = cache_lookup_function_signature.get(sighash)
    if cache_hit:
        return cache_hit
    cache_lookup_function_signature[sighash] = list(ethereum_input_decoder.decoder.FourByteDirectory.lookup_signatures(sighash))
    return cache_lookup_function_signature[sighash]


class EthJsonRpc(object):

    def __init__(self, url):
        self.url = url
        self.id = 1
        self.session = requests.session()

    def call(self, method, params=None):

        params = params or []
        data = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': self.id,
        }
        headers = {'Content-Type': 'application/json'}
        resp = self.session.post(self.url, headers=headers, json=data)

        self.id += 1
        return resp.json()


class BasicBlock(object):

    def __init__(self, address=None, name=None, instructions=None):
        self.instructions = instructions or []
        self.address = address
        self.name = name

    def __repr__(self):
        return "<BasicBlock 0x%x instructions:%d>" % (self.address, len(self.instructions))


class Instruction(object):
    """ Base Instruction class

        doubly linked
    """

    def __init__(self, opcode, name, length_of_operand=0, description=None):
        self.opcode, self.name, self.length_of_operand = opcode, name, length_of_operand
        self.operand = ''
        self.description = description
        self.address = None
        self.next = None
        self.previous = None
        self.xrefs = set([])
        self.jumpto = None
        self.basicblock = None

    def __repr__(self):
        return "<%s name=%s address=%s size=%d>" % (self.__class__.__name__, self.name, hex(self.address), self.size())

    def __str__(self):
        return "%s %s" % (self.name, "0x%s" % self.operand if self.operand else '')

    def size(self):
        return 1 + len(self.operand) // 2  # opcode + operand

    def consume(self, bytecode):
        # clone
        m = Instruction(opcode=self.opcode,
                        name=self.name,
                        length_of_operand=self.length_of_operand,
                        description=self.description)
        # consume
        m.operand = ''.join('%0.2x' % _ for _ in itertools.islice(bytecode, m.length_of_operand))
        return m

    def serialize(self):
        return '%0.2x' % self.opcode + self.operand

    def describe_operand(self, resolve_funcsig=False):
        if not self.operand:
            str_operand = ''
        elif resolve_funcsig and len(self.operand) == 8 and self.address < 0x100:
            # speed improvment: its very unlikely that there will be funcsigs after addr 400
            # 4bytes, could be a func-sig
            pot_funcsigs = lookup_function_signature(self.operand)
            if len(pot_funcsigs) == 0:
                ascii = ''
            elif len(pot_funcsigs) == 1:
                ascii = '  (\'function %s\')' % pot_funcsigs[0]
            else:
                ascii = '  (*ambiguous* \'function %s\')' % pot_funcsigs[0]

            str_operand = "0x%s%s" % (self.operand, ascii)
        elif len(self.operand) > 8:
            ascii = ' (%r)' % hex_decode(self.operand) \
                if self.operand and is_ascii_subsequence(hex_decode(self.operand)) else ''
            str_operand = "0x%s%s" % (self.operand, ascii)
        else:
            ascii = ''
            str_operand = "0x%s%s" % (self.operand, ascii)

        extra = "@%s" % hex(self.jumpto) if self.jumpto else ''
        return "%s%s" % (str_operand, extra)


OPCODES = [
    # Stop and Arithmetic Operations
    Instruction(opcode=0x00, name='STOP', description="Halts execution."),
    Instruction(opcode=0x01, name='ADD', description="Addition operation."),
    Instruction(opcode=0x02, name='MUL', description="Multiplication operation."),
    Instruction(opcode=0x03, name='SUB', description="Subtraction operation."),
    Instruction(opcode=0x04, name='DIV', description="Integer division operation."),
    Instruction(opcode=0x05, name='SDIV', description="Signed integer"),
    Instruction(opcode=0x06, name='MOD', description="Modulo"),
    Instruction(opcode=0x07, name='SMOD', description="Signed modulo"),
    Instruction(opcode=0x08, name='ADDMOD', description="Modulo"),
    Instruction(opcode=0x09, name='MULMOD', description="Modulo"),
    Instruction(opcode=0x0a, name='EXP', description="Exponential operation."),
    Instruction(opcode=0x0b, name='SIGNEXTEND', description="Extend length of two’s complement signed integer."),

    # Comparison & Bitwise Logic Operations
    Instruction(opcode=0x10, name='LT', description="Lesser-than comparison"),
    Instruction(opcode=0x11, name='GT', description="Greater-than comparison"),
    Instruction(opcode=0x12, name='SLT', description="Signed less-than comparison"),
    Instruction(opcode=0x13, name='SGT', description="Signed greater-than comparison"),
    Instruction(opcode=0x14, name='EQ', description="Equality  comparison"),
    Instruction(opcode=0x15, name='ISZERO', description="Simple not operator"),
    Instruction(opcode=0x16, name='AND', description="Bitwise AND operation."),
    Instruction(opcode=0x17, name='OR', description="Bitwise OR operation."),
    Instruction(opcode=0x18, name='XOR', description="Bitwise XOR operation."),
    Instruction(opcode=0x19, name='NOT', description="Bitwise NOT operation."),
    Instruction(opcode=0x1a, name='BYTE', description="Retrieve single byte from word"),

    # SHA3
    Instruction(opcode=0x20, name='SHA3', description="Compute Keccak-256 hash."),

    # Environmental Information
    Instruction(opcode=0x30, name='ADDRESS', description="Get address of currently executing account."),
    Instruction(opcode=0x31, name='BALANCE', description="Get balance of the given account."),
    Instruction(opcode=0x32, name='ORIGIN', description="Get execution origination address."),
    Instruction(opcode=0x33, name='CALLER',
                description="Get caller address.This is the address of the account that is directly responsible for this execution."),
    Instruction(opcode=0x34, name='CALLVALUE',
                description="Get deposited value by the instruction/transaction responsible for this execution."),
    Instruction(opcode=0x35, name='CALLDATALOAD', description="Get input data of current environment."),
    Instruction(opcode=0x36, name='CALLDATASIZE', description="Get size of input data in current environment."),
    Instruction(opcode=0x37, name='CALLDATACOPY',
                description="Copy input data in current environment to memory. This pertains to the input data passed with the message call instruction or transaction."),
    Instruction(opcode=0x38, name='CODESIZE', description="Get size of code running in current environment."),
    Instruction(opcode=0x39, name='CODECOPY', description="Copy code running in current environment to memory."),
    Instruction(opcode=0x3a, name='GASPRICE', description="Get price of gas in current environment."),
    Instruction(opcode=0x3b, name='EXTCODESIZE', description="Get size of an account’s code."),
    Instruction(opcode=0x3c, name='EXTCODECOPY', description="Copy an account’s code to memory."),
    Instruction(opcode=0x3d, name='RETURNDATASIZE',
                description="Push the size of the return data buffer onto the stack."),
    Instruction(opcode=0x3e, name='RETURNDATACOPY', description="Copy data from the return data buffer."),

    # Block Information
    Instruction(opcode=0x40, name='BLOCKHASH',
                description="Get the hash of one of the 256 most recent complete blocks."),
    Instruction(opcode=0x41, name='COINBASE', description="Get the block’s beneficiary address."),
    Instruction(opcode=0x42, name='TIMESTAMP', description="Get the block’s timestamp."),
    Instruction(opcode=0x43, name='NUMBER', description="Get the block’s number."),
    Instruction(opcode=0x44, name='DIFFICULTY', description="Get the block’s difficulty."),
    Instruction(opcode=0x45, name='GASLIMIT', description="Get the block’s gas limit."),

    # Stack, Memory, Storage and Flow Operations
    Instruction(opcode=0x50, name='POP', description="Remove item from stack."),
    Instruction(opcode=0x51, name='MLOAD', description="Load word from memory."),
    Instruction(opcode=0x52, name='MSTORE', description="Save word to memory."),
    Instruction(opcode=0x53, name='MSTORE8', length_of_operand=0x8, description="Save byte to memory."),
    Instruction(opcode=0x54, name='SLOAD', description="Load word from storage."),
    Instruction(opcode=0x55, name='SSTORE', description="Save word to storage."),
    Instruction(opcode=0x56, name='JUMP', description="Alter the program counter."),
    Instruction(opcode=0x57, name='JUMPI', description="Conditionally alter the program counter."),
    Instruction(opcode=0x58, name='PC', description="Get the value of the program counter prior to the increment."),
    Instruction(opcode=0x59, name='MSIZE', description="Get the size of active memory in bytes."),
    Instruction(opcode=0x5a, name='GAS',
                description="Get the amount of available gas, including the corresponding reduction"),
    Instruction(opcode=0x5b, name='JUMPDEST', description="Mark a valid destination for jumps."),

    # Stack Push Operations
    Instruction(opcode=0x60, name='PUSH1', length_of_operand=0x1, description="Place 1 byte item on stack."),
    Instruction(opcode=0x61, name='PUSH2', length_of_operand=0x2, description="Place 2-byte item on stack."),
    Instruction(opcode=0x62, name='PUSH3', length_of_operand=0x3, description="Place 3-byte item on stack."),
    Instruction(opcode=0x63, name='PUSH4', length_of_operand=0x4, description="Place 4-byte item on stack."),
    Instruction(opcode=0x64, name='PUSH5', length_of_operand=0x5, description="Place 5-byte item on stack."),
    Instruction(opcode=0x65, name='PUSH6', length_of_operand=0x6, description="Place 6-byte item on stack."),
    Instruction(opcode=0x66, name='PUSH7', length_of_operand=0x7, description="Place 7-byte item on stack."),
    Instruction(opcode=0x67, name='PUSH8', length_of_operand=0x8, description="Place 8-byte item on stack."),
    Instruction(opcode=0x68, name='PUSH9', length_of_operand=0x9, description="Place 9-byte item on stack."),
    Instruction(opcode=0x69, name='PUSH10', length_of_operand=0xa, description="Place 10-byte item on stack."),
    Instruction(opcode=0x6a, name='PUSH11', length_of_operand=0xb, description="Place 11-byte item on stack."),
    Instruction(opcode=0x6b, name='PUSH12', length_of_operand=0xc, description="Place 12-byte item on stack."),
    Instruction(opcode=0x6c, name='PUSH13', length_of_operand=0xd, description="Place 13-byte item on stack."),
    Instruction(opcode=0x6d, name='PUSH14', length_of_operand=0xe, description="Place 14-byte item on stack."),
    Instruction(opcode=0x6e, name='PUSH15', length_of_operand=0xf, description="Place 15-byte item on stack."),
    Instruction(opcode=0x6f, name='PUSH16', length_of_operand=0x10, description="Place 16-byte item on stack."),
    Instruction(opcode=0x70, name='PUSH17', length_of_operand=0x11, description="Place 17-byte item on stack."),
    Instruction(opcode=0x71, name='PUSH18', length_of_operand=0x12, description="Place 18-byte item on stack."),
    Instruction(opcode=0x72, name='PUSH19', length_of_operand=0x13, description="Place 19-byte item on stack."),
    Instruction(opcode=0x73, name='PUSH20', length_of_operand=0x14, description="Place 20-byte item on stack."),
    Instruction(opcode=0x74, name='PUSH21', length_of_operand=0x15, description="Place 21-byte item on stack."),
    Instruction(opcode=0x75, name='PUSH22', length_of_operand=0x16, description="Place 22-byte item on stack."),
    Instruction(opcode=0x76, name='PUSH23', length_of_operand=0x17, description="Place 23-byte item on stack."),
    Instruction(opcode=0x77, name='PUSH24', length_of_operand=0x18, description="Place 24-byte item on stack."),
    Instruction(opcode=0x78, name='PUSH25', length_of_operand=0x19, description="Place 25-byte item on stack."),
    Instruction(opcode=0x79, name='PUSH26', length_of_operand=0x1a, description="Place 26-byte item on stack."),
    Instruction(opcode=0x7a, name='PUSH27', length_of_operand=0x1b, description="Place 27-byte item on stack."),
    Instruction(opcode=0x7b, name='PUSH28', length_of_operand=0x1c, description="Place 28-byte item on stack."),
    Instruction(opcode=0x7c, name='PUSH29', length_of_operand=0x1d, description="Place 29-byte item on stack."),
    Instruction(opcode=0x7d, name='PUSH30', length_of_operand=0x1e, description="Place 30-byte item on stack."),
    Instruction(opcode=0x7e, name='PUSH31', length_of_operand=0x1f, description="Place 31-byte item on stack."),
    Instruction(opcode=0x7f, name='PUSH32', length_of_operand=0x20,
                description="Place 32-byte (full word) item on stack."),

    # Duplication Operations
    Instruction(opcode=0x80, name='DUP1', description="Duplicate 1st stack item."),
    Instruction(opcode=0x81, name='DUP2', description="Duplicate 2nd stack item."),
    Instruction(opcode=0x82, name='DUP3', description="Duplicate 3rd stack item."),
    Instruction(opcode=0x83, name='DUP4', description="Duplicate 4th stack item."),
    Instruction(opcode=0x84, name='DUP5', description="Duplicate 5th stack item."),
    Instruction(opcode=0x85, name='DUP6', description="Duplicate 6th stack item."),
    Instruction(opcode=0x86, name='DUP7', description="Duplicate 7th stack item."),
    Instruction(opcode=0x87, name='DUP8', description="Duplicate 8th stack item."),
    Instruction(opcode=0x88, name='DUP9', description="Duplicate 9th stack item."),
    Instruction(opcode=0x89, name='DUP10', description="Duplicate 10th stack item."),
    Instruction(opcode=0x8a, name='DUP11', description="Duplicate 11th stack item."),
    Instruction(opcode=0x8b, name='DUP12', description="Duplicate 12th stack item."),
    Instruction(opcode=0x8c, name='DUP13', description="Duplicate 13th stack item."),
    Instruction(opcode=0x8d, name='DUP14', description="Duplicate 14th stack item."),
    Instruction(opcode=0x8e, name='DUP15', description="Duplicate 15th stack item."),
    Instruction(opcode=0x8f, name='DUP16', description="Duplicate 16th stack item."),

    # Exchange Operations
    Instruction(opcode=0x90, name='SWAP1', description="Exchange 1st and 2nd stack items."),
    Instruction(opcode=0x91, name='SWAP2', description="Exchange 1st and 3rd stack items."),
    Instruction(opcode=0x92, name='SWAP3', description="Exchange 1st and 4th stack items."),
    Instruction(opcode=0x93, name='SWAP4', description="Exchange 1st and 5th stack items."),
    Instruction(opcode=0x94, name='SWAP5', description="Exchange 1st and 6th stack items."),
    Instruction(opcode=0x95, name='SWAP6', description="Exchange 1st and 7th stack items."),
    Instruction(opcode=0x96, name='SWAP7', description="Exchange 1st and 8th stack items."),
    Instruction(opcode=0x97, name='SWAP8', description="Exchange 1st and 9th stack items."),
    Instruction(opcode=0x98, name='SWAP9', description="Exchange 1st and 10th stack items."),
    Instruction(opcode=0x99, name='SWAP10', description="Exchange 1st and 11th stack items."),
    Instruction(opcode=0x9a, name='SWAP11', description="Exchange 1st and 12th stack items."),
    Instruction(opcode=0x9b, name='SWAP12', description="Exchange 1st and 13th stack items."),
    Instruction(opcode=0x9c, name='SWAP13', description="Exchange 1st and 14th stack items."),
    Instruction(opcode=0x9d, name='SWAP14', description="Exchange 1st and 15th stack items."),
    Instruction(opcode=0x9e, name='SWAP15', description="Exchange 1st and 16th stack items."),
    Instruction(opcode=0x9f, name='SWAP16', description="Exchange 1st and 17th stack items."),

    # Logging Operations
    Instruction(opcode=0xa0, name='LOG0', length_of_operand=0x0, description="Append log record with no topics."),
    Instruction(opcode=0xa1, name='LOG1', length_of_operand=0x1, description="Append log record with one topic."),
    Instruction(opcode=0xa2, name='LOG2', length_of_operand=0x2, description="Append log record with two topics."),
    Instruction(opcode=0xa3, name='LOG3', length_of_operand=0x3, description="Append log record with three topics."),
    Instruction(opcode=0xa4, name='LOG4', length_of_operand=0x4, description="Append log record with four topics."),

    # System Operations
    Instruction(opcode=0xf0, name='CREATE', description="Create a new account with associated code."),
    Instruction(opcode=0xf1, name='CALL', description="Message-call into an account."),
    Instruction(opcode=0xf2, name='CALLCODE',
                description="Message-call into this account with alternative account’s code."),
    Instruction(opcode=0xf3, name='RETURN', description="Halt execution returning output data."),

    # Newer opcode
    Instruction(opcode=0xfd, name='REVERT', description='throw an error'),

    # Halt Execution, Mark for deletion
    Instruction(opcode=0xff, name='SUICIDE', description="Halt execution and register account for later deletion."), ]

OPCODE_MARKS_BASICBLOCK_END = ['JUMP', 'JUMPI', 'STOP', 'RETURN']


class EVMCode(object):
    def __init__(self, debug=False):
        self.dis = EVMDisAssembler(debug=debug)
        self.first = None
        self.last = None
        self.duration = None

        self.instruction_at = {}  # address:instruction
        self.name_for_address = {}  # address:name
        self.xrefs = {}  # address:set(ref istruction,ref instruction)

    def assemble(self, instructions):
        return '0x' + ''.join(inst.serialize() for inst in instructions)

    def _iter(self, first=None):
        current = first or self.first
        yield current
        while current.next:
            current = current.next
            yield current

    def disassemble(self, bytecode=None):
        """
        for inst in self.dis.disassemble(bytecode):
            # return them as we process them
            yield inst
        """
        if bytecode:
            t_start = time.time()
            disasm = list(self.dis.disassemble(bytecode))
            self.first = disasm[0]
            self.last = disasm[-1]
            self._update_address_space(self.first)
            self._update_xrefs()
            self.duration = time.time() - t_start

        # current = self.first
        return self._iter()

    def _update_address_space(self, first):
        for instruction in self._iter(first):
            self.instruction_at[instruction.address] = instruction

    def _update_xrefs(self):
        # find all JUMP, JUMPI's
        for loc, instruction in ((l, i) for l, i in self.instruction_at.items() if i.name in ("JUMP", "JUMPI")):
            if instruction.previous and instruction.previous.name.startswith("PUSH"):
                instruction.jumpto = int(instruction.previous.operand, 16)
                target_instruction = self.instruction_at.get(instruction.jumpto)
                if target_instruction and target_instruction.name == "JUMPDEST":
                    # valid address, valid target
                    self.xrefs.setdefault(instruction.jumpto, set([]))
                    self.xrefs[instruction.jumpto] = instruction
                    target_instruction.xrefs.add(instruction)

    def basicblocks(self, disasm):
        # listify it in order to resolve xrefs, jumps
        current_basicblock = BasicBlock(address=0, name="init")

        for i, nm in enumerate(disasm):
            if nm.name == "JUMPDEST":
                # jumpdest belongs tto the new basicblock (marks the start)
                yield current_basicblock
                current_basicblock = BasicBlock(address=nm.address, name="loc_%s"% hex(nm.address))

            # add to current basicblock
            current_basicblock.instructions.append(nm)
            nm.basicblock = current_basicblock
        # yield the last basicblock
        yield current_basicblock


class EVMDisAssembler(object):
    OPCODE_TABLE = dict((obj.opcode, obj) for obj in OPCODES)

    def __init__(self, debug=False):
        self.errors = []
        self.debug = debug

    def disassemble(self, bytecode):
        """ Disassemble evm bytecode to a Instruction objects """

        def iterbytes(bytecode):
            iter_bytecode = (b for b in bytecode if b in '1234567890abcdefABCDEFx')  # 0x will bail below.
            for b in zip(iter_bytecode, iter_bytecode):
                b = ''.join(b)
                try:
                    yield int(b, 16)
                except ValueError:
                    logger.warning("skipping invalid byte: %s" % repr(b))

        pc = 0
        previous = None
        iter_bytecode = iterbytes(bytecode)
        # disassemble
        seen_stop = False
        for opcode in iter_bytecode:
            logger.debug(opcode)
            try:
                instruction = self.OPCODE_TABLE[opcode].consume(iter_bytecode)
            except KeyError as ke:
                instruction = Instruction(opcode=opcode,
                                          name="UNKNOWN_%s" % hex(opcode),
                                          description="Invalid opcode")

                if not seen_stop:
                    msg = "error: byte at address %d (%s) is not a valid operator" % (pc, hex(opcode))
                    if self.debug:
                        logger.exception(msg)
                    self.errors.append("%s; %r" % (msg, ke))
            if instruction.name == 'STOP' and not seen_stop:
                seen_stop = True
            instruction.address = pc
            pc += instruction.size()
            # doubly link
            instruction.previous = previous
            if previous:
                previous.next = instruction

            # current is previous
            previous = instruction
            yield instruction

    def assemble(self, instructions):
        """ Assemble a list of Instruction() objects to evm bytecode"""
        for instruction in instructions:
            yield instruction.serialize()


class EVMDasmPrinter:
    """ utility class for different output formats
    """

    @staticmethod
    def listing(disasm):
        for i, nm in enumerate(disasm):
            print("%s %s" % (nm.name, nm.operand))

    @staticmethod
    def detailed(disasm, resolve_funcsig=False):
        print("%-3s %-4s %-3s  %-15s %-36s %-30s %s" % (
            "Inst", "addr", " hex ", "mnemonic", "operand", "xrefs", "description"))
        print("-" * 150)
        # listify it in order to resolve xrefs, jumps
        for i, nm in enumerate(disasm):
            if nm.name == "JUMPDEST":
                print(":loc_%s" % hex(nm.address))
            try:
                operand = ','.join('%s@%s' % (x.name, hex(x.address)) for x in nm.xrefs) if nm.xrefs else ''
                print("%4d [%3d 0x%0.3x] %-15s %-36s %-30s # %s" % (i, nm.address, nm.address, nm.name,
                                                                    nm.describe_operand(resolve_funcsig=resolve_funcsig),
                                                                    operand,
                                                                    nm.description))
            except Exception as e:
                print(e)
            if nm.name in OPCODE_MARKS_BASICBLOCK_END:
                print("")

    @staticmethod
    def basicblocks_detailed(basicblocks, resolve_funcsig=False):
        print("%-3s %-4s %-3s  %-15s %-36s %-30s %s" % (
            "Inst", "addr", " hex ", "mnemonic", "operand", "xrefs", "description"))
        print("-" * 150)

        i = 0
        for bb in basicblocks:
            # every basicblock
            print(":loc_%s" % hex(bb.address))
            for nm in bb.instructions:
                try:
                    operand = ','.join('%s@%s' % (x.name, hex(x.address)) for x in nm.xrefs) if nm.xrefs else ''
                    print("%4d [%3d 0x%0.3x] %-15s %-36s %-30s # %s" % (i, nm.address, nm.address, nm.name,
                                                                        nm.describe_operand(
                                                                            resolve_funcsig=resolve_funcsig),
                                                                        operand,
                                                                        nm.description))
                except Exception as e:
                    print(e)
                i += 1
            if nm.name in OPCODE_MARKS_BASICBLOCK_END:
                print("")


def main():
    logging.basicConfig(format="%(levelname)-7s - %(message)s")
    from optparse import OptionParser
    usage = """usage: %prog [options]

       example: %prog [-L -F -v] <file_or_bytecode>
                %prog [-L -F -v] # read from stdin
                %prog [-L -F -a <address>] # fetch contract code from infura.io
    """
    parser = OptionParser(usage=usage)
    loglevels = ['CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'WARN', 'INFO', 'DEBUG', 'NOTSET']
    parser.add_option("-v", "--verbosity", default="critical",
                      help="available loglevels: %s [default: %%default]" % ','.join(l.lower() for l in loglevels))
    parser.add_option("-L", "--listing", action="store_true", dest="listing",
                      help="disables table mode, outputs assembly only")
    parser.add_option("-F", "--no-online-lookup", action="store_false", default=True, dest="function_signature_lookup",
                      help="disable online function signature lookup")
    parser.add_option("-a", "--address",
                      help="fetch contract bytecode from address")

    # parse args
    (options, args) = parser.parse_args()

    if options.verbosity.upper() in loglevels:
        options.verbosity = getattr(logging, options.verbosity.upper())
        logger.setLevel(options.verbosity)
    else:
        parser.error("invalid verbosity selected. please check --help")

    if options.function_signature_lookup and not ethereum_input_decoder:
        logger.warning("ethereum_input_decoder package not installed. function signature lookup not available.(pip install ethereum-input-decoder)")

    # get bytecode from stdin, or arg:file or arg:bytcode
    if options.address:
        api = EthJsonRpc("https://mainnet.infura.io/")
        evmcode = api.call(method="eth_getCode", params=[options.address, "latest"])["result"]
    elif not args:
        evmcode = sys.stdin.read()
    else:
        if os.path.isfile(args[0]):
            evmcode = open(args[0], 'r').read()
        else:
            evmcode = args[0]

    # init analyzer
    evm_dasm = EVMCode(debug=options.verbosity)
    logger.debug(EVMDisAssembler.OPCODE_TABLE)

    # print dissasembly
    if options.listing:
        EVMDasmPrinter.listing(evm_dasm.disassemble(evmcode))
    else:
        EVMDasmPrinter.basicblocks_detailed(evm_dasm.basicblocks(evm_dasm.disassemble(evmcode)), resolve_funcsig=options.function_signature_lookup)
        #EVMDasmPrinter.detailed(evm_dasm.disassemble(evmcode), resolve_funcsig=options.function_signature_lookup)

    logger.info("finished in %0.3f seconds." % evm_dasm.duration)
    # post a notification that disassembly might be incorrect due to errors
    if evm_dasm.dis.errors:
        logger.warning("disassembly finished with %d errors" % len(evm_dasm.dis.errors))
        if options.verbosity >= 30:
            logger.warning("use -v INFO to see the errors")
        else:
            for e in evm_dasm.dis.errors:
                logger.info(e)

    # quick check
    logger.debug("assemble(disassemble(evmcode))==",
                 evmcode.strip() == ''.join(evm_dasm.assemble(evm_dasm.disassemble())))
    sys.exit(len(evm_dasm.dis.errors))


if __name__ == "__main__":
    main()
