# SimpleAlu Documentation

## Module Interface

```systemverilog
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
```
