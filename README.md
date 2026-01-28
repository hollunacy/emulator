# Harvard Architecture Single-Address Instruction Set Emulator

## Project Overview

This project implements a **Harvard architecture CPU emulator** with a **single-address instruction set**, featuring both a **Python GUI emulator** and a **Verilog hardware implementation**.

## Key Features

### 🖥️ Python GUI Emulator (`emulator.py`)
- **Harvard Architecture**: Separate code and data memory spaces
- **Single-Address Instruction Set**: All operations use the accumulator (ACC) as one operand
- **Four Addressing Modes**:
  - Immediate (`#value`)
  - Direct (memory address)
  - Register (`Rx`)
  - Indirect (`[Rx]`)
- **Interactive GUI** with:
  - Assembly code editor with syntax highlighting
  - Real-time CPU state visualization
  - Memory viewers for both code and data
  - Step-by-step and full execution modes
- **Built-in Examples**:
  - Array summation program
  - Array convolution program
- **Full Assembly Support** with labels, comments, and error checking

### 🔧 Verilog Implementation (`cpu.v`)
- **Three-Stage Pipeline**: Fetch, Decode, Execute
- **16-bit Architecture** with:
  - 256-word code memory
  - 256-word data memory
  - 8 general-purpose registers (R1-R8)
  - Special registers: ACC, PC, IR
  - Status flags: Z (Zero), N (Negative)
- **Memory Initialization** from file (`sum_program.mem`)
- **Test Bench** (`sum_test.v`) for verification

## Instruction Set

| Mnemonic | Opcode | Description |
|----------|--------|-------------|
| HALT | 0xF | Stop execution |
| LOAD | 0x1 | Load value to ACC |
| STORE | 0x2 | Store ACC to memory |
| ADD | 0x3 | Add to ACC |
| SUB | 0x4 | Subtract from ACC |
| MUL | 0x5 | Multiply ACC |
| CMP | 0x6 | Compare and set flags |
| JMP | 0x7 | Unconditional jump |
| JZ | 0x8 | Jump if zero |
| JN | 0x9 | Jump if negative |
| INC | 0xA | Increment operand |
| DEC | 0xB | Decrement operand |

## Use Cases

1. **Computer Architecture Education**: Understand Harvard architecture and instruction execution
2. **Assembly Programming**: Learn single-address instruction sets
3. **Hardware/Software Codesign**: Compare Python emulator with Verilog implementation
4. **Algorithm Implementation**: Write and test algorithms in assembly

## Technical Details

- **Instruction Format**: 16-bit `[opcode:4][addr_type:2][operand:10]`
- **Memory Size**: 256 words each for code and data
- **Data Representation**: 16-bit signed integers
- **Addressing Modes**: Immediate, Direct, Register, Indirect
