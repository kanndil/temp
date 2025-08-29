# Temp Project

A temporary repository for ASIC design experiments and prototyping.

## Overview

This repository serves as a sandbox environment for developing and testing digital ASIC designs using open-source EDA tools. It provides a structured workspace for RTL development, verification, synthesis, and physical implementation.

## Project Structure

```
temp/
├── README.md           # This file
├── rtl/               # RTL source files
├── tb/                # Testbenches and verification
├── syn/               # Synthesis scripts and results
├── pnr/               # Place and route files
├── docs/              # Documentation
└── scripts/           # Build and automation scripts
```

## Features

- **RTL Development**: SystemVerilog/Verilog HDL design files
- **Verification**: Cocotb/PyUVM based testbenches
- **Synthesis**: Yosys-based synthesis flow
- **Physical Design**: OpenLane integration for PnR
- **Documentation**: Comprehensive design documentation

## Prerequisites

- Python 3.8+
- Yosys synthesis suite
- OpenLane 2 (LibreLane)
- Cocotb for verification
- Verilator for simulation and linting

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/kanndil/temp.git
   cd temp
   ```

2. **Set up environment**:
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Source OpenLane environment
   source $OPENLANE_ROOT/env.sh
   ```

3. **Run basic checks**:
   ```bash
   # Lint RTL files
   make lint
   
   # Run verification
   make verify
   
   # Synthesize design
   make synth
   ```

## Available IP Cores

This project has access to a comprehensive library of pre-verified IP cores including:

- **Communication**: UART, SPI, I2C, USB CDC
- **Memory**: SRAM controllers, DFFRAM variants
- **Security**: AES, SHA256 encryption cores
- **Peripherals**: GPIO, PWM, Timers, Watchdog
- **Processing**: RISC-V core (EF_R2RVC02)
- **Analog**: Oscillators, Comparators

## Design Guidelines

- Follow SystemVerilog-2017 synthesizable subset
- Use single clock domain unless explicitly required
- Implement proper reset synchronization
- Apply power optimization techniques
- Ensure lint-clean code with Verilator
- Maintain comprehensive documentation

## Verification Strategy

- Cocotb/PyUVM based testbenches
- Functional coverage collection
- Constrained random testing
- Self-checking test environments
- Gate-level simulation validation

## Synthesis & Implementation

- **Synthesis**: Yosys with technology mapping
- **Physical Design**: OpenLane automated flow
- **Timing**: Static timing analysis
- **Power**: Power estimation and optimization
- **DRC/LVS**: Physical verification

## Contributing

1. Create feature branch from main
2. Follow coding guidelines
3. Add comprehensive tests
4. Update documentation
5. Submit pull request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Contact

For questions or support, please open an issue in this repository.

---

**Note**: This is a temporary/experimental repository. For production designs, follow established design review and verification processes.