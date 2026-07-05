import customtkinter as ctk
import time
from mips_engine import MIPSSimulator

ctk.set_appearance_mode("Light")  
ctk.set_default_color_theme("blue")

class MIPSSimulatorUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.sim = MIPSSimulator()
        self.current_line_index = 0  

        self.title("Simplified MIPS Simulator")
        self.geometry("1400x800")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_columnconfigure(2, weight=1) 

        self.build_top_bar()
        self.build_left_column()
        self.build_middle_column()
        self.build_right_column()

    def build_top_bar(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="ew")

        title_lbl = ctk.CTkLabel(top_frame, text="MIPS  SIMPLIFIED MIPS SIMULATOR", font=ctk.CTkFont(size=24, weight="bold"))
        title_lbl.pack(side="left")

        btn_run = ctk.CTkButton(top_frame, text="Run to End ⏩", command=self.run_to_end, fg_color="white", text_color="black", border_width=1)
        btn_run.pack(side="right", padx=5)
        
        btn_next = ctk.CTkButton(top_frame, text="▶ Next", command=self.step_instruction)
        btn_next.pack(side="right", padx=5)
        
        btn_reset = ctk.CTkButton(top_frame, text="↻ Reset", command=self.reset_simulator, fg_color="white", text_color="black", border_width=1)
        btn_reset.pack(side="right", padx=5)

    def build_left_column(self):
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")

        asm_lbl = ctk.CTkLabel(left_frame, text="1. ASSEMBLY CODE (User Input)", font=ctk.CTkFont(weight="bold"))
        asm_lbl.pack(anchor="w")
        
        self.code_box = ctk.CTkTextbox(left_frame, height=400, border_width=1)
        self.code_box.pack(fill="x", pady=(0, 20))
        
        # Load the comprehensive test code directly into the box
        sample_code = """addi $t0, $zero, 100
addi $t1, $zero, 42
addi $t2, $zero, -15
sw $t1, 0($t0)
sw $t2, 4($t0)
lw $s0, 0($t0)
lw $s1, 4($t0)
add $s2, $s0, $s1
sub $s3, $s0, $s1
and $s4, $s2, $s3
or $s5, $s2, $s3
slt $s6, $s1, $s0
slt $s7, $s0, $s1
sw $s2, 8($t0)"""
        self.code_box.insert("0.0", sample_code)

        pc_lbl = ctk.CTkLabel(left_frame, text="PROGRAM COUNTER (PC)", font=ctk.CTkFont(weight="bold"))
        pc_lbl.pack(anchor="w")
        
        pc_frame = ctk.CTkFrame(left_frame, border_width=1, fg_color="white")
        pc_frame.pack(fill="x", pady=(0, 20))
        
        self.pc_display = ctk.CTkLabel(pc_frame, text="0x00000000", text_color="green", font=ctk.CTkFont(size=18, weight="bold"))
        self.pc_display.pack(pady=10)

        status_lbl = ctk.CTkLabel(left_frame, text="CONTROL / STATUS", font=ctk.CTkFont(weight="bold"))
        status_lbl.pack(anchor="w")
        
        status_frame = ctk.CTkFrame(left_frame, border_width=1, fg_color="white")
        status_frame.pack(fill="x")
        self.status_display = ctk.CTkLabel(status_frame, text="Status: Ready", text_color="black")
        self.status_display.pack(anchor="w", padx=10, pady=5)

    def build_middle_column(self):
        mid_frame = ctk.CTkFrame(self, fg_color="transparent")
        mid_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        mc_lbl = ctk.CTkLabel(mid_frame, text="2. MACHINE CODE", font=ctk.CTkFont(weight="bold"))
        mc_lbl.pack(anchor="w")
        
        self.mc_box = ctk.CTkTextbox(mid_frame, height=400, border_width=1, font=ctk.CTkFont(family="Courier"))
        self.mc_box.pack(fill="x", pady=(0, 20))
        self.mc_box.insert("0.0", "Addr (Hex) |     Machine Code (Binary)     | Hex\n----------------------------------------------------\n")

        cur_lbl = ctk.CTkLabel(mid_frame, text="3. CURRENT INSTRUCTION", font=ctk.CTkFont(weight="bold"))
        cur_lbl.pack(anchor="w")
        
        self.cur_box = ctk.CTkTextbox(mid_frame, height=150, border_width=1)
        self.cur_box.pack(fill="x")

    def build_right_column(self):
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.grid(row=1, column=2, padx=(10, 20), pady=10, sticky="nsew")

        reg_lbl = ctk.CTkLabel(right_frame, text="4. REGISTERS (32)", font=ctk.CTkFont(weight="bold"))
        reg_lbl.pack(anchor="w")
        
        self.reg_frame = ctk.CTkScrollableFrame(right_frame, height=400, border_width=1, fg_color="white")
        self.reg_frame.pack(fill="x", pady=(0, 20))
        
        self.reg_labels = [] 
        self.idx_to_reg = {v: k for k, v in self.sim.reg_map.items()}

        for i in range(32):
            reg_name = self.idx_to_reg[i]
            reg_value = self.sim.registers[i]
            row = ctk.CTkFrame(self.reg_frame, fg_color="transparent")
            row.pack(fill="x", padx=5, pady=2)
            name_lbl = ctk.CTkLabel(row, text=reg_name, width=50, anchor="w", font=ctk.CTkFont(weight="bold"), text_color="black")
            name_lbl.pack(side="left")
            val_lbl = ctk.CTkLabel(row, text=f"0x{reg_value:08X}", text_color="black")
            val_lbl.pack(side="right")
            self.reg_labels.append(val_lbl)

        mem_lbl = ctk.CTkLabel(right_frame, text="5. DATA MEMORY", font=ctk.CTkFont(weight="bold"))
        mem_lbl.pack(anchor="w")
        
        self.mem_box = ctk.CTkTextbox(right_frame, height=150, border_width=1)
        self.mem_box.pack(fill="x")
        self.mem_box.insert("0.0", "Memory is empty.")

    def step_instruction(self):
        code_text = self.code_box.get("0.0", "end").strip()
        lines = code_text.split('\n')
        
        if self.current_line_index >= len(lines):
            self.status_display.configure(text="Status: Program Finished", text_color="red")
            return
            
        current_instruction = lines[self.current_line_index]
        
        if not current_instruction.strip() or current_instruction.strip().startswith('#'):
            self.current_line_index += 1
            if self.current_line_index < len(lines):
                self.step_instruction() 
            return

        bin_str, hex_str, type_str, breakdown = self.sim.get_machine_code(current_instruction)
        
        cur_text = f"Address:\t\t0x{self.sim.pc:08X}\n"
        cur_text += f"Assembly:\t\t{current_instruction}\n"
        cur_text += f"Machine Code (Bin):\t{bin_str}\n"
        cur_text += f"Machine Code (Hex):\t{hex_str}\n"
        cur_text += f"Type:\t\t{type_str}\n"
        cur_text += f"Operation:\t\t{breakdown}"
        
        self.cur_box.delete("0.0", "end")
        self.cur_box.insert("0.0", cur_text)
        
        mc_line = f"0x{self.sim.pc:08X} | {bin_str} | {hex_str}\n"
        self.mc_box.insert("end", mc_line)
        
        self.sim.execute_step(current_instruction)
        
        self.pc_display.configure(text=f"0x{self.sim.pc:08X}")
        
        for i in range(32):
            current_val = self.sim.registers[i]
            if current_val < 0:
                 current_val = current_val & 0xFFFFFFFF
            self.reg_labels[i].configure(text=f"0x{current_val:08X}")
            
        # Update Data Memory Box
        self.mem_box.delete("0.0", "end")
        if not self.sim.data_memory:
            self.mem_box.insert("0.0", "Memory is empty.")
        else:
            for addr, val in sorted(self.sim.data_memory.items()):
                display_val = val & 0xFFFFFFFF if val < 0 else val
                mem_line = f"0x{addr:08X}  ->  0x{display_val:08X}  ({val})\n"
                self.mem_box.insert("end", mem_line)

        self.status_display.configure(text=f"Status: Running | Executed: {self.current_line_index + 1}", text_color="black")
        self.current_line_index += 1

    def reset_simulator(self):
        self.sim.reset()
        self.current_line_index = 0
        
        self.pc_display.configure(text="0x00000000")
        self.status_display.configure(text="Status: Ready", text_color="black")
        
        self.mc_box.delete("0.0", "end")
        self.mc_box.insert("0.0", "Addr (Hex) |     Machine Code (Binary)     | Hex\n----------------------------------------------------\n")
        self.cur_box.delete("0.0", "end")
        
        for i in range(32):
            current_val = self.sim.registers[i]
            if current_val < 0:
                 current_val = current_val & 0xFFFFFFFF
            self.reg_labels[i].configure(text=f"0x{current_val:08X}")

        self.mem_box.delete("0.0", "end")
        self.mem_box.insert("0.0", "Memory is empty.")

    def run_to_end(self):
        code_text = self.code_box.get("0.0", "end").strip()
        lines = code_text.split('\n')
        
        # Loop through instructions
        while self.current_line_index < len(lines):
            self.step_instruction()
            self.update() # FORCES UI TO REFRESH IMMEDIATELY
            time.sleep(0.05) # Adds a tiny delay so you can watch the values change

if __name__ == "__main__":
    app = MIPSSimulatorUI()
    app.mainloop()
