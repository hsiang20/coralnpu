# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Makefile for CoralNPU UVM Testbench (Using DSim simulator)

# Check if CORALNPU_MPACT is set. If not, exit with an error.
# ifndef CORALNPU_MPACT
#     $(error CORALNPU_MPACT is not set. Please define it, e.g., export CORALNPU_MPACT=$(abspath ../../../coralnpu-mpact))
# endif

# Workspace root (two levels up from tests/uvm/)
WORKSPACE_ROOT := $(shell cd ../.. && pwd)

# Generated RTL path
BAZEL_BIN_DIR = $(shell cd $(WORKSPACE_ROOT) && bazel info bazel-bin)
GENERATED_RTL_NAME = RvvCoreMiniVerificationAxi.sv
GENERATED_RTL_SRC = $(BAZEL_BIN_DIR)/hdl/chisel/src/coralnpu/$(GENERATED_RTL_NAME)

# User Configuration
VCS = dsim
CXX = clang++

# UVM DV Directories
COMMON_DIR = ./common
TB_DIR = ./tb
ENV_DIR = ./env
TESTS_DIR = ./tests
BIN_DIR = ./bin
UTILS_DIR = ./utils

# Simulation Work Directory
SIM_DIR = ./sim_work
LOG_DIR = $(SIM_DIR)/logs
WAVE_DIR = $(SIM_DIR)/waves
MEM_FILE_DIR = $(SIM_DIR)/mem_files
RUN_OPTS_FILE = $(MEM_FILE_DIR)/elf_run_opts.f

# MPACT-Sim Integration Paths
MPACT_BAZEL_BIN_DIR = $(CORALNPU_MPACT)/bazel-bin/sim/cosim
MPACT_COSIM_LIB_NAME = coralnpu_cosim_lib_static

# File List for VCS -f option
FILE_LIST = ./coralnpu_dv.f

# Simulation Settings
DSIM_WORK = dsim_work
DSIM_IMAGE = image
UVM_TESTNAME ?= coralnpu_base_test
TEST_ELF ?= $(BIN_DIR)/coralnpu_v2_program.elf
UVM_VERBOSITY ?= UVM_HIGH
TEST_TIMEOUT_NS ?= 100000
PLUSARGS = +UVM_TESTNAME=$(UVM_TESTNAME) \
           +UVM_VERBOSITY=$(UVM_VERBOSITY) +TEST_TIMEOUT=$(TEST_TIMEOUT_NS) \
           +TEST_ELF=$(TEST_ELF) \
					 +acc+b -waves $(SIM_DIR)/waves/waves.vcd

# Waveform Dumping
DUMP_WAVES = 1
WAVE_FILE = $(WAVE_DIR)/$(UVM_TESTNAME).vcd

# DSim Compilation Options
# Note: UVM_HOME and DSIM_HOME are set in the Docker environment
# UVM_HOME=/root/AltairDSim/2025/uvm/1.2/
# DSIM_HOME=/root/AltairDSim/2025
VCS_COMPILE_OPTS = \
	-sv \
	+define+UVM_NO_DEPRECATED \
	-incdir ${UVM_HOME}/src \
	-timescale 1ns/1ps \
	-sv_lib ${UVM_HOME}/src/dpi/libuvm_dpi.so \
	-uvm default \
	-noopt \
	+acc+b -waves $(SIM_DIR)/waves/waves.vcd

VCS_RUN_OPTS = \
	$(PLUSARGS) \
	-f $(RUN_OPTS_FILE) \
	-sv_lib ${UVM_HOME}/src/dpi/libuvm_dpi.so

# Add define to COMPILE options for waveform dumping
ifeq ($(DUMP_WAVES),1)
VCS_COMPILE_OPTS += +define+DUMP_WAVES
endif

# Targets

.PHONY: all compile run clean dirs help build_mpact_lib gen_mem_files rtl

# Default target, builds and then runs.
all: compile run

# Create necessary directories
dirs:
	@mkdir -p $(SIM_DIR) $(LOG_DIR) $(WAVE_DIR) $(BIN_DIR) $(MEM_FILE_DIR)

