"""CPU functionality"""

import sys

# Main CPU class
class CPU:
    def __init__(self):
        # Construct a new CPU
        # Initialize 8 registers
        self.R = [0] * 8
        # R7 is reserved as the stack pointer (SP)
        self.R[7] = 0xF4
        # Initizlize progrm counter
        # PC: Program Counter - address of the currently executing instruction
        self.PC = 0
        # Initialize Instruction Register
        # IR: contains a copy of the currently executing instruction
        self.IR = 0
        # Initialize Memory Address Register
        # MAR: holds the memory address we're reading or writing 
        self.MAR = 0
        # Initialize Memory Data Register
        # MDR: holds the value to write or just read
        self.MDR = 0
        # Initizlize Flags 
        # FL: the flags (register FL) holds the current flags status. These flags can change based on the operands given to the CMP opcode
        self.FL = 0
        # Initialize memory
        self.RAM = [0] * 256
        # Allow interrupts
        self.interrupts_enable = True
        # The system is not halted at startup
        self.HALT = False
        # The Program Counter is not set by an opcode by default
        self.PC_SET = False
        # Set registers for storing operands
        self.opA = 0
        self.opB = 0
        
    """
    Registers
    8 general-purpose 8-bit numeric registers R0-R7:
        R5 is reserved as the interrupt mask (IM)
        R6 is reserved as the interrupt status (IS)
        R7 is reserved as the stack pointer (SP)
    These registers only hold values between 0-255. After performing math on registers in the emulator, bitwise-AND the result with 0xFF (255) to keep the register values in that range.
    """
    # Named register methods
    def regOP(self, f, i):
        # Perform operation on register
        if 0 <= i and i < 8:
            self.R[i] = f(self.R[i]) & 255
            
    def register(self, num):
        # Get register associated with 8 bit input
        return self.R[num & 7]
    # Use @ property decorator: It's used to add functionality to the existing code. AKA metaprogramming, as a part of the program tries to modify another part of the program at compile time
    @property
    # R5 is reserved as the interrupt mask (IM)
    def IM(self):
        return self.R[5]
    def set_IM(self, value):
        self.R[5] = value
    @property
    # R6 is reserved as the interrupt status (IS)
    def IS(self):
        return self.R[6]
    def set_IS(self, value):
        self.R[6] = value
        
    """
    The flags (register FL) holds the current flags status. These flags can change based on the operands given to the CMP Compare opcode. 
    The register is made up of 8 bits. if a particular bit is set, that flag is "true".
    FL bits: 00000LGE
    L Less-than: during a CMP, set to 1 if registerA < register B, zero otherwise.
    G Greater-than: during a CMP, set to 1 if registerA > registerB, zero otherwise.
    E Equal: during a CMP, set to 1 if registerA == registerB, zero otherwise.
    """
    # MVP 1. Add the euql flag to your LS-8
    def flag(self, j):
        # Get jth flag
        i = j & 7
        return (self.FL & 2 ** i) >> i
    def set_flag(self, j, b):
        # Set jth flag to b
        i = j & 7
        # zero ith bit
        self.FL -= self.FL & 2 ** i
        if b:
            # set ith bit to 1
            self.FL += 2 ** i
    @property
    def L(self):
        # Less-than: during a CMP, set to 1 if registerA < registerB, zero otherwise
        return self.flag(2)
    def set_L(self, b):
        self.set_flag(2, b)
    @property
    def G(self):
        # Greater-than: during a CMP, set to 1 if registerA > registerB, zero otherwise
        return self.flag(1)
    def set_G(self, b):
        self.set_flag(1, b)
    @property
    def E(self):
        # Equal: during a CMP, set to 1 if registerA == registerB, zero otherwise
        return self.flag(0)
    def set_E(self, b):
        self.set_flag(0, b)


    # Named RAM methods
    @property
    def I7(self):
        return self.RAM[255]
    @property
    def I6(self):
        return self.RAM[254]
    @property
    def I5(self):
        return self.RAM[253]
    @property
    def I4(self):
        return self.RAM[252]
    @property
    def I3(self):
        return self.RAM[251]
    @property
    def I2(self):
        return self.RAM[250]
    @property
    def I1(self):
        return self.RAM[249]
    @property
    def I0(self):
        return self.RAM[248]
    
    @property
    def Key(self):
        return self.RAM[244]
    
    
    # Read and Write methods
    # MAR: Memory Address Register - holds the memory address we're readng or writing
    # MDR: Memory Data Register - holds the value to write or just read
    def ram_read(self):
        self.MDR = self.RAM[self.MAR]
        
    def ram_write(self, value, address):
        self.RAM[self.MAR] = self.MDR
        
    
    # Stack related methods
    def SP(self):
        return self.R[7]
    def set_SP(self, value):
        self.R[7] = value
        
    def pop(self):
        val = self.RAM[self.SP]
        self.RAM[self.SP] = 0
        self.set_SP((self.SP + 1) & 255)
        return val
    
    def push(self, val):
        self.set_SP((self.SP - 1) & 255)
        self.RAM[self.SP] = val & 255
        
    
    # Opcode Functions:
    def create_opcode_table(self):
        self.opcode_table = {}
        # NOP: No Operation - Do nothing for this instruction
        self.opcode_table[0x00] = self.NOP
        self.opcode_table[0x01] = self.HLT
        self.opcode_table[0x11] = self.RET
        self.opcode_table[0x13] = self.IRET
        self.opcode_table[0x45] = self.PUSH
        self.opcode_table[0x46] = self.POP
        self.opcode_table[0x47] = self.PRN
        self.opcode_table[0x50] = self.CALL
        self.opcode_table[0x52] = self.INT
        self.opcode_table[0x54] = self.JMP
        self.opcode_table[0x55] = self.JEQ
        self.opcode_table[0x56] = self.JNE
        self.opcode_table[0x57] = self.JGT
        self.opcode_table[0x58] = self.JLT
        self.opcode_table[0x59] = self.JLE
        self.opcode_table[0x5A] = self.JGE
        self.opcode_table[0x65] = self.INC
        self.opcode_table[0x66] = self.DEC
        self.opcode_table[0x69] = self.NOT
        self.opcode_table[0x82] = self.LDI
        self.opcode_table[0x83] = self.LD
        self.opcode_table[0x84] = self.ST
        self.opcode_table[0xA0] = self.ADD
        self.opcode_table[0xA1] = self.SUB
        self.opcode_table[0xA2] = self.MUL
        self.opcode_table[0xA3] = self.DIV
        self.opcode_table[0xA4] = self.MOD
        self.opcode_table[0xA7] = self.CMP
        self.opcode_table[0xA8] = self.AND
        self.opcode_table[0xAA] = self.OR
        self.opcode_table[0xAB] = self.XOR
        self.opcode_table[0xAC] = self.SHL
        self.opcode_table[0xAD] = self.SHR


    # MVP 1. Add the CMP instruction
    def CMP(self):
        # Compare the values in 2 registers
        # If they are equal, set the Equal E flag to 1, otherwise set it to 0
        # If reigsterA is < registerB, set the Less-Than L flag to 1, otherwise set it to 0
        # If reigsterA is > registerB, set the Greater-Than G flag to 1, otherwise set it to 0
        self.alu('CMP', self.opA, self.opB)
        
    # 2. Add the JMP instruction
    def JMP(self):
        # Jump the address stored in the given register
        self.PC_SET = True
        self.PC = self.R[self.opA & 7]
        
        
    # 4. Stretch: Add the ALU operations: `AND` `OR` `XOR` `NOT` `SHL` `SHR` `MOD`
    # ALU Table
    def create_ALU_table(self):
        self.ALU_table = {}
        # Increment (add 1 to) the value in the given register.
        self.ALU_table["INC"] = self.ALU_INC
        self.ALU_table["DEC"] = self.ALU_DEC
        self.ALU_table["NOT"] = self.ALU_NOT  # Stretch
        self.ALU_table["ADD"] = self.ALU_ADD  
        self.ALU_table["SUB"] = self.ALU_SUB
        self.ALU_table["MUL"] = self.ALU_MUL
        self.ALU_table["DIV"] = self.ALU_DIV
        self.ALU_table["MOD"] = self.ALU_MOD  # Stretch
        self.ALU_table["CMP"] = self.ALU_CMP
        self.ALU_table["AND"] = self.ALU_AND  # Stretch
        self.ALU_table["OR"] = self.ALU_OR  # Stretch
        self.ALU_table["XOR"] = self.ALU_XOR  # Stretch
        self.ALU_table["SHL"] = self.ALU_SHL  # Stretch
        self.ALU_table["SHR"] = self.ALU_SHR  # Stretch
        
    # 4. Stretch: Add the ALU operations: `AND` `OR` `XOR` `NOT` `SHL` `SHR` `MOD`
    def ALU_AND(self, reg_a, reg_b):
        self.R[reg_a] = self.R[reg_a] & self.R[reg_b]
        
    def ALU_OR(self, reg_a, reg_b):
        self.R[reg_a] = self.R[reg_a] | self.R[reg_b]
        
    def ALU_XOR(self, reg_a, reg_b):
        self.R[reg_a] = self.R[reg_a] ^ self.R[reg_b]
        
    # NOT register: Perform a bitwise-NOT on the value in a register, storing the result in the register
    def ALU_NOT(self, reg_a, reg_b):
        self.R[reg_a] = ~ self.R[reg_a]
        
    def ALU_SHL(self, reg_a, reg_b):
        self.R[reg_a] = (self.R[reg_a] << self.R[reg_b]) & 255

    def ALU_SHR(self, reg_a, reg_b):
        self.R[reg_a] = self.R[reg_a] >> self.R[reg_b]
    
    # MOD registerA registerB: Divide the value in the first register by the value in the second, storing the remainder of the result in registerA. If the value in the secod register is 0, the system should print an error message and halt.
    def ALU_MOD(self, reg_a, reg_b):
        if self.R[reg_b] == 0:
            raise Exception("Division by zero error")

        self.R[reg_a] = (self.R[reg_a] % self.R[reg_b]) & 255


    def alu(self, op, reg_a, reg_b):
        # Perform ALU operations
        do = self.ALU_table.get(op, None)
        if do is None:
            raise Exception("Unsupported ALU operation")
        do(reg_a, reg_b)


    def load(self, program):
        # Load a program into Memory
        self.create_opcode_table()
        self.create_ALU_table()

        address = 0

        for instruction in program:
            self.RAM[address] = instruction
            address += 1


    def step(self):
        """Run a single program step"""
        # Read byte at PC
        self.MAR = self.PC
        self.ram_read()
        self.IR = self.MDR

        # Read byte at PC+1
        self.MAR = (self.MAR + 1) & 255
        self.ram_read()
        self.opA = self.MDR

        # Read byte at PC+2
        self.MAR = (self.MAR + 1) & 255
        self.ram_read()
        self.opB = self.MDR

        # Set flag to see if the PC was set by an opcode
        self.PC_SET = False

        # Run opcode
        op = self.opcode_table.get(self.IR, None)
        if op is None:
            raise Exception(f'Undefined opcode {"0x{:02x}".format(self.IR)}.')
        op()

        # NOTE: The number of bytes an instruction uses can be determined from the
        # two high bits (bits 6-7) of the instruction opcode.
        if not self.PC_SET:
            high6 = (self.IR & 2 ** 6) >> 6
            high7 = (self.IR & 2 ** 7) >> 7

            if high6:
                self.PC = (self.PC + 2) & 255
            if high7:
                self.PC = (self.PC + 3) & 255


    def run(self):
        """
        Run the CPU
        command line: python3 ls8.py sctest.ls8 
        """
        # print("Running program...")

        while not self.HALT:
            self.step()
            # print("PC:", self.PC)
