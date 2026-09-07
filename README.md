# CAN-Bus-Monitor-Fault-Detector
• Designed a Verilog-based CAN 2.0A frame monitor supporting 11-bit identifier, DLC and payload decoding. • Implemented CAN bit-stuffing detection/removal and CRC-15 based frame integrity checking. • Developed an FSM-based RTL testbench to verify valid frame decoding and detect CRC, stuffing and format errors.
# Automotive CAN Bus Monitor & Fault Detector

**Verilog HDL | Classic CAN 2.0A | FPGA-oriented RTL simulation**

## Overview

This project implements a lightweight, simulation-oriented **Classic CAN 2.0A standard-frame monitor** in Verilog HDL. The design receives an already-sampled CAN RX bit stream, removes CAN bit-stuffing, decodes the 11-bit identifier, DLC and payload, calculates/checks the CAN CRC-15, and reports basic frame errors.

The project is intentionally scoped as an **RTL/protocol monitor**, not a complete production CAN controller. Physical-layer functions such as CAN_H/CAN_L differential signaling, analog thresholds, transceiver behavior, bit-rate synchronization and actual bus arbitration are outside the scope of this simulation.

## Why this project

CAN is a fundamental communication bus in automotive electronics. An FPGA/RTL implementation is a useful exercise in finite-state-machine design, serial protocol decoding, error detection, timing-aware sampling and hardware verification.

## Features

- Standard CAN 2.0A data frame support
- 11-bit identifier decoding
- DLC decoding
- Up to 8-byte payload storage
- CAN bit-stuff removal/checking
- CAN CRC-15 generation/checking
- CRC delimiter / ACK delimiter / EOF format checks
- Frame-valid indication
- Basic CRC, stuff and format error flags
- Self-contained Verilog testbench
- Python reference model for generating the known test frame

## Block diagram

```text
                 already-sampled CAN RX bitstream
                              |
                              v
                     +----------------+
                     | CAN RX Monitor |
                     |                |
                     | SOF detection  |
                     | Bit destuffing |
                     | Frame parser   |
                     | CRC-15 checker |
                     | Format checks  |
                     +-------+--------+
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
       Frame ID            DLC/Data          Error flags
       11 bits              64 bits       CRC/STUFF/FORMAT
```

## CAN frame used in verification

The testbench uses this Classic CAN 2.0A data frame:

| Field | Value |
|---|---|
| Identifier | `0x123` |
| RTR | `0` |
| IDE | `0` |
| r0 | `0` |
| DLC | `4` |
| Data | `DE AD BE EF` |
| CRC-15 | `0x4E6B` |
| Stuff bits | `2` |

The standard CAN frame uses an 11-bit identifier, a 4-bit DLC, 0–8 data bytes and a 15-bit CRC. Bit stuffing is applied from SOF through the CRC sequence; after five consecutive equal bits, a complementary bit is inserted.

## Repository structure

```text
.
├── README.md
├── src/
│   └── can_monitor.v
├── tb/
│   └── tb_can_monitor.v
├── results/
│   ├── expected_results.txt
│   └── waveform_notes.txt
└── can_reference_model.py
```

## Simulation

### Option 1 — Icarus Verilog

```bash
iverilog -g2012 -o can_sim src/can_monitor.v tb/tb_can_monitor.v
vvp can_sim
```

### Option 2 — Vivado Simulator

1. Create a new RTL project.
2. Add `src/can_monitor.v` as a design source.
3. Add `tb/tb_can_monitor.v` as a simulation source.
4. Set `tb_can_monitor` as the simulation top.
5. Run behavioral simulation.
6. Observe `can_rx`, `bit_tick`, `frame_valid`, `frame_id`, `frame_dlc`, `frame_data`, `crc_error`, `stuff_error` and `format_error`.

## Expected output

```text
---------------------------------------------
CAN MONITOR SIMULATION RESULT
Frame valid : 1
Frame ID    : 0x123
DLC         : 4
DATA        : 0x00000000deadbeef
CRC error   : 0
Stuff error : 0
Format error: 0
---------------------------------------------
```

The exact capitalization of hexadecimal digits can vary between simulators.

## Verification approach

The verification flow is:

1. Construct a known CAN 2.0A frame.
2. Calculate the CRC-15 using the CAN polynomial.
3. Insert CAN stuff bits after five consecutive equal bits.
4. Append CRC delimiter, ACK slot, ACK delimiter and EOF.
5. Drive the resulting wire-level bitstream into `can_rx`.
6. Confirm that the RTL removes stuff bits and reconstructs the original frame.
7. Confirm that the calculated CRC matches the received CRC.
8. Confirm that no format/stuff/CRC error is reported for the valid frame.

## Engineering concepts demonstrated

- FSM-based serial protocol decoding
- Synchronous digital design
- Bit-level parsing
- Shift registers
- CRC implementation using polynomial division
- Bit-stuffing detection/removal
- Hardware-oriented verification
- Error detection and fault reporting

## Limitations / future work

This is a learning/portfolio implementation rather than a production CAN controller. Future work could add:

- CAN 2.0B extended 29-bit frames
- Remote and error frames
- Complete CAN transmit path
- Bit timing and synchronization logic
- Arbitration logic
- Acceptance filtering
- CAN FD support
- FIFO interface / AXI4-Lite register interface
- Physical CAN transceiver integration
- FPGA board validation with a real CAN transceiver

## Important disclosure

This repository is intended as a **simulation/reference project**. The prepared artifact does not claim physical validation on a CAN bus or FPGA board. In an interview, describe it accurately as an RTL simulation project and explain how you would extend it to a hardware prototype.

## References

- Bosch CAN Specification 2.0, Part A
- NXP CAN protocol overview
