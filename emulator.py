import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class Emulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Эмулятор с Гарвардской архитектурой и одноадресной системой команд")
        self.root.geometry("1400x800")
        
        # Инициализация процессора
        self.reset_cpu()
        
        # Создание интерфейса
        self.create_widgets()
        
    def reset_cpu(self):
        """Сброс состояния процессора"""
        # Регистры
        self.ACC = 0  # Аккумулятор
        self.PC = 0   # Счетчик команд
        self.IR = 0   # Регистр команд
        
        # Регистры общего назначения R1-R8
        self.registers = {f"R{i}": 0 for i in range(1, 9)}
        
        # Флаги
        self.Z = 0  # Флаг нуля
        self.N = 0  # Флаг отрицательного числа
        
        # Память команд (Гарвардская архитектура - отдельная)
        self.code_memory = [0] * 256  # 256 ячеек по 16 бит
        
        # Память данных
        self.data_memory = [0] * 256  # 256 ячеек
        
        # Машинный код (для отображения)
        self.machine_code = []
        
        # Текущая выполняемая программа
        self.current_program = ""
        
        # Режим выполнения
        self.running = False
        self.step_mode = False
        
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Основной контейнер
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель (редактирование и управление)
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)
        
        # Правая панель (состояние процессора)
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)
        
        # ===== ЛЕВАЯ ПАНЕЛЬ =====
        
        # 1. Редактор ассемблерного кода
        code_frame = ttk.LabelFrame(left_panel, text="Ассемблерный код", padding=10)
        code_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.code_text = scrolledtext.ScrolledText(code_frame, width=50, height=20, font=("Courier New", 10))
        self.code_text.pack(fill=tk.BOTH, expand=True)
        
        # 2. Ввод данных
        data_frame = ttk.LabelFrame(left_panel, text="Входные данные", padding=10)
        data_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.data_text = scrolledtext.ScrolledText(data_frame, width=50, height=5, font=("Courier New", 10))
        self.data_text.pack(fill=tk.X, pady=5)
        
        # 3. Кнопки управления
        button_frame = ttk.LabelFrame(left_panel, text="Примерные программы", padding=10)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(button_frame, text="Сумма массива", command=self.load_sum_example).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Свертка двух массивов", command=self.load_convolution_example).pack(side=tk.LEFT, padx=2)
        
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(button_frame, text="Загрузить", command=self.load_program).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Выполнить полно", command=self.run_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Выполнить пошагово", command=self.step).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Сбросить", command=self.reset).pack(side=tk.LEFT, padx=2)

        # ===== ПРАВАЯ ПАНЕЛЬ =====
        
        # Верхняя часть: регистры и флаги
        top_right = ttk.Frame(right_panel)
        top_right.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 1. Специальные регистры
        special_frame = ttk.LabelFrame(top_right, text="Специальные регистры", padding=10)
        special_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.acc_label = ttk.Label(special_frame, text="ACC: 0", font=("Courier New", 12, "bold"))
        self.acc_label.pack(anchor=tk.W)
        
        self.pc_label = ttk.Label(special_frame, text="PC: 0", font=("Courier New", 12))
        self.pc_label.pack(anchor=tk.W)
        
        self.ir_label = ttk.Label(special_frame, text="IR: 0x0000", font=("Courier New", 12))
        self.ir_label.pack(anchor=tk.W)
        
        # 2. Регистры общего назначения
        reg_frame = ttk.LabelFrame(top_right, text="Регистры общего назначения", padding=10)
        reg_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.reg_labels = {}
        reg_grid = ttk.Frame(reg_frame)
        reg_grid.pack()
        
        for i in range(1, 5):
            frame = ttk.Frame(reg_grid)
            frame.pack(anchor=tk.W)
            for j in range(2):
                reg_num = i + (j * 4)
                if reg_num <= 8:
                    reg_name = f"R{reg_num}"
                    label = ttk.Label(frame, text=f"{reg_name}: 0", font=("Courier New", 10), width=15, anchor=tk.W)
                    label.pack(side=tk.LEFT, padx=5)
                    self.reg_labels[reg_name] = label
        
        # 3. Флаги
        flags_frame = ttk.LabelFrame(top_right, text="Флаги", padding=10)
        flags_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.z_label = ttk.Label(flags_frame, text="Z (Zero): 0", font=("Courier New", 12))
        self.z_label.pack(anchor=tk.W)
        
        self.n_label = ttk.Label(flags_frame, text="N (Negative): 0", font=("Courier New", 12))
        self.n_label.pack(anchor=tk.W)
        
        # Нижняя часть: память
        bottom_right = ttk.Frame(right_panel)
        bottom_right.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 4. Память команд
        code_mem_frame = ttk.LabelFrame(bottom_right, text="Память команд", padding=10)
        code_mem_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.code_mem_text = scrolledtext.ScrolledText(code_mem_frame, width=35, height=30, 
                                                       font=("Courier New", 9))
        self.code_mem_text.pack(fill=tk.BOTH, expand=True)
        self.code_mem_text.config(state=tk.DISABLED)
        
        # 5. Память данных
        data_mem_frame = ttk.LabelFrame(bottom_right, text="Память данных", padding=10)
        data_mem_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.data_mem_text = scrolledtext.ScrolledText(data_mem_frame, width=35, height=30, 
                                                       font=("Courier New", 9))
        self.data_mem_text.pack(fill=tk.BOTH, expand=True)
        self.data_mem_text.config(state=tk.DISABLED)
        
        # Статус бар
        self.status_bar = ttk.Label(self.root, text="Готов к работе", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def update_display(self):
        """Обновление отображения состояния процессора"""
        # Специальные регистры
        self.acc_label.config(text=f"ACC: {self.ACC}")
        self.pc_label.config(text=f"PC: {self.PC}")
        self.ir_label.config(text=f"IR: 0x{self.IR:04X}")
        
        # Регистры общего назначения
        for reg, label in self.reg_labels.items():
            label.config(text=f"{reg}: {self.registers[reg]}")
        
        # Флаги
        self.z_label.config(text=f"Z (Zero): {self.Z}")
        self.n_label.config(text=f"N (Negative): {self.N}")
        
        # Память команд
        self.code_mem_text.config(state=tk.NORMAL)
        self.code_mem_text.delete("1.0", tk.END)
        
        for addr in range(0, min(32, len(self.code_memory))):
            instr = self.code_memory[addr]
            if instr != 0 or addr == self.PC:
                # Форматирование: адрес | машинный код | ассемблер
                asm = self.disassemble(instr) if instr != 0 else "NOP"
                line = f"{addr:03d}: 0x{instr:04X}  {asm}\n"
                
                # Подсветка текущей команды
                if addr == self.PC:
                    self.code_mem_text.insert(tk.END, line, "current")
                else:
                    self.code_mem_text.insert(tk.END, line)
        
        self.code_mem_text.tag_config("current", background="lightyellow")
        self.code_mem_text.config(state=tk.DISABLED)
        
        # Память данных
        self.data_mem_text.config(state=tk.NORMAL)
        self.data_mem_text.delete("1.0", tk.END)
        
        for addr in range(0, min(32, len(self.data_memory))):
            value = self.data_memory[addr]
            line = f"{addr:03d}: {value}\n"
            self.data_mem_text.insert(tk.END, line)
        
        self.data_mem_text.config(state=tk.DISABLED)
        
        # Статус бар
        if self.running:
            self.status_bar.config(text="Выполнение...")
        else:
            self.status_bar.config(text="Готов к работе")
    
    def parse_operand(self, operand_str):
        """Парсинг операнда и определение типа адресации"""
        if not operand_str:
            return 0, 0  # Нет операнда
        
        operand_str = operand_str.strip()
        
        # Непосредственная адресация (#число)
        if operand_str.startswith('#'):
            try:
                value = int(operand_str[1:])
                return value, 0b00  # Непосредственная адресация
            except:
                return 0, 0
        
        # Косвенно-регистровая адресация ([Rx])
        elif operand_str.startswith('[') and operand_str.endswith(']'):
            reg_name = operand_str[1:-1].strip()
            if reg_name in self.registers:
                reg_num = int(reg_name[1:])
                return reg_num, 0b11  # Косвенно-регистровая адресация
        
        # Регистровая адресация (Rx)
        elif operand_str.startswith('R'):
            try:
                reg_num = int(operand_str[1:])
                if 1 <= reg_num <= 8:
                    return reg_num, 0b10  # Регистровая адресация
            except:
                pass
        
        # Прямая адресация (число) или метка
        try:
            addr = int(operand_str)
            return addr, 0b01  # Прямая адресация
        except:
            # Это метка, будет обработано позже
            return operand_str, 0b01
    
    def encode_instruction(self, opcode, operand_value, addr_type):
        """Кодирование инструкции в 16-битное слово"""
        # Формат: [15:12] - opcode, [11:10] - тип адресации, [9:0] - операнд
        
        operand = operand_value & 0x3FF

        instruction = (opcode << 12) | (addr_type << 10) | operand
        return instruction
    
    def disassemble(self, instruction):
        """Дизассемблирование машинного кода в ассемблерную инструкцию"""
        opcode = (instruction >> 12) & 0xF
        addr_type = (instruction >> 10) & 0x3
        operand = instruction & 0x3FF
        
        # Таблица мнемоник
        mnemonics = {
            0xF: "HALT",
            0x1: "LOAD",
            0x2: "STORE",
            0x3: "ADD",
            0x4: "SUB",
            0x5: "MUL",
            0x6: "CMP",
            0x7: "JMP",
            0x8: "JZ",
            0x9: "JN",
            0xA: "INC",
            0xB: "DEC"
        }
        
        if opcode not in mnemonics:
            return f"UNKNOWN 0x{instruction:04X}"
        
        mnemonic = mnemonics[opcode]
        
        # Формирование строки операнда
        if mnemonic == "HALT":
            return "HALT"
        
        # Определение типа адресации
        if addr_type == 0b00:  # Непосредственная
            return f"{mnemonic} #{operand}"
        elif addr_type == 0b01:  # Прямая
            return f"{mnemonic} {operand}"
        elif addr_type == 0b10:  # Регистровая
            if 1 <= operand <= 8:
                return f"{mnemonic} R{operand}"
            else:
                return f"{mnemonic} 0x{operand:X}"
        elif addr_type == 0b11:  # Косвенно-регистровая
            if 1 <= operand <= 8:
                return f"{mnemonic} [R{operand}]"
            else:
                return f"{mnemonic} 0x{operand:X}"
        
        return f"{mnemonic} 0x{operand:X}"
    
    def get_operand_value(self, instruction):
        """Получение фактического значения операнда"""
        addr_type = (instruction >> 10) & 0x3
        operand = instruction & 0x3FF
        
        if addr_type == 0b00:  # Непосредственная
            # Для знаковых чисел
            if operand & 0x200:  # Проверка на отрицательное (11-битное со знаком)
                return operand - 0x400  # Преобразование в отрицательное
            return operand
        
        elif addr_type == 0b01:  # Прямая
            if operand < len(self.data_memory):
                return self.data_memory[operand]
        
        elif addr_type == 0b10:  # Регистровая
            if 1 <= operand <= 8:
                reg_name = f"R{operand}"
                return self.registers[reg_name]
        
        elif addr_type == 0b11:  # Косвенно-регистровая
            if 1 <= operand <= 8:
                reg_name = f"R{operand}"
                addr = self.registers[reg_name]
                if 0 <= addr < len(self.data_memory):
                    return self.data_memory[addr]
        
        return 0
    
    def set_operand_value(self, instruction, value):
        """Установка значения по адресу операнда"""
        addr_type = (instruction >> 10) & 0x3
        operand = instruction & 0x3FF
        
        if addr_type == 0b01:  # Прямая
            if operand < len(self.data_memory):
                self.data_memory[operand] = value
        
        elif addr_type == 0b10:  # Регистровая
            if 1 <= operand <= 8:
                reg_name = f"R{operand}"
                self.registers[reg_name] = value
        
        elif addr_type == 0b11:  # Косвенно-регистровая
            if 1 <= operand <= 8:
                reg_name = f"R{operand}"
                addr = self.registers[reg_name]
                if 0 <= addr < len(self.data_memory):
                    self.data_memory[addr] = value
    
    def load_data_memory(self, data_str):
        """Загрузка данных в память"""
        try:
            numbers = list(map(int, data_str.split()))
            
            # Очистка памяти данных
            self.data_memory = [0] * 256
            
            # Загрузка данных
            for i, num in enumerate(numbers):
                if i < len(self.data_memory):
                    self.data_memory[i] = num
            
            return True
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
            return False
    
    def assemble_program(self, asm_code):
        """Ассемблирование программы из текста"""
        lines = asm_code.split('\n')
        machine_code = []
        labels = {}
        current_addr = 0
        
        # Первый проход: сбор меток
        for line in lines:
            line = line.strip()
            
            # Пропуск пустых строк и комментариев
            if not line or line.startswith(';'):
                continue
            
            # Удаление комментариев
            if ';' in line:
                line = line.split(';')[0].strip()
            
            # Проверка на метку
            if line.endswith(':'):
                label = line[:-1].strip()
                labels[label] = current_addr
                continue
            
            current_addr += 1
        
        # Второй проход: ассемблирование
        current_addr = 0
        for line in lines:
            line = line.strip()
            
            # Пропуск пустых строк, комментариев и меток
            if not line or line.startswith(';') or line.endswith(':'):
                continue
            
            # Удаление комментариев
            if ';' in line:
                line = line.split(';')[0].strip()
            
            # Разделение на мнемонику и операнд
            parts = line.split(None, 1)
            mnemonic = parts[0].upper()
            operand_str = parts[1] if len(parts) > 1 else ""
            
            # Таблица опкодов
            opcodes = {
                "HALT": 0xF,
                "LOAD": 0x1,
                "STORE": 0x2,
                "ADD": 0x3,
                "SUB": 0x4,
                "MUL": 0x5,
                "CMP": 0x6,
                "JMP": 0x7,
                "JZ": 0x8,
                "JN": 0x9,
                "INC": 0xA,
                "DEC": 0xB
            }
            
            if mnemonic not in opcodes:
                machine_code.append(0)
                current_addr += 1
                continue
            
            opcode = opcodes[mnemonic]
            
            # Для команд переходов - адрес перехода
            if mnemonic in ["JMP", "JZ", "JN"]:
                if operand_str in labels:
                    operand_value = labels[operand_str]
                    addr_type = 0b00  # Непосредственная адресация для адреса перехода
                else:
                    # Пробуем как число
                    try:
                        operand_value = int(operand_str)
                        addr_type = 0b00
                    except:
                        operand_value = 0
                        addr_type = 0b00
            else:
                # Для остальных команд парсим операнд
                operand_value, addr_type = self.parse_operand(operand_str)
                
                # Если это метка (строка) для не-JMP команд, ошибка
                if isinstance(operand_value, str):
                    messagebox.showerror("Ошибка", f"Неверный операнд '{operand_value}' для команды {mnemonic}")
                    return []
            
            instruction = self.encode_instruction(opcode, operand_value, addr_type)
            machine_code.append(instruction)
            current_addr += 1
        
        return machine_code
    
    def load_program(self):
        """Загрузка программы из редактора"""
        # Получение кода и данных
        asm_code = self.code_text.get("1.0", tk.END)
        data_str = self.data_text.get("1.0", tk.END).strip()
        
        # Сброс процессора
        self.reset_cpu()
        
        # Загрузка данных в память
        if not self.load_data_memory(data_str):
            return
        
        # Ассемблирование программы
        self.machine_code = self.assemble_program(asm_code)
        
        if not self.machine_code:
            messagebox.showerror("Ошибка", "Ошибка ассемблирования программы")
            return
        
        # Загрузка в память команд
        for i, instr in enumerate(self.machine_code):
            if i < len(self.code_memory):
                self.code_memory[i] = instr
        
        self.current_program = asm_code
        self.update_display()
        
        # Показываем количество загруженных команд
        non_zero = sum(1 for instr in self.machine_code if instr != 0)
        messagebox.showinfo("Успех", f"Программа загружена в память.\nЗагружено {non_zero} команд.")
    
    def execute_instruction(self):
        """Выполнение одной инструкции"""
        if self.PC >= len(self.code_memory):
            self.running = False
            return False
        
        # Загрузка инструкции
        self.IR = self.code_memory[self.PC]
        
        # Если команда 0 (NOP), пропускаем
        if self.IR == 0:
            self.PC += 1
            return True
        
        opcode = (self.IR >> 12) & 0xF
        
        # Выполнение инструкции
        if opcode == 0xF:  # HALT
            self.running = False
            self.PC += 1
            return False
        
        elif opcode == 0x1:  # LOAD
            value = self.get_operand_value(self.IR)
            self.ACC = value
            self.PC += 1
        
        elif opcode == 0x2:  # STORE
            self.set_operand_value(self.IR, self.ACC)
            self.PC += 1
        
        elif opcode == 0x3:  # ADD
            value = self.get_operand_value(self.IR)
            self.ACC += value
            self.PC += 1
        
        elif opcode == 0x4:  # SUB
            value = self.get_operand_value(self.IR)
            self.ACC -= value
            self.PC += 1
        
        elif opcode == 0x5:  # MUL
            value = self.get_operand_value(self.IR)
            self.ACC *= value
            self.PC += 1
        
        elif opcode == 0x6:  # CMP
            value = self.get_operand_value(self.IR)
            result = self.ACC - value
            
            # Установка флагов
            self.Z = 1 if result == 0 else 0
            self.N = 1 if result < 0 else 0
            self.PC += 1
        
        elif opcode == 0x7:  # JMP
            addr = self.get_operand_value(self.IR)
            self.PC = addr
        
        elif opcode == 0x8:  # JZ
            if self.Z:
                addr = self.get_operand_value(self.IR)
                self.PC = addr
            else:
                self.PC += 1
        
        elif opcode == 0x9:  # JN
            if self.N:
                addr = self.get_operand_value(self.IR)
                self.PC = addr
            else:
                self.PC += 1
        
        elif opcode == 0xA:  # INC
            value = self.get_operand_value(self.IR)
            self.set_operand_value(self.IR, value + 1)
            self.PC += 1
        
        elif opcode == 0xB:  # DEC
            value = self.get_operand_value(self.IR)
            self.set_operand_value(self.IR, value - 1)
            self.PC += 1
        
        else:
            # Неизвестная инструкция
            self.PC += 1
        
        # Обновление флагов после арифметических операций (кроме CMP)
        if opcode in [0x1, 0x3, 0x4, 0x5]:
            self.Z = 1 if self.ACC == 0 else 0
            self.N = 1 if self.ACC < 0 else 0
        
        return True
    
    def run_all(self):
        """Выполнение всей программы"""
        if not self.machine_code or all(instr == 0 for instr in self.machine_code):
            messagebox.showwarning("Предупреждение", "Сначала загрузите программу")
            return
        
        self.running = True
        self.step_mode = False
        
        max_steps = 1000  # Защита от бесконечного цикла
        steps = 0
        
        # Обновляем дисплей перед началом
        self.update_display()
        self.root.update()
        
        while self.running and steps < max_steps:
            if not self.execute_instruction():
                break
            
            steps += 1
            
            # Обновляем дисплей после каждого шага
            self.update_display()
            self.root.update()
            
            # Небольшая задержка для визуализации
            self.root.after(50)
        
        self.running = False
        self.update_display()
        
        if steps >= max_steps:
            messagebox.showwarning("Предупреждение", 
                                 f"Превышено максимальное количество шагов ({max_steps})\n"
                                 f"Возможен бесконечный цикл. PC={self.PC}")
        else:
            messagebox.showinfo("Завершено", 
                              f"Выполнение программы завершено за {steps} шагов.\n"
                              f"Результат в ACC: {self.ACC}")
    
    def step(self):
        """Пошаговое выполнение"""
        if not self.machine_code or all(instr == 0 for instr in self.machine_code):
            messagebox.showwarning("Предупреждение", "Сначала загрузите программу")
            return
        
        self.running = True
        
        result = self.execute_instruction()
        self.update_display()
        
        # Проверка на HALT или конец программы
        if not result or self.IR == 0xF:
            self.running = False
            messagebox.showinfo("Завершено", f"Программа завершена.\nРезультат в ACC: {self.ACC}")
    
    def reset(self):
        """Сброс эмулятора"""
        self.reset_cpu()
        self.update_display()
        messagebox.showinfo("Сброс", "Эмулятор сброшен в начальное состояние")

    def load_sum_example(self):
        """Загрузка примера программы для суммы массива"""
        # Программа для суммы массива
        sum_code = """START:
    LOAD #0
    STORE R1     ; R1 = сумма

    LOAD 0       ; ACC = размер массива
    STORE R2     ; R2 = счетчик

    LOAD #1
    STORE R3     ; R3 = индекс массива

LOOP:
    LOAD R2      ; ACC = счетчик
    CMP #0       ; Сравнить с 0
    JZ END       ; Если счетчик == 0, закончить

    LOAD [R3]    ; ACC = элемент массива
    ADD R1       ; ACC = ACC + сумма
    STORE R1     ; R1 = новая сумма

    INC R3       ; Следующий элемент
    DEC R2       ; Уменьшить счетчик
    JMP LOOP     ; Повторить цикл

END:
    LOAD R1      ; ACC = результат
    HALT"""
        
        # Данные для суммы: размер 10, затем 10 элементов
        sum_data = """10 1 2 3 4 5 6 7 8 9 10"""
        
        self.code_text.delete("1.0", tk.END)
        self.code_text.insert("1.0", sum_code)
        
        self.data_text.delete("1.0", tk.END)
        self.data_text.insert("1.0", sum_data)
        
        messagebox.showinfo("Пример загружен", "Загружен пример программы для суммы элементов массива")
    
    def load_convolution_example(self):
        """Загрузка примера программы для свертки"""
        # Программа для свертки двух массивов
        conv_code = """START:
    LOAD #0
    STORE R1     ; R1 = результат

    LOAD 0       ; ACC = размер массивов
    STORE R2     ; R2 = счетчик

    LOAD #1
    STORE R3     ; R3 = индекс массива A
    
    LOAD R2
    ADD #1
    STORE R4     ; R4 = индекс массива B

LOOP:
    LOAD R2      ; ACC = счетчик
    CMP #0       ; Сравнить с 0
    JZ END       ; Если счетчик == 0, закончить

    LOAD [R3]    ; Загрузка A[i]
    MUL [R4]     ; Умножение на B[i]
    ADD R1       ; Прибавление к итоговой сумме
    STORE R1     ; Обновляем результат

    INC R3
    INC R4
    DEC R2
    JMP LOOP

END:
    LOAD R1      ; ACC = результат
    HALT"""
        
        # Данные для свертки: размер 10, затем два массива по 10 элементов
        conv_data = """10 1 2 3 4 5 6 7 8 9 10 10 -9 8 -7 6 -5 4 -3 2 -1"""
        
        self.code_text.delete("1.0", tk.END)
        self.code_text.insert("1.0", conv_code)
        
        self.data_text.delete("1.0", tk.END)
        self.data_text.insert("1.0", conv_data)
        
        messagebox.showinfo("Пример загружен", "Загружен пример программы для свертки двух массивов")
    
def main():
    root = tk.Tk()
    app = Emulator(root)
    root.mainloop()

if __name__ == "__main__":

    main()
