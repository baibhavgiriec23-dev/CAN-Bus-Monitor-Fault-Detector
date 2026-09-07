#!/usr/bin/env python3
"""Reference model for the CAN 2.0A frame used by the Verilog testbench."""

ID = 0x123
DATA = bytes.fromhex("DE AD BE EF")
DLC = len(DATA)


def crc15(bits):
    crc = 0
    for bit in bits:
        feedback = ((crc >> 14) & 1) ^ bit
        crc = (crc << 1) & 0x7FFF
        if feedback:
            crc ^= 0x4599
    return crc


def bits_from_int(value, width):
    return [(value >> i) & 1 for i in range(width - 1, -1, -1)]

base = [0]                         # SOF
base += bits_from_int(ID, 11)      # ID
base += [0, 0, 0]                  # RTR, IDE, r0
base += bits_from_int(DLC, 4)      # DLC
for b in DATA:
    base += bits_from_int(b, 8)

crc = crc15(base)
crc_bits = bits_from_int(crc, 15)
pre_crc = base + crc_bits

stuffed = []
run = 0
previous = None
stuff_count = 0
for bit in pre_crc:
    if previous is None or bit != previous:
        run = 1
    else:
        run += 1
    stuffed.append(bit)
    previous = bit
    if run == 5:
        stuff_bit = 1 - bit
        stuffed.append(stuff_bit)
        stuff_count += 1
        previous = stuff_bit
        run = 1

wire = stuffed + [1, 0, 1] + [1] * 7

print(f"ID        = 0x{ID:03X}")
print(f"DLC       = {DLC}")
print(f"DATA      = {DATA.hex(' ').upper()}")
print(f"CRC-15    = 0x{crc:04X}")
print(f"Raw bits  = {len(pre_crc)}")
print(f"Stuff bits= {stuff_count}")
print(f"Wire bits = {len(wire)}")
print("WIRE      = " + ''.join(map(str, wire)))
