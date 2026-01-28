`timescale 1ns / 1ps

module cpu(
    input wire clk,
    input wire rst,
//    input wire [15:0] code_memory [0:255],
//    input wire [15:0] data_memory [0:255],
    output reg [15:0] ACC,
//    output reg [15:0] PC,
//    output reg [15:0] IR,
//    output reg [15:0] R1, R2, R3, R4, R5, R6, R7, R8,
//    output reg Z, N,
    output reg halted
);

    // Параметры состояний
    localparam STAGE_FETCH  = 2'b00;
    localparam STAGE_DECODE = 2'b01;
    localparam STAGE_EXECUTE = 2'b10;
    
    // Регистры
    reg [15:0] PC;
    reg [15:0] IR;
    reg [15:0] R1, R2, R3, R4, R5, R6, R7, R8;
    reg Z, N;
    
    // Коды операций (opcode)
    localparam OP_HALT = 4'hF;
    localparam OP_LOAD = 4'h1;
    localparam OP_STORE = 4'h2;
    localparam OP_ADD = 4'h3;
    localparam OP_SUB = 4'h4;
    localparam OP_MUL = 4'h5;
    localparam OP_CMP = 4'h6;
    localparam OP_JMP = 4'h7;
    localparam OP_JZ = 4'h8;
    localparam OP_JN = 4'h9;
    localparam OP_INC = 4'hA;
    localparam OP_DEC = 4'hB;
    
    // Типы адресации
    localparam ADDR_IMMEDIATE = 2'b00;  // Непосредственная (#)
    localparam ADDR_DIRECT = 2'b01;     // Прямая
    localparam ADDR_REGISTER = 2'b10;   // Регистровая (Rx)
    localparam ADDR_INDIRECT = 2'b11;   // Косвенно-регистровая ([Rx])
    
    // Памяти
    reg [15:0] data_mem [0:255];
    reg [15:0] code_mem [0:255];
    
    // Внутренние сигналы
    reg [15:0] operand_value;
    reg [1:0] addr_type;
    reg [9:0] ir_operand;
    reg [15:0] reg_addr;
    
    // Промежуточные переменные для вычисления
    reg [15:0] add_result;
    reg [15:0] sub_result;
    reg [15:0] mul_result;
    
    // Состояния автомата управления
    reg [1:0] state;
    
    // Декодирование инструкции
    wire [3:0] opcode = IR[15:12];
    
    // Загрузка программы из файла
    initial begin
        // Инициализация памяти команд нулями
        for (integer i = 0; i < 256; i = i + 1) begin
            code_mem[i] = 16'b0000000000000000;
        end
        
        // Загрузка программы суммы
        $readmemb("sum_program.mem", code_mem);
    end
    
    // Тестовые данные
    initial begin
        // Инициализация памяти данных нулями
        for (integer i = 0; i < 256; i = i + 1) begin
            data_mem[i] = 0;
        end
        
        // Данные для суммы: размер 10, затем 10 элементов
        data_mem[0] = 10;  // Размер массива
        data_mem[1] = 1;
        data_mem[2] = 2;
        data_mem[3] = 3;
        data_mem[4] = 4;
        data_mem[5] = 5;
        data_mem[6] = 6;
        data_mem[7] = 7;
        data_mem[8] = 8;
        data_mem[9] = 9;
        data_mem[10] = 10;
    end
        
    // Инициализация
    initial begin
        state = STAGE_FETCH;
        halted = 0;
        operand_value = 0;
        addr_type = 0;
        ir_operand = 0;
        add_result = 0;
        sub_result = 0;
        mul_result = 0;
        ACC = 0;
        PC = 0;
        IR = 0;
        R1 = 0; R2 = 0; R3 = 0; R4 = 0; R5 = 0; R6 = 0; R7 = 0; R8 = 0;
        Z = 0; N = 0;
    end
    
    // Основной процессорный цикл
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            // Сброс состояния
            ACC <= 0;
            PC <= 0;
            IR <= 0;
            R1 <= 0; R2 <= 0; R3 <= 0; R4 <= 0; R5 <= 0; R6 <= 0; R7 <= 0; R8 <= 0;
            Z <= 0;
            N <= 0;
            halted <= 0;
            state <= STAGE_FETCH;
            addr_type <= 0;
            ir_operand <= 0;
            operand_value <= 0;
        end else if (!halted) begin
            case(state)
                STAGE_FETCH: begin
                    if (PC < 256) begin
                        IR <= code_mem[PC];
                        state <= STAGE_DECODE;
                    end else begin
                        halted <= 1;
                    end
                end
                
                STAGE_DECODE: begin
                    // Сохраняем операнд и тип адресации
                    addr_type <= IR[11:10];
                    ir_operand <= IR[9:0];
                    
                    // Вычисление значения операнда
                    case(IR[11:10])
                        ADDR_IMMEDIATE: begin // Непосредственная адресация
                            operand_value <= IR[9:0];

                            // Знаковое расширение для 11-битного числа
//                            if (IR[9]) begin // Проверка знака (11-битное число)
//                                operand_value <= {6'b111111, IR[9:0]};
//                            end else begin
//                                operand_value <= {6'b000000, IR[9:0]};
//                            end
                        end
                        
                        ADDR_DIRECT: begin // Прямая адресация
                            operand_value <= data_mem[IR[9:0]];
                        end
                        
                        ADDR_REGISTER: begin // Регистровая адресация
                            case(IR[2:0])
                                3'b001: operand_value <= R1;
                                3'b010: operand_value <= R2;
                                3'b011: operand_value <= R3;
                                3'b100: operand_value <= R4;
                                default: operand_value <= 0;
                            endcase
                        end
                        
                        ADDR_INDIRECT: begin // Косвенно-регистровая адресация
                            case(IR[2:0])
                                3'b001: operand_value <= data_mem[R1];
                                3'b010: operand_value <= data_mem[R2];
                                3'b011: operand_value <= data_mem[R3];
                                3'b100: operand_value <= data_mem[R4];
                                default: operand_value <= 0;
                            endcase
                        end
                        
//                        default: operand_value <= 0;
                    endcase
                    
                    state <= STAGE_EXECUTE;
                end
                
                STAGE_EXECUTE: begin
                    case(opcode)
                        OP_HALT: begin // HALT
                            halted <= 1;
                        end
                        
                        OP_LOAD: begin // LOAD
                            ACC <= operand_value;
                            PC <= PC + 1;
                        end
                        
                        OP_STORE: begin // STORE
                            // Установка значения по адресу операнда
                            case(addr_type)
                                ADDR_DIRECT: begin // Прямая адресация
                                    if (ir_operand < 256) begin
                                        data_mem[ir_operand] <= ACC;
                                    end
                                end
                                
                                ADDR_REGISTER: begin // Регистровая адресация
                                    case(ir_operand[2:0])
                                        3'b001: R1 <= ACC;
                                        3'b010: R2 <= ACC;
                                        3'b011: R3 <= ACC;
                                        3'b100: R4 <= ACC;
                                    endcase
                                end
                                
                                ADDR_INDIRECT: begin // Косвенно-регистровая адресация
                                    case(ir_operand[2:0])
                                        3'b001: data_mem[R1] <= ACC;
                                        3'b010: data_mem[R2] <= ACC;
                                        3'b011: data_mem[R3] <= ACC;
                                        3'b100: data_mem[R4] <= ACC;
                                    endcase
                                end
                            endcase
                            PC <= PC + 1;
                        end
                        
                        OP_ADD: begin // ADD
                            add_result <= ACC + operand_value;
                            ACC <= (ACC + operand_value);
                            PC <= PC + 1;
                        end
                        
                        OP_SUB: begin // SUB
                            sub_result <= ACC - operand_value;
                            ACC <= sub_result;
                            PC <= PC + 1;
                        end
                        
                        OP_MUL: begin // MUL
                            mul_result <= ACC * operand_value;
                            ACC <= mul_result;
                            PC <= PC + 1;
                        end
                        
                        OP_CMP: begin // CMP
                            // Установка флагов
                            sub_result <= ACC - operand_value;
                            Z <= ACC - operand_value == 0;
                            N <= sub_result[15];
                            PC <= PC + 1;
                        end
                        
                        OP_JMP: begin // JMP
                            PC <= operand_value;
                        end
                        
                        OP_JZ: begin // JZ
                            if (Z) begin
                                PC <= operand_value;
                            end else begin
                                PC <= PC + 1;
                            end
                        end
                        
                        OP_JN: begin // JN
                            if (N) begin
                                PC <= operand_value;
                            end else begin
                                PC <= PC + 1;
                            end
                        end
                        
                        OP_INC: begin // INC
                            case(addr_type)
                                ADDR_DIRECT: begin
                                    if (ir_operand < 256) begin
                                        data_mem[ir_operand] <= data_mem[ir_operand] + 1;
                                    end
                                end
                                
                                ADDR_REGISTER: begin
                                    case(ir_operand[2:0])
                                        3'b001: R1 <= R1 + 1;
                                        3'b010: R2 <= R2 + 1;
                                        3'b011: R3 <= R3 + 1;
                                        3'b100: R4 <= R4 + 1;
                                    endcase
                                end
                                
                                ADDR_INDIRECT: begin
                                    case(ir_operand[2:0])
                                    3'b001: reg_addr = R1;
                                        3'b010: reg_addr = R2;
                                        3'b011: reg_addr = R3;
                                        3'b100: reg_addr = R4;
                                        3'b101: reg_addr = R5;
                                        3'b110: reg_addr = R6;
                                        3'b111: reg_addr = R7;
                                        3'b000: reg_addr = R8;
                                        default: reg_addr = 0;
                                    endcase
                                    
                                    if (reg_addr < 256) begin
                                        data_mem[reg_addr] <= data_mem[reg_addr] + 1;
                                    end
                                end
                            endcase
                            PC <= PC + 1;
                        end
                        
                        OP_DEC: begin // DEC
                            case(addr_type)
                                ADDR_DIRECT: begin
                                    if (ir_operand < 256) begin
                                        data_mem[ir_operand] <= data_mem[ir_operand] - 1;
                                    end
                                end
                                
                                ADDR_REGISTER: begin
                                    case(ir_operand[2:0])
                                        3'b001: R1 <= R1 - 1;
                                        3'b010: R2 <= R2 - 1;
                                        3'b011: R3 <= R3 - 1;
                                        3'b100: R4 <= R4 - 1;
                                    endcase
                                end
                                
                                ADDR_INDIRECT: begin
//                                    reg [15:0] reg_addr;
                                    case(ir_operand[2:0])
                                        3'b001: reg_addr = R1;
                                        3'b010: reg_addr = R2;
                                        3'b011: reg_addr = R3;
                                        3'b100: reg_addr = R4;
                                        3'b101: reg_addr = R5;
                                        3'b110: reg_addr = R6;
                                        3'b111: reg_addr = R7;
                                        3'b000: reg_addr = R8;
                                        default: reg_addr = 0;
                                    endcase
                                    
                                    if (reg_addr < 256) begin
                                        data_mem[reg_addr] <= data_mem[reg_addr] - 1;
                                    end
                                end
                            endcase
                            PC <= PC + 1;
                        end
                        
                        default: begin
                            PC <= PC + 1;
                        end
                    endcase
                    state <= STAGE_FETCH;
                end
            endcase
        end
    end
    
endmodule