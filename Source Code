`timescale 1ns/1ps

// Simulation-oriented Classic CAN 2.0A standard-frame monitor.
// Assumptions: already-sampled CAN RX bit stream, standard data frames only,
// no physical CAN transceiver or analog bit timing included.
module can_monitor (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        bit_tick,
    input  wire        can_rx,
    output reg         frame_valid,
    output reg         crc_error,
    output reg         stuff_error,
    output reg         format_error,
    output reg [10:0]  frame_id,
    output reg [3:0]   frame_dlc,
    output reg [63:0]  frame_data
);

    localparam S_IDLE = 2'd0;
    localparam S_RX   = 2'd1;
    localparam S_WAIT = 2'd2;

    reg [1:0] state;
    reg [6:0] bit_pos;
    reg [3:0] dlc;
    reg [2:0] data_byte_count;
    reg [3:0] data_bit_count;
    reg [14:0] crc_reg;
    reg [14:0] rx_crc;
    reg [14:0] rx_crc_next;
    reg [10:0] id_reg;
    reg [63:0] data_reg;

    reg last_bit;
    reg [2:0] run_len;
    reg stuff_pending;
    reg [6:0] data_end_pos;
    reg [6:0] crc_start_pos;
    reg [6:0] crc_end_pos;

    function [14:0] crc15_next;
        input [14:0] crc;
        input        bit_in;
        reg feedback;
        begin
            feedback = crc[14] ^ bit_in;
            crc15_next = {crc[13:0],1'b0};
            if (feedback)
                crc15_next = crc15_next ^ 15'h4599;
        end
    endfunction

    task start_frame;
        begin
            state         <= S_RX;
            bit_pos       <= 0;
            crc_reg       <= 0;
            rx_crc        <= 0;
            id_reg        <= 0;
            data_reg      <= 0;
            dlc           <= 0;
            data_byte_count <= 0;
            data_bit_count  <= 0;
            last_bit      <= 1'b0;
            run_len       <= 3'd1;
            stuff_pending <= 1'b0;
            frame_valid  <= 1'b0;
            crc_error    <= 1'b0;
            stuff_error  <= 1'b0;
            format_error <= 1'b0;
        end
    endtask

    always @(posedge clk) begin
        if (!rst_n) begin
            state        <= S_IDLE;
            bit_pos      <= 0;
            frame_valid  <= 0;
            crc_error    <= 0;
            stuff_error  <= 0;
            format_error <= 0;
            frame_id     <= 0;
            frame_dlc    <= 0;
            frame_data   <= 0;
            crc_reg      <= 0;
            rx_crc       <= 0;
            id_reg       <= 0;
            data_reg     <= 0;
            dlc          <= 0;
            run_len      <= 0;
            stuff_pending <= 0;
        end else if (bit_tick) begin
            frame_valid <= 1'b0;

            if (state == S_IDLE) begin
                // CAN SOF is dominant (logic 0).
                if (can_rx == 1'b0)
                    start_frame();
            end else if (state == S_RX) begin
                // Handle an inserted stuff bit. It is not part of the frame
                // fields and is therefore excluded from CRC calculation.
                if (stuff_pending) begin
                    if (can_rx == last_bit) begin
                        stuff_error <= 1'b1;
                        state <= S_WAIT;
                    end else begin
                        last_bit      <= can_rx;
                        run_len       <= 3'd1;
                        stuff_pending <= 1'b0;
                    end
                end else begin
                    // Parse the next destuffed bit.
                    if (bit_pos == 0) begin
                        if (can_rx != 1'b0)
                            format_error <= 1'b1;
                    end else if (bit_pos >= 1 && bit_pos <= 11) begin
                        id_reg <= {id_reg[9:0], can_rx};
                    end else if (bit_pos == 12) begin
                        if (can_rx != 1'b0) format_error <= 1'b1; // RTR=0
                    end else if (bit_pos == 13) begin
                        if (can_rx != 1'b0) format_error <= 1'b1; // IDE=0
                    end else if (bit_pos == 14) begin
                        if (can_rx != 1'b0) format_error <= 1'b1; // r0=0
                    end else if (bit_pos >= 15 && bit_pos <= 18) begin
                        dlc <= {dlc[2:0], can_rx};
                    end else if (bit_pos >= 19 && bit_pos < (19 + (dlc * 8))) begin
                        data_reg <= {data_reg[62:0], can_rx};
                    end else if (bit_pos >= (19 + (dlc * 8)) && bit_pos < (34 + (dlc * 8))) begin
                        rx_crc <= {rx_crc[13:0], can_rx};
                    end else if (bit_pos == (34 + (dlc * 8))) begin
                        if (can_rx != 1'b1) format_error <= 1'b1; // CRC delimiter
                        if (rx_crc != crc_reg)
                            crc_error <= 1'b1;
                    end else if (bit_pos == (35 + (dlc * 8))) begin
                        // ACK slot: monitor accepts either value.
                    end else if (bit_pos == (36 + (dlc * 8))) begin
                        if (can_rx != 1'b1) format_error <= 1'b1;
                    end else if (bit_pos >= (37 + (dlc * 8)) && bit_pos < (44 + (dlc * 8))) begin
                        if (can_rx != 1'b1) format_error <= 1'b1;
                    end else if (bit_pos == (44 + (dlc * 8))) begin
                        frame_id    <= id_reg;
                        frame_dlc   <= dlc;
                        frame_data  <= data_reg;
                        frame_valid <= 1'b1;
                        state       <= S_WAIT;
                    end

                    // CRC covers SOF through the end of DATA field.
                    if (bit_pos <= (18 + (dlc * 8)))
                        crc_reg <= crc15_next(crc_reg, can_rx);

                    // Bit-stuff tracking applies through the CRC sequence.
                    if (bit_pos <= (33 + (dlc * 8))) begin
                        if (can_rx == last_bit) begin
                            if (run_len == 3'd5) begin
                                stuff_pending <= 1'b1;
                                run_len <= 3'd5;
                            end else begin
                                run_len <= run_len + 1'b1;
                            end
                        end else begin
                            run_len  <= 3'd1;
                            last_bit <= can_rx;
                        end
                    end

                    bit_pos <= bit_pos + 1'b1;
                end
            end else if (state == S_WAIT) begin
                // Wait for recessive bus idle before accepting the next frame.
                if (can_rx == 1'b1) begin
                    state <= S_IDLE;
                    if (frame_valid) frame_valid <= 1'b0;
                end
            end
        end
    end
endmodule
