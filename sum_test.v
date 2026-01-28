`timescale 1ns / 1ps

module test_sum;
    reg clk = 0;
    reg rst = 0;
    
    // Выходы процессора
    wire [15:0] ACC;
    wire halted;
    
    // Генерация тактового сигнала
    always #1 clk <= ~clk;
    
    // Экземпляр процессора
    cpu dut(
        .clk(clk),
        .rst(rst),
        .ACC(ACC),
        .halted(halted)
    );
    
endmodule