START:
    LOAD #0
    STORE R1     ; R1 = результат

    LOAD 0       ; ACC = размер массива
    STORE R2     ; R2 = счетчик

    LOAD #1
    STORE R3     ; R3 = индекс массива A
    
    LOAD R2
    ADD #1
    STORE R4     ; R4 = индекс массива B

LOOP:
    LOAD R2      ; ACC = счетчик
    CMP #0       ; Сравнение с 0
    JZ END       ; Закончение если счетчик == 0

    LOAD [R3]    ; ACC = A[i]
    MUL [R4]     ; ACC = A[i] * B[i]
    ADD R1       ; Прибавление к итоговой сумме
    STORE R1     ; Обновление результата

    INC R3
    INC R4
    DEC R2
    JMP LOOP

END:
    LOAD R1      ; ACC = результат
    HALT
