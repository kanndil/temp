#!/usr/bin/env python3

"""
Cocotb testbench for SimpleAlu module
Tests all ALU operations with comprehensive coverage
"""

import cocotb
from cocotb.triggers import Timer
from cocotb.binary import BinaryValue
import random
import pytest

# ALU operation codes
ALU_ADD  = 0x0
ALU_SUB  = 0x1
ALU_AND  = 0x2
ALU_OR   = 0x3
ALU_XOR  = 0x4
ALU_SLL  = 0x5
ALU_SRL  = 0x6
ALU_SRA  = 0x7
ALU_SLT  = 0x8
ALU_SLTU = 0x9
ALU_NOR  = 0xA
ALU_NAND = 0xB

class AluTester:
    """Helper class for ALU testing"""
    
    def __init__(self, dut):
        self.dut = dut
        self.data_width = 32
        self.max_val = (1 << self.data_width) - 1
        
    async def apply_inputs(self, a, b, op):
        """Apply inputs to ALU and wait for propagation"""
        self.dut.a_i.value = a
        self.dut.b_i.value = b
        self.dut.op_i.value = op
        await Timer(1, units='ns')  # Allow combinational logic to settle
        
    def to_signed(self, val):
        """Convert unsigned to signed representation"""
        if val >= (1 << (self.data_width - 1)):
            return val - (1 << self.data_width)
        return val
        
    def to_unsigned(self, val):
        """Convert signed to unsigned representation"""
        if val < 0:
            return val + (1 << self.data_width)
        return val & self.max_val
        
    async def check_add(self, a, b):
        """Test addition operation"""
        await self.apply_inputs(a, b, ALU_ADD)
        
        expected_result = (a + b) & self.max_val
        expected_carry = 1 if (a + b) > self.max_val else 0
        expected_zero = 1 if expected_result == 0 else 0
        
        # Check overflow for signed addition
        a_signed = self.to_signed(a)
        b_signed = self.to_signed(b)
        result_signed = self.to_signed(expected_result)
        expected_overflow = 0
        if (a_signed >= 0 and b_signed >= 0 and result_signed < 0) or \
           (a_signed < 0 and b_signed < 0 and result_signed >= 0):
            expected_overflow = 1
            
        assert self.dut.result_o.value == expected_result, \
            f"ADD: Expected result {expected_result:08x}, got {self.dut.result_o.value:08x}"
        assert self.dut.carry_o.value == expected_carry, \
            f"ADD: Expected carry {expected_carry}, got {self.dut.carry_o.value}"
        assert self.dut.zero_o.value == expected_zero, \
            f"ADD: Expected zero {expected_zero}, got {self.dut.zero_o.value}"
        assert self.dut.overflow_o.value == expected_overflow, \
            f"ADD: Expected overflow {expected_overflow}, got {self.dut.overflow_o.value}"
            
    async def check_sub(self, a, b):
        """Test subtraction operation"""
        await self.apply_inputs(a, b, ALU_SUB)
        
        expected_result = (a - b) & self.max_val
        expected_carry = 1 if a < b else 0
        expected_zero = 1 if expected_result == 0 else 0
        
        # Check overflow for signed subtraction
        a_signed = self.to_signed(a)
        b_signed = self.to_signed(b)
        result_signed = self.to_signed(expected_result)
        expected_overflow = 0
        if (a_signed >= 0 and b_signed < 0 and result_signed < 0) or \
           (a_signed < 0 and b_signed >= 0 and result_signed >= 0):
            expected_overflow = 1
            
        assert self.dut.result_o.value == expected_result, \
            f"SUB: Expected result {expected_result:08x}, got {self.dut.result_o.value:08x}"
        assert self.dut.carry_o.value == expected_carry, \
            f"SUB: Expected carry {expected_carry}, got {self.dut.carry_o.value}"
        assert self.dut.zero_o.value == expected_zero, \
            f"SUB: Expected zero {expected_zero}, got {self.dut.zero_o.value}"
        assert self.dut.overflow_o.value == expected_overflow, \
            f"SUB: Expected overflow {expected_overflow}, got {self.dut.overflow_o.value}"
            
    async def check_logical(self, a, b, op, op_name):
        """Test logical operations"""
        await self.apply_inputs(a, b, op)
        
        if op == ALU_AND:
            expected_result = a & b
        elif op == ALU_OR:
            expected_result = a | b
        elif op == ALU_XOR:
            expected_result = a ^ b
        elif op == ALU_NOR:
            expected_result = (~(a | b)) & self.max_val
        elif op == ALU_NAND:
            expected_result = (~(a & b)) & self.max_val
        else:
            raise ValueError(f"Unknown logical operation: {op}")
            
        expected_zero = 1 if expected_result == 0 else 0
        
        assert self.dut.result_o.value == expected_result, \
            f"{op_name}: Expected result {expected_result:08x}, got {self.dut.result_o.value:08x}"
        assert self.dut.zero_o.value == expected_zero, \
            f"{op_name}: Expected zero {expected_zero}, got {self.dut.zero_o.value}"
        assert self.dut.carry_o.value == 0, \
            f"{op_name}: Expected carry 0, got {self.dut.carry_o.value}"
        assert self.dut.overflow_o.value == 0, \
            f"{op_name}: Expected overflow 0, got {self.dut.overflow_o.value}"
            
    async def check_shift(self, a, b, op, op_name):
        """Test shift operations"""
        await self.apply_inputs(a, b, op)
        
        shift_amount = b & 0x1F  # Use lower 5 bits
        
        if op == ALU_SLL:
            expected_result = (a << shift_amount) & self.max_val
        elif op == ALU_SRL:
            expected_result = a >> shift_amount
        elif op == ALU_SRA:
            # Arithmetic right shift
            a_signed = self.to_signed(a)
            expected_result = self.to_unsigned(a_signed >> shift_amount)
        else:
            raise ValueError(f"Unknown shift operation: {op}")
            
        expected_zero = 1 if expected_result == 0 else 0
        
        assert self.dut.result_o.value == expected_result, \
            f"{op_name}: Expected result {expected_result:08x}, got {self.dut.result_o.value:08x}"
        assert self.dut.zero_o.value == expected_zero, \
            f"{op_name}: Expected zero {expected_zero}, got {self.dut.zero_o.value}"
            
    async def check_compare(self, a, b, op, op_name):
        """Test comparison operations"""
        await self.apply_inputs(a, b, op)
        
        if op == ALU_SLT:
            # Signed comparison
            a_signed = self.to_signed(a)
            b_signed = self.to_signed(b)
            expected_result = 1 if a_signed < b_signed else 0
        elif op == ALU_SLTU:
            # Unsigned comparison
            expected_result = 1 if a < b else 0
        else:
            raise ValueError(f"Unknown comparison operation: {op}")
            
        expected_zero = 1 if expected_result == 0 else 0
        
        assert self.dut.result_o.value == expected_result, \
            f"{op_name}: Expected result {expected_result}, got {self.dut.result_o.value}"
        assert self.dut.zero_o.value == expected_zero, \
            f"{op_name}: Expected zero {expected_zero}, got {self.dut.zero_o.value}"


