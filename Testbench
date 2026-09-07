`timescale 1ns/1ps
module tb_can_monitor;
    reg clk = 0;
    reg rst_n = 0;
    reg bit_tick = 0;
    reg can_rx = 1;

    wire frame_valid;
    wire crc_error;
    wire stuff_error;
    wire format_error;
    wire [10:0] frame_id;
    wire [3:0] frame_dlc;
    wire [63:0] frame_data;

    can_monitor dut (
        .clk(clk), .rst_n(rst_n), .bit_tick(bit_tick), .can_rx(can_rx),
        .frame_valid(frame_valid), .crc_error(crc_error),
        .stuff_error(stuff_error), .format_error(format_error),
        .frame_id(frame_id), .frame_dlc(frame_dlc), .frame_data(frame_data)
    );

    always #5 clk = ~clk;

    // Generated from a standard CAN 2.0A frame:
    // ID=0x123, DLC=4, DATA=DE AD BE EF, CRC=0x4E6B.
    // Two stuff bits are inserted by the CAN transmitter.
    reg [77:0] frame_bits;
    integer i;

    task send_bit;
        input b;
        begin
            @(negedge clk);
            can_rx = b;
            bit_tick = 1'b1;
            @(negedge clk);
            bit_tick = 1'b0;
        end
    endtask

    initial begin
        // Wire-level frame, including stuffing, CRC delimiter, ACK,
        // ACK delimiter and EOF. See results/expected_results.txt.
        frame_bits = 78'b000100100011000010011011110101011011011111001110111110001110011010111011111111;

        repeat (4) @(negedge clk);
        rst_n = 1'b1;
        repeat (4) @(negedge clk);

        for (i = 77; i >= 0; i = i - 1)
            send_bit(frame_bits[i]);

        // Wait until the decoder asserts frame_valid at EOF.
        @(posedge frame_valid);
        #1;
        $display("---------------------------------------------");
        $display("CAN MONITOR SIMULATION RESULT");
        $display("Frame valid : %0d", frame_valid);
        $display("Frame ID    : 0x%03h", frame_id);
        $display("DLC         : %0d", frame_dlc);
        $display("DATA        : 0x%016h", frame_data);
        $display("CRC error   : %0d", crc_error);
        $display("Stuff error : %0d", stuff_error);
        $display("Format error: %0d", format_error);
        $display("---------------------------------------------");
        $finish;
    end
endmodule