# Build the MPACT-Sim library using Bazel with CC=clang
build_mpact_lib:
	@echo "--- Building MPACT-Sim Co-sim Library via Bazel ---"
	cd $(CORALNPU_MPACT) && CC=clang bazel build //sim/cosim:$(MPACT_COSIM_LIB_NAME)

# Generate memory and run option files from the ELF file
gen_mem_files: dirs
	@echo "--- Generating Memory and Run Option Files from ELF ---"
	@rm -f $(MEM_FILE_DIR)/*
	python3 $(UTILS_DIR)/elf_to_mem.py --elf_file $(TEST_ELF) --out_dir $(MEM_FILE_DIR)

# Generate the DUT RTL from Chisel source
rtl:
	@echo "--- Generating DUT RTL from Chisel ---"
	cd $(WORKSPACE_ROOT)
	bazel build //hdl/chisel/src/coralnpu:rvv_core_mini_verification_axi_cc_library_emit_verilog
	@echo "--- Fixing Chisel-generated code for DSim compatibility ---"
	sed -i 's/:\/\/\(.*\)/: \/\/\1/g' $(GENERATED_RTL_SRC)
	@echo "--- Removing duplicate SRAM module definitions ---"
	python3 $(UTILS_DIR)/rename_duplicate_sram_modules.py $(GENERATED_RTL_SRC) $(GENERATED_RTL_SRC).tmp
	mv $(GENERATED_RTL_SRC).tmp $(GENERATED_RTL_SRC)

# Compile the design (removed build_mpact_lib dependency since CORALNPU_MPACT is not set)
compile: $(FILE_LIST) dirs rtl
	@echo "--- Compiling with dsim ---"
	$(VCS) $(VCS_COMPILE_OPTS) -l $(LOG_DIR)/compile.log -work $(DSIM_WORK) -genimage $(DSIM_IMAGE) -f $(FILE_LIST) $(GENERATED_RTL_SRC)
	@echo "--- Compilation Finished ---"

# Run the simulation
run: gen_mem_files
	@echo "--- Running Simulation ---"
	@echo "Test:      $(UVM_TESTNAME)"
	@echo "ELF File:  $(TEST_ELF)"
	@echo "Verbosity: $(UVM_VERBOSITY)"
	@echo "Timeout:   $(TEST_TIMEOUT_NS) ns"
	@echo "Plusargs:  $(PLUSARGS)"
	@echo "Log File:  $(LOG_DIR)/$(UVM_TESTNAME).log"
ifeq ($(DUMP_WAVES),1)
	@echo "Wave File: $(WAVE_FILE)"
endif
	$(VCS) -work $(DSIM_WORK) -image $(DSIM_IMAGE) $(VCS_RUN_OPTS) -l $(LOG_DIR)/$(UVM_TESTNAME).log
	@echo "--- Simulation Finished ---"

# Clean up simulation files
clean:
	@echo "--- Cleaning Simulation Files ---"
	rm -rf $(SIM_DIR) $(DSIM_WORK) $(GENERATED_RTL_SRC).tmp simv* dsim* csrc* *.log* *.key *.vpd *.vcd *.fsdb *.mxd *.db ucli.key DVEfiles/ verdiLog/ novas.* work/
	cd $(WORKSPACE_ROOT)
	bazel clean --expunge
	# @echo "--- Cleaning MPACT-Sim Bazel cache ---"
	# cd $(CORALNPU_MPACT) && bazel clean --expunge

# Help
help:
	@echo "Makefile Targets:"
	@echo "  make all              : Compiles and runs the default test (same as just 'make')."
	@echo "  make compile          : Builds the simulator executable."
	@echo "  make run              : Runs the simulation. Compiles first if the executable is missing or source files have changed."
	@echo "                        :   Override defaults: make run UVM_TESTNAME=<test> TEST_ELF=<path> UVM_VERBOSITY=<level>"
	@echo "  make rtl              : Generates the DUT Verilog from Chisel source"
	@echo "  make build_mpact_lib  : Only builds the MPACT-Sim C++ library"
	@echo "  make gen_mem_files    : Only generates ITCM/DTCM and run opt files"
	@echo "  make clean            : Removes generated simulation and MPACT-Sim files"
	@echo "  make dirs             : Creates simulation directories"
	@echo "  make help             : Shows this help message"