@cocotb.test()
async def test_basic_operations(dut):
    """Test basic ALU operations with known values"""
    tester = AluTester(dut)
    
    # Test addition
    await tester.check_add(0x12345678, 0x87654321)
    await tester.check_add(0xFFFFFFFF, 0x00000001)  # Overflow case
    await tester.check_add(0x7FFFFFFF, 0x00000001)  # Signed overflow
    
    # Test subtraction
    await tester.check_sub(0x87654321, 0x12345678)
    await tester.check_sub(0x00000001, 0xFFFFFFFF)  # Underflow case
    await tester.check_sub(0x80000000, 0x00000001)  # Signed overflow
    
    # Test logical operations
    await tester.check_logical(0xAAAAAAAA, 0x55555555, ALU_AND, "AND")
    await tester.check_logical(0xAAAAAAAA, 0x55555555, ALU_OR, "OR")
    await tester.check_logical(0xAAAAAAAA, 0x55555555, ALU_XOR, "XOR")
    await tester.check_logical(0xAAAAAAAA, 0x55555555, ALU_NOR, "NOR")
    await tester.check_logical(0xAAAAAAAA, 0x55555555, ALU_NAND, "NAND")
    
    # Test shift operations
    await tester.check_shift(0x12345678, 4, ALU_SLL, "SLL")
    await tester.check_shift(0x12345678, 4, ALU_SRL, "SRL")
    await tester.check_shift(0x87654321, 4, ALU_SRA, "SRA")  # Negative number
    
    # Test comparison operations
    await tester.check_compare(0x12345678, 0x87654321, ALU_SLT, "SLT")
    await tester.check_compare(0x87654321, 0x12345678, ALU_SLT, "SLT")
    await tester.check_compare(0x12345678, 0x87654321, ALU_SLTU, "SLTU")
    await tester.check_compare(0x87654321, 0x12345678, ALU_SLTU, "SLTU")


