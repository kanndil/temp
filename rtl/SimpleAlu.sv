`default_nettype none

//=============================================================================
// Module: SimpleAlu
// Description: Simple 32-bit Arithmetic Logic Unit with basic operations
// Author: NativeChips Agent
// Date: 2025-08-29
// License: Apache License 2.0
//=============================================================================

module SimpleAlu #(
  parameter int DATA_WIDTH = 32
) (
  // Data inputs
  input  logic [DATA_WIDTH-1:0] a_i,
  input  logic [DATA_WIDTH-1:0] b_i,
  input  logic [3:0]            op_i,
  
  // Data outputs
  output logic [DATA_WIDTH-1:0] result_o,
  output logic                  zero_o,
  output logic                  overflow_o,
  output logic                  carry_o
);

  // ALU operation codes
  localparam logic [3:0] ALU_ADD  = 4'b0000;
  localparam logic [3:0] ALU_SUB  = 4'b0001;
  localparam logic [3:0] ALU_AND  = 4'b0010;
  localparam logic [3:0] ALU_OR   = 4'b0011;
  localparam logic [3:0] ALU_XOR  = 4'b0100;
  localparam logic [3:0] ALU_SLL  = 4'b0101;  // Shift left logical
  localparam logic [3:0] ALU_SRL  = 4'b0110;  // Shift right logical
  localparam logic [3:0] ALU_SRA  = 4'b0111;  // Shift right arithmetic
  localparam logic [3:0] ALU_SLT  = 4'b1000;  // Set less than
  localparam logic [3:0] ALU_SLTU = 4'b1001;  // Set less than unsigned
  localparam logic [3:0] ALU_NOR  = 4'b1010;
  localparam logic [3:0] ALU_NAND = 4'b1011;

  // Internal signals
  logic [DATA_WIDTH:0]   add_result;
  logic [DATA_WIDTH:0]   sub_result;
  logic [4:0]            shift_amount;
  logic                  signed_lt;
  logic                  unsigned_lt;

  // Shift amount (use lower 5 bits for 32-bit data)
  assign shift_amount = b_i[4:0];

  // Addition with carry
  assign add_result = {1'b0, a_i} + {1'b0, b_i};
  
  // Subtraction with borrow
  assign sub_result = {1'b0, a_i} - {1'b0, b_i};

  // Signed and unsigned comparisons
  assign signed_lt   = $signed(a_i) < $signed(b_i);
  assign unsigned_lt = a_i < b_i;

  // Main ALU logic
  always_comb begin
    result_o   = '0;
    carry_o    = 1'b0;
    overflow_o = 1'b0;
    
    case (op_i)
      ALU_ADD: begin
        result_o = add_result[DATA_WIDTH-1:0];
        carry_o  = add_result[DATA_WIDTH];
        // Overflow occurs when signs of operands are same but result sign differs
        overflow_o = (a_i[DATA_WIDTH-1] == b_i[DATA_WIDTH-1]) && 
                     (result_o[DATA_WIDTH-1] != a_i[DATA_WIDTH-1]);
      end
      
      ALU_SUB: begin
        result_o = sub_result[DATA_WIDTH-1:0];
        carry_o  = sub_result[DATA_WIDTH];
        // Overflow occurs when signs of operands are different and result sign matches subtrahend
        overflow_o = (a_i[DATA_WIDTH-1] != b_i[DATA_WIDTH-1]) && 
                     (result_o[DATA_WIDTH-1] == b_i[DATA_WIDTH-1]);
      end
      
      ALU_AND:  result_o = a_i & b_i;
      ALU_OR:   result_o = a_i | b_i;
      ALU_XOR:  result_o = a_i ^ b_i;
      ALU_NOR:  result_o = ~(a_i | b_i);
      ALU_NAND: result_o = ~(a_i & b_i);
      
      ALU_SLL:  result_o = a_i << shift_amount;
      ALU_SRL:  result_o = a_i >> shift_amount;
      ALU_SRA:  result_o = $signed(a_i) >>> shift_amount;
      
      ALU_SLT:  result_o = {{(DATA_WIDTH-1){1'b0}}, signed_lt};
      ALU_SLTU: result_o = {{(DATA_WIDTH-1){1'b0}}, unsigned_lt};
      
      default:  result_o = '0;
    endcase
  end

  // Zero flag
  assign zero_o = (result_o == '0);

endmodule

`default_nettype wire