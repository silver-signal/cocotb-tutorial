# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

import os
import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.runner import get_runner
from cocotb.triggers import RisingEdge
from cocotb.types import LogicArray


@cocotb.test()
async def dff_simple_test(dut):
    """Test that d propagates to q"""

    # The initial state of a DFF is undefined, so it should be an X value.
    initial = LogicArray("X")
    assert LogicArray(dut.q.value) == initial

    # Set initial input value to prevent it from floating
    dut.d.value = 0

    clock = Clock(dut.clk, 10, units="us")  # Create a 10us period clock on port clk
    # Start the clock. Start it low to avoid issues on the first RisingEdge
    cocotb.start_soon(clock.start(start_high=False))

    # Synchronize with the clock. This will regisiter the initial `d` value
    await RisingEdge(dut.clk)
    expected_val = 0  # Matches initial input value
    for i in range(10):
        val = random.randint(0, 1)
        dut.d.value = val  # Assign the random value val to the input port d
        await RisingEdge(dut.clk)
        assert dut.q.value == expected_val, f"output q was incorrect on the {i}th cycle"
        expected_val = val  # Save random value for next RisingEdge

    # Check the final input on the next clock
    await RisingEdge(dut.clk)
    assert dut.q.value == expected_val, "output q was incorrect on the last cycle"


def test_simple_dff_runner():
    sim = "icarus"
    # Option to generate waveforms for the user to see in a wave viewer. These aren't necessary when
    # only running tests, so the default is OFF. These are useful for debugging or understanding
    # a design.
    waves_val = os.getenv("WAVES", "0")
    waves = False
    if waves_val == "1":
        waves = True

    # We need a reproducible way to point to the project path. We can't use the directory the user is operating
    # from because they could be in any other directory in the filesystem.
    proj_path = Path(__file__).resolve().parent

    verilog_sources = [proj_path / "dff.sv"]

    runner = get_runner(sim)
    runner.build(
        verilog_sources=verilog_sources,
        hdl_toplevel="dff",
        always=True,
        waves=waves,
    )

    runner.test(hdl_toplevel="dff", test_module="test_dff,", waves=waves)


if __name__ == "__main__":
    test_simple_dff_runner()