@cocotb.test()
async def test_edge_cases(dut):
    """Test edge cases and corner conditions"""
    tester = AluTester(dut)
    
    # Test with zero
    await tester.check_add(0x00000000, 0x00000000)
    await tester.check_sub(0x00000000, 0x00000000)
    await tester.check_logical(0x00000000, 0xFFFFFFFF, ALU_AND, "AND")
    await tester.check_logical(0x00000000, 0x00000000, ALU_OR, "OR")
    
    # Test with maximum values
    await tester.check_add(0xFFFFFFFF, 0xFFFFFFFF)
    await tester.check_sub(0xFFFFFFFF, 0xFFFFFFFF)
    
    # Test shift by zero and maximum
    await tester.check_shift(0x12345678, 0, ALU_SLL, "SLL")
    await tester.check_shift(0x12345678, 31, ALU_SRL, "SRL")
    await tester.check_shift(0x80000000, 31, ALU_SRA, "SRA")


@cocotb.test()
async def test_random_operations(dut):
    """Test with random values for comprehensive coverage"""
    tester = AluTester(dut)
    
    # Generate random test cases
    for _ in range(100):
        a = random.randint(0, tester.max_val)
        b = random.randint(0, tester.max_val)
        
        # Test a random operation
        op = random.choice([ALU_ADD, ALU_SUB, ALU_AND, ALU_OR, ALU_XOR, 
                           ALU_SLL, ALU_SRL, ALU_SRA, ALU_SLT, ALU_SLTU])
        
        if op in [ALU_ADD]:
            await tester.check_add(a, b)
        elif op in [ALU_SUB]:
            await tester.check_sub(a, b)
        elif op in [ALU_AND, ALU_OR, ALU_XOR, ALU_NOR, ALU_NAND]:
            op_names = {ALU_AND: "AND", ALU_OR: "OR", ALU_XOR: "XOR", 
                       ALU_NOR: "NOR", ALU_NAND: "NAND"}
            await tester.check_logical(a, b, op, op_names[op])
        elif op in [ALU_SLL, ALU_SRL, ALU_SRA]:
            op_names = {ALU_SLL: "SLL", ALU_SRL: "SRL", ALU_SRA: "SRA"}
            await tester.check_shift(a, b, op, op_names[op])
        elif op in [ALU_SLT, ALU_SLTU]:
            op_names = {ALU_SLT: "SLT", ALU_SLTU: "SLTU"}
            await tester.check_compare(a, b, op, op_names[op])


@cocotb.test()
async def test_invalid_operations(dut):
    """Test behavior with invalid operation codes"""
    tester = AluTester(dut)
    
    # Test with invalid operation codes
    for invalid_op in [0xC, 0xD, 0xE, 0xF]:
        await tester.apply_inputs(0x12345678, 0x87654321, invalid_op)
        
        # Should return zero for invalid operations
        assert dut.result_o.value == 0, \
            f"Invalid op {invalid_op:x}: Expected result 0, got {dut.result_o.value:08x}"
        assert dut.zero_o.value == 1, \
            f"Invalid op {invalid_op:x}: Expected zero flag 1, got {dut.zero_o.value}"