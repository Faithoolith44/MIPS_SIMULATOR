import re

class MIPSSimulator:
    def __init__(self):
        self.reset() 

    def reset(self):
        """Clears all registers, memory, and resets the Program Counter."""
        self.registers = [0] * 32
        self.registers[29] = 0x7FFFFFFC # Initialize Stack Pointer ($sp)
        self.pc = 0x00000000
        self.data_memory = {} 
        
        # Maps string names to integer indices
        self.reg_map = {
            '$zero': 0, '$at': 1, '$v0': 2, '$v1': 3, 
            '$a0': 4, '$a1': 5, '$a2': 6, '$a3': 7,
            '$t0': 8, '$t1': 9, '$t2': 10, '$t3': 11,
            '$t4': 12, '$t5': 13, '$t6': 14, '$t7': 15,
            '$s0': 16, '$s1': 17, '$s2': 18, '$s3': 19,
            '$s4': 20, '$s5': 21, '$s6': 22, '$s7': 23,
            '$t8': 24, '$t9': 25, '$k0': 26, '$k1': 27,
            '$gp': 28, '$sp': 29, '$fp': 30, '$ra': 31
        }

    def parse_instruction(self, line):
        line = line.split('#')[0].strip() 
        if not line:
            return None
        tokens = re.split(r'[,\s]+', line)
        return [t for t in tokens if t] 

    def get_machine_code(self, line):
        tokens = self.parse_instruction(line)
        if not tokens: return "", "", "", ""
        
        opcode_str = tokens[0]
        
        r_type_functs = {'add': 32, 'sub': 34, 'and': 36, 'or': 37, 'slt': 42}
        i_type_opcodes = {'addi': 8, 'lw': 35, 'sw': 43}
        
        binary = ""
        type_str = ""
        breakdown = ""
        
        if opcode_str in r_type_functs:
            type_str = "R-type"
            rd = self.reg_map[tokens[1]]
            rs = self.reg_map[tokens[2]]
            rt = self.reg_map[tokens[3]]
            funct = r_type_functs[opcode_str]
            binary = f"000000{rs:05b}{rt:05b}{rd:05b}00000{funct:06b}"
            breakdown = f"{tokens[1]} = {tokens[2]} {opcode_str} {tokens[3]}"
            
        elif opcode_str in i_type_opcodes:
            type_str = "I-type"
            op = i_type_opcodes[opcode_str]
            if opcode_str == 'addi':
                rt = self.reg_map[tokens[1]]
                rs = self.reg_map[tokens[2]]
                imm = int(tokens[3]) & 0xFFFF 
                binary = f"{op:06b}{rs:05b}{rt:05b}{imm:016b}"
                breakdown = f"{tokens[1]} = {tokens[2]} + {tokens[3]}"
            elif opcode_str in ['lw', 'sw']:
                rt = self.reg_map[tokens[1]]
                match = re.match(r'(-?\d+)\((.+)\)', tokens[2])
                imm = int(match.group(1)) & 0xFFFF
                rs = self.reg_map[match.group(2)]
                binary = f"{op:06b}{rs:05b}{rt:05b}{imm:016b}"
                breakdown = f"Mem[{match.group(2)} + {match.group(1)}] {'->' if opcode_str=='lw' else '<-'} {tokens[1]}"
                
        if binary:
            hex_str = f"0x{int(binary, 2):08X}"
            if type_str == "R-type":
                bin_display = f"{binary[0:6]} {binary[6:11]} {binary[11:16]} {binary[16:21]} {binary[21:26]} {binary[26:32]}"
            else:
                bin_display = f"{binary[0:6]} {binary[6:11]} {binary[11:16]} {binary[16:32]}"
                
            return bin_display, hex_str, type_str, breakdown
            
        return "", "", "", ""

    def execute_step(self, instruction_line):
        tokens = self.parse_instruction(instruction_line)
        if not tokens: return

        opcode = tokens[0]

        if opcode == "addi":
            rt = self.reg_map[tokens[1]]
            rs = self.reg_map[tokens[2]]
            imm = int(tokens[3])
            self.registers[rt] = self.registers[rs] + imm

        elif opcode in ["lw", "sw"]:
            rt = self.reg_map[tokens[1]]
            match = re.match(r'(-?\d+)\((.+)\)', tokens[2])
            offset = int(match.group(1))
            rs = self.reg_map[match.group(2)]
            address = self.registers[rs] + offset
            if opcode == "lw":
                self.registers[rt] = self.data_memory.get(address, 0)
            elif opcode == "sw":
                self.data_memory[address] = self.registers[rt]

        elif opcode in ["add", "sub", "and", "or", "slt"]:
            rd = self.reg_map[tokens[1]]
            rs = self.reg_map[tokens[2]]
            rt = self.reg_map[tokens[3]]

            if opcode == "add":
                self.registers[rd] = self.registers[rs] + self.registers[rt]
            elif opcode == "sub":
                self.registers[rd] = self.registers[rs] - self.registers[rt]
            elif opcode == "and":
                self.registers[rd] = self.registers[rs] & self.registers[rt]
            elif opcode == "or":
                self.registers[rd] = self.registers[rs] | self.registers[rt]
            elif opcode == "slt":
                self.registers[rd] = 1 if self.registers[rs] < self.registers[rt] else 0

        self.registers[0] = 0
        self.pc += 4
