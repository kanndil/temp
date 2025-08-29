# Makefile for SimpleAlu project

# Project configuration
PROJECT_NAME = SimpleAlu
RTL_DIR = rtl
TB_DIR = tb
SYN_DIR = syn
DOCS_DIR = docs

# Tool configuration
VERILATOR = verilator
YOSYS = yosys
COCOTB_SIMULATOR = verilator

# RTL files
RTL_FILES = $(RTL_DIR)/$(PROJECT_NAME).sv

# Testbench configuration
TOPLEVEL = $(PROJECT_NAME)
MODULE = test_simple_alu
TESTBENCH = $(TB_DIR)/$(MODULE).py

# Default target
.PHONY: all
all: lint verify synth

# Lint RTL files
.PHONY: lint
lint:
	@echo "=== Linting RTL files ==="
	$(VERILATOR) --lint-only --Wno-EOFNEWLINE $(RTL_FILES)
	@echo "Linting completed successfully"

# Run verification
.PHONY: verify
verify: lint
	@echo "=== Running verification ==="
	cd $(TB_DIR) && \
	TOPLEVEL=$(TOPLEVEL) MODULE=$(MODULE) \
	COCOTB_SIMULATOR=$(COCOTB_SIMULATOR) \
	make -f /usr/local/lib/python3.12/site-packages/cocotb/share/makefiles/Makefile.sim VERILOG_SOURCES=../$(RTL_FILES)
	@echo "Verification completed successfully"

# Synthesize design
.PHONY: synth
synth: lint
	@echo "=== Synthesizing design ==="
	mkdir -p $(SYN_DIR)
	cd $(SYN_DIR) && \
	$(YOSYS) -p "read_verilog -sv ../$(RTL_FILES); \
	             synth -top $(PROJECT_NAME); \
	             abc; \
	             write_verilog $(PROJECT_NAME)_synth.v; \
	             stat; \
	             show -format svg -prefix $(PROJECT_NAME)"
	@echo "Synthesis completed successfully"

# Generate documentation
.PHONY: docs
docs:
	@echo "=== Generating documentation ==="
	mkdir -p $(DOCS_DIR)
	@echo "# $(PROJECT_NAME) Documentation" > $(DOCS_DIR)/README.md
	@echo "" >> $(DOCS_DIR)/README.md
	@echo "## Module Interface" >> $(DOCS_DIR)/README.md
	@echo "" >> $(DOCS_DIR)/README.md
	@echo "\`\`\`systemverilog" >> $(DOCS_DIR)/README.md
	@head -20 $(RTL_FILES) | tail -15 >> $(DOCS_DIR)/README.md
	@echo "\`\`\`" >> $(DOCS_DIR)/README.md
	@echo "Documentation generated in $(DOCS_DIR)/"

# Clean generated files
.PHONY: clean
clean:
	@echo "=== Cleaning generated files ==="
	rm -rf $(SYN_DIR)/*
	rm -rf $(TB_DIR)/__pycache__
	rm -rf $(TB_DIR)/*.vcd
	rm -rf $(TB_DIR)/sim_build
	rm -rf $(TB_DIR)/results.xml
	rm -rf $(DOCS_DIR)/*
	@echo "Clean completed"

# Show help
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all     - Run lint, verify, and synth"
	@echo "  lint    - Lint RTL files with Verilator"
	@echo "  verify  - Run cocotb verification"
	@echo "  synth   - Synthesize design with Yosys"
	@echo "  docs    - Generate documentation"
	@echo "  clean   - Clean generated files"
	@echo "  help    - Show this help message"