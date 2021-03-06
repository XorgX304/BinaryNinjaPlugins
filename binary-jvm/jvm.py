import struct
import traceback
import os

from binaryninja import *
            
InstructionNames = [
'nop', 'aconst_null', 'iconst_m1', 'iconst_0', 'iconst_1', 'iconst_2', 'iconst_3', 'iconst_4', 
'iconst_5', 'lconst_0', 'lconst_1', 'fconst_0', 'fconst_1', 'fconst_2', 'dconst_0', 'dconst_1', 
'bipush', 'sipush', 'ldc', 'ldc_w', 'ldc2_w', 'iload', 'lload', 'fload', 
'dload', 'aload', 'iload_0', 'iload_1', 'iload_2', 'iload_3', 'lload_0', 'lload_1', 
'lload_2', 'lload_3', 'fload_0', 'fload_1', 'fload_2', 'fload_3', 'dload_0', 'dload_1', 
'dload_2', 'dload_3', 'aload_0', 'aload_1', 'aload_2', 'aload_3', 'iaload', 'laload', 
'faload', 'daload', 'aaload', 'baload', 'caload', 'saload', 'istore', 'lstore', 
'fstore', 'dstore', 'astore', 'istore_0', 'istore_1', 'istore_2', 'istore_3', 'lstore_0', 
'lstore_1', 'lstore_2', 'lstore_3', 'fstore_0', 'fstore_1', 'fstore_2', 'fstore_3', 'dstore_0', 
'dstore_1', 'dstore_2', 'dstore_3', 'astore_0', 'astore_1', 'astore_2', 'astore_3', 'iastore', 
'lastore', 'fastore', 'dastore', 'aastore', 'bastore', 'castore', 'sastore', 'pop', 
'pop2', 'dup', 'dup_x1', 'dup_x2', 'dup2', 'dup2_x1', 'dup2_x2', 'swap', 
'iadd', 'ladd', 'fadd', 'dadd', 'isub', 'lsub', 'fsub', 'dsub', 
'imul', 'lmul', 'fmul', 'dmul', 'idiv', 'ldiv', 'fdiv', 'ddiv', 
'irem', 'lrem', 'frem', 'drem', 'ineg', 'lneg', 'fneg', 'dneg', 
'ishl', 'lshl', 'ishr', 'lshr', 'iushr', 'lushr', 'iand', 'land', 
'ior', 'lor', 'ixor', 'lxor', 'iinc', 'i2l', 'i2f', 'i2d', 
'l2i', 'l2f', 'l2d', 'f2i', 'f2l', 'f2d', 'd2i', 'd2l', 
'd2f', 'i2b', 'i2c', 'i2s', 'lcmp', 'fcmpl', 'fcmpg', 'dcmpl', 
'dcmpg', 'ifeq', 'ifne', 'iflt', 'ifge', 'ifgt', 'ifle', 'if_icmpeq', 
'if_icmpne', 'if_icmplt', 'if_icmpge', 'if_icmpgt', 'if_icmple', 'if_acmpeq', 'if_acmpne', 'goto', 
'jsr', 'ret', 'tableswitch', 'lookupswitch', 'ireturn', 'lreturn', 'freturn', 'dreturn', 
'areturn', 'return', 'getstatic', 'putstatic', 'getfield', 'putfield', 'invokevirtual', 'invokespecial', 
'invokestatic', 'invokeinterface', 'invokedynamic', 'new', 'newarray', 'anewarray', 'arraylength', 'athrow', 
'checkcast', 'instanceof', 'monitorenter', 'monitorexit', 'wide', 'multianewarray', 'ifnull', 'ifnonnull', 
'goto_w', 'jsr_w', None, None, None, None, None, None, 
None, None, None, None, None, None, None, None, 
None, None, None, None, None, None, None, None, 
None, None, None, None, None, None, None, None, 
None, None, None, None, None, None, None, None, 
None, None, None, None, None, None, None, None, 
None, None, None, None, None, None, None, None]


PSEUDOMEMORY_PRIMITIVES = 0xE0000000 #Pointer to not existing memory containing symbols with names of the primitives these fields represent
PSEUDOMEMORY_TABLE      = 0xF0000000 #Pointer to not existing memory containing symbols with string content of contant table entries

InstructionLengths = [0,1,2,1,2,2,12,8,2,4,4,1,3,3,4,1]

TYPE_NONE   = 0
TYPE_BYTE   = 1
TYPE_2BYTE  = 2
TYPE_INDEX  = 3
TYPE_IINC   = 4
TYPE_2BRANCH = 5
TYPE_TABLESWITCH = 6
TYPE_LOOKUPSWITCH = 7
TYPE_2INDEX = 8
TYPE_INTERFACE = 9
TYPE_DYNAMIC = 10
TYPE_ATYPE = 11
TYPE_WIDE = 12
TYPE_MULTIARRAY = 13
TYPE_4BRANCH = 14
TYPE_LDC = 15

InstructionFormat = [
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_BYTE, TYPE_2BYTE, TYPE_LDC, TYPE_2INDEX, TYPE_2INDEX, TYPE_INDEX, TYPE_INDEX, TYPE_INDEX, 
TYPE_INDEX, TYPE_INDEX, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_INDEX, TYPE_INDEX, 
TYPE_INDEX, TYPE_INDEX, TYPE_INDEX, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_IINC, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_2BRANCH ,TYPE_2BRANCH, TYPE_2BRANCH, TYPE_2BRANCH, TYPE_2BRANCH, TYPE_2BRANCH, TYPE_2BRANCH, 
TYPE_2BRANCH, TYPE_2BRANCH, TYPE_2BRANCH, TYPE_2BRANCH, TYPE_2BRANCH, TYPE_2BRANCH, TYPE_2BRANCH, TYPE_2BRANCH, 
TYPE_2BRANCH, TYPE_INDEX, TYPE_TABLESWITCH, TYPE_LOOKUPSWITCH, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_2INDEX, TYPE_2INDEX, TYPE_2INDEX, TYPE_2INDEX, TYPE_2INDEX, TYPE_2INDEX, 
TYPE_2INDEX, TYPE_INTERFACE, TYPE_DYNAMIC, TYPE_2INDEX, TYPE_ATYPE, TYPE_2INDEX, TYPE_NONE, TYPE_NONE, 
TYPE_2INDEX, TYPE_2INDEX, TYPE_NONE, TYPE_NONE, TYPE_WIDE, TYPE_MULTIARRAY, TYPE_2BRANCH, TYPE_2BRANCH, 
TYPE_4BRANCH, TYPE_4BRANCH, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, 
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE,
TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE]

"""
def getPoolEntry(il, value):
    return il.const(4, value)
    
def loadLocal(il, index, size):
    return il.const(4, 0)
    
def storeLocal(il, index, size):
    return il.const(4, 0)

InstructionIL = {
    "nop":         lambda il, operand: il.nop(),
    "aconst_null": lambda il, operand: il.push(4, il.const(4,0)),
    "iconst_m1":   lambda il, operand: il.push(4, il.const(4,-1)),
    "iconst_0":    lambda il, operand: il.push(4, il.const(4,0)),
    "iconst_1":    lambda il, operand: il.push(4, il.const(4,1)),
    "iconst_2":    lambda il, operand: il.push(4, il.const(4,2)),
    "iconst_3":    lambda il, operand: il.push(4, il.const(4,3)),
    "iconst_4":    lambda il, operand: il.push(4, il.const(4,4)),
    "iconst_5":    lambda il, operand: il.push(4, il.const(4,5)),
    "lconst_0":    lambda il, operand: il.push(8, il.const(8,0)),
    "lconst_1":    lambda il, operand: il.push(8, il.const(8,1)),
    "fconst_0":    lambda il, operand: il.push(4, il.float_const_single(0.0)),
    "fconst_1":    lambda il, operand: il.push(4, il.float_const_single(1.0)),
    "fconst_2":    lambda il, operand: il.push(4, il.float_const_single(2.0)),
    "dconst_0":    lambda il, operand: il.push(8, il.float_const_double(0.0)),
    "dconst_1":    lambda il, operand: il.push(8, il.float_const_double(1.0)),
    "bipush":      lambda il, operand: il.push(4, il.const(4,operand)),
    "sipush":      lambda il, operand: il.push(4, il.const(4,operand)),
    "ldc":         lambda il, operand: il.push(4, getPoolEntry(il,operand)),
    "ldc_w":       lambda il, operand: il.push(4, getPoolEntry(il,operand)),
    "ldc2_w":      lambda il, operand: [il.push(4, getPoolEntry(il,operand+1)),il.push(4, getPoolEntry(il,operand))],
    "iload":       lambda il, operand: il.push(4, loadLocal(il,operand,4)),
    "lload":       lambda il, operand: il.push(8, loadLocal(il,operand,8)),
    "fload":       lambda il, operand: il.push(4, loadLocal(il,operand,4)),
    "dload":       lambda il, operand: il.push(8, loadLocal(il,operand,8)),
    "aload":       lambda il, operand: il.push(4, loadLocal(il,operand,4)),
    "iload_0":     lambda il, operand: il.push(4, loadLocal(il,0,4)),
    "iload_1":     lambda il, operand: il.push(4, loadLocal(il,1,4)),
    "iload_2":     lambda il, operand: il.push(4, loadLocal(il,2,4)),
    "iload_3":     lambda il, operand: il.push(4, loadLocal(il,3,4)),
    "lload_0":     lambda il, operand: il.push(8, loadLocal(il,0,8)),
    "lload_1":     lambda il, operand: il.push(8, loadLocal(il,2,8)),
    "lload_2":     lambda il, operand: il.push(8, loadLocal(il,4,8)),
    "lload_3":     lambda il, operand: il.push(8, loadLocal(il,6,8)),
    "fload_0":     lambda il, operand: il.push(4, loadLocal(il,0,4)),
    "fload_1":     lambda il, operand: il.push(4, loadLocal(il,1,4)),
    "fload_2":     lambda il, operand: il.push(4, loadLocal(il,2,4)),
    "fload_3":     lambda il, operand: il.push(4, loadLocal(il,3,4)),
    "dload_0":     lambda il, operand: il.push(8, loadLocal(il,0,8)),
    "dload_1":     lambda il, operand: il.push(8, loadLocal(il,2,8)),
    "dload_2":     lambda il, operand: il.push(8, loadLocal(il,4,8)),
    "dload_3":     lambda il, operand: il.push(8, loadLocal(il,6,8)),
    "aload_0":     lambda il, operand: il.push(4, loadLocal(il,0,4)),
    "aload_1":     lambda il, operand: il.push(4, loadLocal(il,1,4)),
    "aload_2":     lambda il, operand: il.push(4, loadLocal(il,2,4)),
    "aload_3":     lambda il, operand: il.push(4, loadLocal(il,3,4)),
    #ialod
}
"""
OperandTokens = [
	lambda self,value: [],    # TYPE_NONE
	lambda self,value: [InstructionTextToken(InstructionTextTokenType.IntegerToken, "%d" % value)],  # TYPE_BYTE
	lambda self,value: [InstructionTextToken(InstructionTextTokenType.IntegerToken, "%d" % value)],  # TYPE_2BYTE
	lambda self,value: [InstructionTextToken(InstructionTextTokenType.IntegerToken, "var_%d" % value)],  # TYPE_INDEX
    lambda self,value: [InstructionTextToken(InstructionTextTokenType.IntegerToken, "var_%d" % value[0]), InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "), InstructionTextToken(InstructionTextTokenType.IntegerToken, "%d" % value[1])],  # TYPE_IINC
    lambda self,value: [InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, "0x%.2x" % value, value)],  # TYPE_2BRANCH
    lambda self,value: [],  # TYPE_TABLESWITCH
    lambda self,value: [],  # TYPE_LOOKUPSWITCH
    lambda self,value: [InstructionTextToken(InstructionTextTokenType.IntegerToken, "Pool@%d" % value, value+PSEUDOMEMORY_TABLE)],  # TYPE_2INDEX
    lambda self,value: [InstructionTextToken(InstructionTextTokenType.IntegerToken, "Pool@%d" % value[0],value[0]+PSEUDOMEMORY_TABLE)],  # TYPE_INTERFACE
    lambda self,value: [InstructionTextToken(InstructionTextTokenType.IntegerToken, "Pool@%d" % value[0],value[0]+PSEUDOMEMORY_TABLE)],  # TYPE_DYNAMIC
    lambda self,value: [InstructionTextToken(InstructionTextTokenType.IntegerToken, "A@0x%.2x" % value,value+PSEUDOMEMORY_PRIMITIVES)],  # TYPE_ATYPE
    lambda self,value: [InstructionTextToken(InstructionTextTokenType.TextToken, "%s " % InstructionNames[value[0]]), InstructionTextToken(InstructionTextTokenType.IntegerToken, "var_%d" % value[1])] if len(value) == 2 else [InstructionTextToken(InstructionTextTokenType.TextToken, "%s " % InstructionNames[value[0]]), InstructionTextToken(InstructionTextTokenType.IntegerToken, "var_@%d" % value[1]), InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "), InstructionTextToken(InstructionTextTokenType.IntegerToken, "%d" % value[2])],  # TYPE_WIDE
    lambda self,value: [InstructionTextToken(InstructionTextTokenType.IntegerToken, "Pool@%d" % value[0],value[0]+PSEUDOMEMORY_TABLE), InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "), InstructionTextToken(InstructionTextTokenType.IntegerToken, "$%.1x" % value[1])],  # TYPE_MULTIARRAY
    lambda self,value: [InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, "0x%.4x" % value, value)],   # TYPE_4BRANCH
    lambda self,value: [InstructionTextToken(InstructionTextTokenType.IntegerToken, "Pool@%d" % value,value+PSEUDOMEMORY_TABLE)]  # TYPE_LDC
]

def decode_instruction(data, addr):
        if len(data) < 1:
            return None, None, None, None
        opcode = ord(data[0])
        instr = InstructionNames[opcode]
        if instr is None:
            return None, None, None, None

        operand = InstructionFormat[opcode]
        length = 1 + InstructionLengths[operand]
        if len(data) < length:
            return None, None, None, None

        if operand == TYPE_NONE:
            value = None
        elif operand == TYPE_BYTE:
            value = struct.unpack(">b", data[1:2])[0]
        elif operand == TYPE_2BYTE:
            value = struct.unpack(">h", data[1:3])[0]
        elif operand == TYPE_INDEX:
            value = struct.unpack(">B", data[1:2])[0]
        elif operand == TYPE_LDC:
            value = struct.unpack(">B", data[1:2])[0]
        elif operand == TYPE_2INDEX:
            value = struct.unpack(">H", data[1:3])[0]
        elif operand == TYPE_IINC:
            value = struct.unpack(">Bb", data[1:3])
        elif operand == TYPE_2BRANCH:
            value = addr+struct.unpack(">h", data[1:3])[0]
        elif operand == TYPE_4BRANCH:
            value = addr+struct.unpack(">i", data[1:5])[0]
        elif operand == TYPE_TABLESWITCH:
            padding = 4-((addr+1)%4)
            default,lowbyte,highbyte = struct.unpack(">iII", data[1+padding:13+padding])
            default += addr
            offsets = []
            length = (padding+12+1+(highbyte-lowbyte+1)*4)
            if len(data) < length:
                return None, None, None, length
            for i in range(highbyte-lowbyte+1):
                offsets.append((lowbyte+i, addr+struct.unpack(">i", data[13+i*4+padding:17+i*4+padding])[0]))
            value = (default,lowbyte, highbyte, offsets)
        elif operand == TYPE_LOOKUPSWITCH:
            padding = 4-((addr+1)%4)
   
            default,npairs = struct.unpack(">iI", data[1+padding:9+padding])
            default += addr
            offsets = []
            length = (padding+8+1+npairs*8)
            if len(data) < length:
                return None, None, None, length
            for i in range(npairs):
                offsets.append((struct.unpack(">I", data[9+i*8+padding:13+i*8+padding])[0], addr+struct.unpack(">i", data[13+i*8+padding:17+i*8+padding])[0]))
            value = (default,npairs,offsets)
        elif operand == TYPE_INTERFACE:
            index = struct.unpack(">H", data[1:3])[0]
            real_addr = index
            value = (real_addr, index)
        elif operand == TYPE_DYNAMIC:
            index = struct.unpack(">H", data[1:3])[0]
            real_addr = index
            value = (real_addr, index)
        elif operand == TYPE_ATYPE:
            value = struct.unpack(">B", data[1:2])[0]
        elif operand == TYPE_WIDE:
            op2 = data[1]
            if op2 == 0x84: #iinc
                length = 5
                if len(data) < length:
                    return None, None, None, length
                value = struct.unpack(">BHh", data[1:7])
            else:
                value = struct.unpack(">BH", data[1:4])
        elif operand == TYPE_MULTIARRAY:
            value = struct.unpack(">HB", data[1:4])
        else:
            value = None
        return instr, operand, length, value
        
class JVM(Architecture):
    
    name = "JVM"
    address_size = 2
    default_int_size = 1
    max_instr_length = 255
    regs = { "s": RegisterInfo("s", 1) }
    stack_pointer = "s"
    endianness = Endianness.BigEndian

    def perform_get_instruction_info(self, data, addr):
        instr, operand, length, value = decode_instruction(data, addr)
        if instr is None:
            return None

        result = InstructionInfo()
        result.length = length
        if instr in ["jsr", "jsr_w","goto","goto_w"]:
            result.add_branch(BranchType.UnconditionalBranch, value)
        elif instr in ["invokestatic","invokedynamic"]:
            #result.add_branch(BranchType.CallDestination, value[0])
            pass
        elif instr in ["invokevirtual", "invokespecial"]:
#           result.add_branch(BranchType.IndirectBranch)
            pass
        elif instr == "invokeinterface":
 #           result.add_branch(BranchType.IndirectBranch)
            pass
        elif instr == "tableswitch":
            result.add_branch(BranchType.IndirectBranch)
            #result.add_branch(BranchType.FalseBranch, value[0])
            #for p in value[3]:
            #    result.add_branch(BranchType.UnconditionalBranch, p[1])
        elif instr == "lookupswitch":
            result.add_branch(BranchType.IndirectBranch)
            #result.add_branch(BranchType.FalseBranch, value[0])
            #for p in value[2]:
            #    result.add_branch(BranchType.UnconditionalBranch, p[1])
        elif instr in ["ret", "ireturn","lreturn","freturn","dreturn","areturn","return"]:
            result.add_branch(BranchType.FunctionReturn)
        elif instr in ["ifnull", "ifnonnull","if_acmpne","if_acmpeq","if_icmple","if_icmpgt","if_icmpge","if_icmplt","if_icmpne","if_icmpeq","ifle","ifgt","ifge","iflt","ifne","ifeq"]:
            result.add_branch(BranchType.TrueBranch, value)
            result.add_branch(BranchType.FalseBranch, addr + length)
            
        return result

    def perform_get_instruction_text(self, data, addr):
        instr, operand, length, value = decode_instruction(data, addr)
        if instr is None:
            return None
        tokens = []
        tokens.append(InstructionTextToken(InstructionTextTokenType.TextToken, "%-14s " % instr))
        tokens += OperandTokens[operand](self,value)
        return tokens, length
        
    def perform_get_instruction_low_level_il(self, data, addr, il):
        instr, operand, length, value = decode_instruction(data, addr)
        if instr is None:
            return None
            
        """if InstructionIL.get(instr) is not None:
            inst = InstructionIL[instr](il, operand)
            if isinstance(inst, list):
                for i in inst:
                    il.append(i)
            elif inst is not None:
                il.append(inst)
        else:
            pass"""
        il.append(il.unimplemented())
        return length
        
    def convert_to_nop(self, data, addr):
        instr, operand, length, value = decode_instruction(data, addr)
        if instr == None:
            return None
        if instr.startswith("if_"):
            return "\x58" + ("\x00" * (len(data)-1)) #pop2
        elif instr.startswith("if"):
            return "\x57" + ("\x00" * (len(data)-1)) #pop
        return "\x00" * len(data)

    def is_jump(self,data, addr):
        instr, operand, length, value = decode_instruction(data, addr)
        if instr != None and "if" in instr:
            return True
        return False
        
    def is_never_branch_patch_available(self, data, addr):
        return self.is_jump(data, addr) or data[0] == "\xc8" or data[0] == "\xc9" or data[0] == "\xa7" or data[0] == "\xa8"
        
    def is_invert_branch_patch_available(self, data, addr):
        return self.is_jump(data, addr)
        
    def is_always_branch_patch_available(self, data, addr):
        return self.is_jump(data, addr)
        
    def invert_branch(self, data, addr):
        if data[0] == "\xa5": return "\xa6"+data[1:] #if_acmpeq -> if_acmpne
        if data[0] == "\xa6": return "\xa5"+data[1:] #if_acmpne -> if_acmpeq
        if data[0] == "\x9f": return "\xa0"+data[1:] #if_icmpeq -> if_icmpne
        if data[0] == "\xa2": return "\xa1"+data[1:] #if_icmpge -> if_icmplt
        if data[0] == "\xa3": return "\xa4"+data[1:] #if_icmpgt -> if_icmple
        if data[0] == "\xa4": return "\xa3"+data[1:] #if_icmple -> if_icmpgt
        if data[0] == "\xa1": return "\xa2"+data[1:] #if_icmplt -> if_icmpge
        if data[0] == "\xa0": return "\x9f"+data[1:] #if_icmpne -> if_icmpeq
        if data[0] == "\x99": return "\x9a"+data[1:] #ifeq      -> ifne
        if data[0] == "\x9c": return "\x9b"+data[1:] #ifge      -> iflt
        if data[0] == "\x9d": return "\x9e"+data[1:] #ifgt      -> ifle
        if data[0] == "\x9e": return "\x9d"+data[1:] #ifle      -> ifgt
        if data[0] == "\x9b": return "\x9c"+data[1:] #iflt      -> ifge
        if data[0] == "\x9a": return "\x99"+data[1:] #ifne      -> ifeq
        if data[0] == "\xc7": return "\xc6"+data[1:] #ifnotnull -> ifnull
        if data[0] == "\xc6": return "\xc7"+data[1:] #ifnull    -> ifnotnull
        return None
        
    #beaware, considering this doesn't remove the last push and will most likely will lead to stack corruption!
    def always_branch(self, data, addr):
        return "\xa7"+data[1:] #goto
        
    def appendPacked(self, format, s, sub=0, mode=0):
        try:
            value = 0
            if s.startswith("0x") or s.startswith("0X"):
                value = int(s,16)
            elif s.endswith("h") or s.endswith("H"):
                value = int(s[:-1],16)
            elif any(c.isalpha() for c in s): 
                value = int(s,16)
            else:
                value = int(s)
            value -= sub
            if mode == 1:
                value &= 0x0FFFFFF
            return struct.pack(format, value)
        except Exception as e:
            print e
            return None
        
    def assemble(self, code, addr=0):
        instr = code.replace('\n',";").replace(','," ").split(';')
        for i in range(len(instr)): instr[i] = (" ".join(instr[i].split())).lower().split(" ")   
        data = []
        for inst in instr:
            if len(inst) < 1: continue
            if len(inst[0]) < 1: continue
            instIndex = -1
            for i,names in enumerate(InstructionNames):
                if inst[0] == names:
                    instIndex = i
                    break
            if inst[0] == "db":
                parameter = self.appendPacked(">B",inst[1])
                if parameter != None: data.append(parameter)
                else:                 return None
                continue
            elif inst[0] == "dw":
                parameter = self.appendPacked(">H",inst[1])
                if parameter != None: data.append(parameter)
                else:                 return None
                continue
            elif inst[0] == "dd":
                parameter = self.appendPacked(">I",inst[1])
                if parameter != None: data.append(parameter)
                else:                 return None
                continue
            elif inst[0] == "dq":
                parameter = self.appendPacked(">Q",inst[1])
                if parameter != None: data.append(parameter)
                else:                 return None
                continue
            
            if instIndex == -1:
                return None
            if InstructionFormat[instIndex] == TYPE_NONE: 
                data.append(chr(instIndex))
            elif InstructionFormat[instIndex] == TYPE_BYTE and len(inst) >= 2: 
                data.append(chr(instIndex))
                parameter = self.appendPacked(">b",inst[1])
                if parameter != None: data.append(parameter)
                else:                 return None
            elif InstructionFormat[instIndex] == TYPE_2BYTE and len(inst) >= 2: 
                data.append(chr(instIndex))
                parameter = self.appendPacked(">h",inst[1])
                if parameter != None: data.append(parameter)
                else:                 return None
            elif (InstructionFormat[instIndex] == TYPE_INDEX or InstructionFormat[instIndex] == TYPE_LDC) and len(inst) >= 2: 
                data.append(chr(instIndex))
                parameter = self.appendPacked(">B",inst[1], mode=1)
                if parameter != None: data.append(parameter)
                else:                 return None
            elif InstructionFormat[instIndex] == TYPE_2INDEX and len(inst) >= 2: 
                data.append(chr(instIndex))
                parameter = self.appendPacked(">H",inst[1], mode=1)
                if parameter != None: data.append(parameter)
                else:                 return None
            elif InstructionFormat[instIndex] == TYPE_IINC and len(inst) >= 3: 
                data.append(chr(instIndex))
                parameter = self.appendPacked(">B",inst[1])
                if parameter != None: data.append(parameter)
                else:                 return None
                parameter = self.appendPacked(">b",inst[2])
                if parameter != None: data.append(parameter)
                else:                 return None
            elif InstructionFormat[instIndex] == TYPE_2BRANCH and len(inst) >= 2: 
                data.append(chr(instIndex))
                parameter = self.appendPacked(">h",inst[1], sub=addr)
                if parameter != None: data.append(parameter)
                else:                 return None
            elif InstructionFormat[instIndex] == TYPE_4BRANCH and len(inst) >= 2: 
                data.append(chr(instIndex))
                parameter = self.appendPacked(">i",inst[1], sub=addr)
                if parameter != None: data.append(parameter)
                else:                 return None
            elif InstructionFormat[instIndex] == TYPE_INTERFACE and len(inst) >= 2: 
                data.append(chr(instIndex))
                parameter = self.appendPacked(">H",inst[1], mode=1)
                if parameter != None: data.append(parameter)
                else:                 return None
                data.append("\x00") #count
                data.append("\x00")
            elif InstructionFormat[instIndex] == TYPE_DYNAMIC and len(inst) >= 2: 
                data.append(chr(instIndex))
                parameter = self.appendPacked(">H",inst[1], mode=1)
                if parameter != None: data.append(parameter)
                else:                 return None
                data.append("\x00")
                data.append("\x00")
            elif InstructionFormat[instIndex] == TYPE_ATYPE and len(inst) >= 2: 
                data.append(chr(instIndex))
                parameter = self.appendPacked(">B",inst[1], mode=1)
                if parameter != None: data.append(parameter)
                else:                 return None
            elif InstructionFormat[instIndex] == TYPE_MULTIARRAY  and len(inst) >= 3:
                data.append(chr(instIndex))
                parameter = self.appendPacked(">H",inst[1], mode=1)
                if parameter != None: data.append(parameter)
                else:                 return None
                parameter = self.appendPacked(">B",inst[2])
                if parameter != None: data.append(parameter)
                else:                 return None
            else: 
                return None
        
        if len(data) == 0: return None
        
        data = (''.join(data), '')
        return data

        
#super class for all jvm structures
class JVMStructure():
    def __init__(self, cR):
        self.classReader = cR
        self.structure = Structure() # a binary ninja structure
        self.structure.packed = True # don't align structure
        self.type      = None
        
    """
    def resultingType(self):
        if self.type == None:
            self.type = Type.structure_type(self.structure)
        return self.type
    """
        
    def resultingType(self):
        if self.type == None:
            oid = str(self.__class__.__name__)
            self.type = Type.structure_type(self.structure)
            pos = 0
            while True: # loop all possible structre names until one is free or equal to the current one
                if pos == 0:
                    id = oid
                else:
                    id = oid+"("+str(pos)+")"       
                alr = self.classReader.view.get_type_by_name(id)   
                if(alr != None):
                    if(self.type == alr or (self.type.structure != None and alr.structure != None and str(self.type.structure.members) == str(alr.structure.members))):
                        break
                    else:
                        pos += 1
                        continue
                else:
                    self.classReader.view.define_type(Type.generate_auto_type_id("source", id), id, self.type)
                    break
            self.type = Type.named_type_from_type(id, self.type)
        return  self.type
    def readByte(self, name=''):
        self.structure.append(Type.int(1,False,"u1"),name)
        return self.classReader.readByte()
        
    def readArray(self, amount, name='', aType = Type.int(1,False)):
        value = ""
        self.structure.append(Type.array(aType,amount),name)
        for i in range(amount):
            value += chr(self.classReader.readByte())
        return value
        
    def readShort(self, name=''):
        self.structure.append(Type.int(2,False,"u2"),name)
        return self.classReader.readShort()   
        
    def readInt(self, name=''):
        self.structure.append(Type.int(4,False,"u4"),name)
        return self.classReader.readInt()
        
    def readLong(self, name=''):
        self.structure.append(Type.int(8,False,"u8"),name)
        return self.classReader.readLong()
        
    def readFloat(self, name=''):
        self.structure.append(Type.float(4,False),name)
        return self.classReader.readFloat()
        
    def readLong(self, name=''):
        self.structure.append(Type.float(8,False),name)
        return self.classReader.readLong()
        
    def readStruct(self, obj, name=''):
        self.structure.append(obj.resultingType(),name)
        return obj
        
    def readUTF(self, name=''):
        tname = ''
        if len(name) > 0:
            tname = name + "_len"
        length = self.readShort(tname)
        if len(name) > 0:
            tname = name + "_data"
        return self.readArray(length, tname, aType = self.classReader.charType) # I would prefer Type.char()
        
UTF_8 = 1
INTEGER = 3
FLOAT = 4
LONG = 5
DOUBLE = 6
CLASS_REFERENCE = 7
STRING_REFERENCE = 8
FIELD_REFERENCE = 9
METHOD_REFERENCE = 10
INTERFACE_REFERENCE = 11
NAME_AND_TYPE = 12
METHOD_HANDLE = 15
METHOD_TYPE = 16
INVOKE_DYNAMIC = 18
class JVMConstantPool(JVMStructure):
    
    def __init__(self, r, size):
        JVMStructure.__init__(self, r)
        self.poolSize = size
        self.classReader.constantPool = self
        self.read()
    
    def getTagSize(self, tag):
        if(tag == UTF_8): return -1
        if(tag == INTEGER): return 4
        if(tag == FLOAT): return 4
        if(tag == LONG): return 8
        if(tag == DOUBLE): return 8
        if(tag == CLASS_REFERENCE): return 2
        if(tag == STRING_REFERENCE): return 2
        if(tag == FIELD_REFERENCE): return 4
        if(tag == METHOD_REFERENCE): return 4
        if(tag == INTERFACE_REFERENCE): return 4
        if(tag == NAME_AND_TYPE): return 4
        if(tag == METHOD_HANDLE): return 3
        if(tag == METHOD_TYPE): return 2
        if(tag == INVOKE_DYNAMIC): return 4
        return 0
        
    def getTagName(self, tag):
        if(tag == UTF_8): return "UTF_8"
        if(tag == INTEGER): return "INTEGER"
        if(tag == FLOAT): return "FLOAT"
        if(tag == LONG): return "LONG"
        if(tag == DOUBLE): return "DOUBLE"
        if(tag == CLASS_REFERENCE): return "CLASS_REFERENCE"
        if(tag == STRING_REFERENCE): return "STRING_REFERENCE"
        if(tag == FIELD_REFERENCE): return "FIELD_REFERENCE"
        if(tag == METHOD_REFERENCE): return "METHOD_REFERENCE"
        if(tag == INTERFACE_REFERENCE): return "INTERFACE_REFERENCE"
        if(tag == NAME_AND_TYPE): return "NAME_AND_TYPE"
        if(tag == METHOD_HANDLE): return "METHOD_HANDLE"
        if(tag == METHOD_TYPE): return "METHOD_TYPE"
        if(tag == INVOKE_DYNAMIC): return "INVOKE_DYNAMIC"
        return None
    
    def read(self):
        self.poolContent = [None]*self.poolSize
        self.poolLocation = [0]*self.poolSize
        i = 0
        while i<self.poolSize-1:
            entryName = "constant_pool["+str(i)+"]"
            self.poolLocation[i+1] = self.classReader.index()
            tag = self.readByte(entryName+"_tag")
            size = self.getTagSize(tag)
            if size == 0:
                print("Exception: Error Reading Constant Pool ("+str(tag)+")")
                return
            if  (tag == UTF_8):   self.poolContent[i+1] = self.readUTF(entryName)
            elif(tag == INTEGER): self.poolContent[i+1] = self.readInt(entryName)
            elif(tag == FLOAT):   self.poolContent[i+1] = self.readFloat(entryName)
            elif(tag == LONG):    
                self.poolContent[i+1] = self.readLong(entryName)
                i += 1
            elif(tag == DOUBLE): 
                self.poolContent[i+1] = self.readDouble(entryName)
                i += 1
            elif(tag == CLASS_REFERENCE):     self.poolContent[i+1]    = self.readStruct(JVMClassReference(self.classReader),entryName)
            elif(tag == STRING_REFERENCE):    self.poolContent[i+1]    = self.readStruct(JVMStringReference(self.classReader),entryName)
            elif(tag == FIELD_REFERENCE):     self.poolContent[i+1]    = self.readStruct(JVMFieldReference(self.classReader),entryName)
            elif(tag == METHOD_REFERENCE):    self.poolContent[i+1]    = self.readStruct(JVMMethodReference(self.classReader),entryName)
            elif(tag == INTERFACE_REFERENCE): self.poolContent[i+1]    = self.readStruct(JVMInterfaceMethodReference(self.classReader),entryName)
            elif(tag == NAME_AND_TYPE):       self.poolContent[i+1]    = self.readStruct(JVMNameAndTypeDescriptor(self.classReader),entryName)
            elif(tag == METHOD_HANDLE):       self.poolContent[i+1]    = self.readStruct(JVMMethodHandle(self.classReader),entryName)
            elif(tag == METHOD_TYPE):         self.poolContent[i+1]    = self.readStruct(JVMMethodType(self.classReader),entryName)
            elif(tag == INVOKE_DYNAMIC):      self.poolContent[i+1]    = self.readStruct(JVMInvokeDynamic(self.classReader),entryName)                                                              
            i += 1

    def get(self, index):
        return self.poolContent[index&0xFFFF]
      
class JVMClassReference(JVMStructure):

    def __init__(self,r):
        JVMStructure.__init__(self, r)
        self.poolContent = self.classReader.constantPool
        self.read()
        
    def read(self):
        self.index = self.readShort("index")
        
    def __str__(self):
        return str(self.poolContent.get(self.index))
        
class JVMStringReference(JVMStructure):

    def __init__(self,r):
        JVMStructure.__init__(self, r)
        self.poolContent = self.classReader.constantPool
        self.read()
        
    def read(self):
        self.index = self.readShort("index")
        
    def __str__(self):
        return '"'+str(self.poolContent.get(self.index))+'"'
        
class JVMFieldReference(JVMStructure):

    def __init__(self,r):
        JVMStructure.__init__(self, r)
        self.poolContent = self.classReader.constantPool
        self.read()
        
    def read(self):
        self.classReference   = self.readShort("classReference")
        self.nameAndType      = self.readShort("nameAndType")
        
    def __str__(self):
        return str(self.poolContent.get(self.classReference))+"."+str(self.poolContent.get(self.nameAndType))
    
class JVMMethodReference(JVMStructure):

    def __init__(self,r):
        JVMStructure.__init__(self, r)
        self.poolContent = self.classReader.constantPool
        self.read()
        
    def read(self):
        self.classReference   = self.readShort("classReference")
        self.nameAndType      = self.readShort("nameAndType")
        
    def __str__(self):
        return str(self.poolContent.get(self.classReference))+"."+str(self.poolContent.get(self.nameAndType))
        
class JVMInterfaceMethodReference(JVMStructure):

    def __init__(self,r):
        JVMStructure.__init__(self, r)
        self.poolContent = self.classReader.constantPool
        self.read()
        
    def read(self):
        self.classReference   = self.readShort("classReference")
        self.nameAndType      = self.readShort("nameAndType")
        
    def __str__(self):
        return str(self.poolContent.get(self.classReference))+"."+str(self.poolContent.get(self.nameAndType))
        
class JVMNameAndTypeDescriptor(JVMStructure):

    def __init__(self,r):
        JVMStructure.__init__(self, r)
        self.poolContent = self.classReader.constantPool
        self.read()
        
    def read(self):
        self.identifier            = self.readShort("identifier")
        self.encodedTypeDescriptor = self.readShort("encodedTypeDescriptor")
        
    def __str__(self):
        return str(self.poolContent.get(self.identifier))#+"("+str(self.poolContent[self.encodedTypeDescriptor])+")"
        
class JVMMethodHandle(JVMStructure):

    def __init__(self,r):
        JVMStructure.__init__(self, r)
        self.poolContent = self.classReader.constantPool
        self.read()
        
    def read(self):
        self.kind  = self.readShort("kind")
        self.index = self.readShort("index")
        
    def __str__(self):
        try:
            return str(self.poolContent.get(self.index))
        except Exception:
            return "==Error Parsing=="
        
class JVMMethodType(JVMStructure):

    def __init__(self,r):
        JVMStructure.__init__(self, r)
        self.poolContent = self.classReader.constantPool
        self.read()
        
    def read(self):
        self.index = self.readShort("index")
        
    def __str__(self):
        try:
            return str(self.poolContent.get(self.index))
        except Exception:
            return "==Error Parsing=="

class JVMInvokeDynamic(JVMStructure):

    def __init__(self,r):
        JVMStructure.__init__(self, r)
        self.poolContent = self.classReader.constantPool
        self.read()
        
    def read(self):
        self.bootstrap = self.readShort("bootstrap")
        self.nat = self.readShort("nat")         
        
    def __str__(self):
        #try:
            #str(self.poolContent[self.nat])
            tpl = self.classReader.getBootstrap(self.bootstrap)
            mtd = self.poolContent.get(tpl[0])
            pars = [str(self.poolContent.get(tpl[2][i])) for i in range(tpl[1])]
            if str(mtd) == "java/lang/invoke/LambdaMetafactory.metafactory": #probably not a good idea to work with the serialized version here, doesn't really matter though
                return str(mtd)+" "+pars[1]
            else:
                return str(mtd)+" "+str(pars)
        #except Exception:
        #    return "==Error Parsing=="
        
class JVMFieldInfo(JVMStructure):
        
    def __init__(self, r):
        JVMStructure.__init__(self, r)
        self.read()
        
    def read(self):
        self.access_flags = self.readShort("access_flags")
        self.name_index   = self.readShort("name_index")
        self.descriptor_index = self.readShort("descriptor_index")
        self.attributes_count = self.readShort("attributes_count")
        self.attributes = [None]*self.attributes_count
        for i in range(self.attributes_count):
            self.attributes[i] = self.readStruct(JVMAttributeInfo(self.classReader), "attribute["+str(i)+"]")
            
class JVMMethodInfo(JVMStructure):

    def __init__(self, r, ind):
        JVMStructure.__init__(self, r)
        self.index = ind
        self.read()
        
    def read(self):
        self.access_flags = self.readShort("access_flags")
        self.name_index   = self.readShort("name_index")
        self.descriptor_index = self.readShort("descriptor_index")
        self.attributes_count = self.readShort("attributes_count")
        self.attributes = [None]*self.attributes_count
        self.code_attribute = None
        for i in range(self.attributes_count):
            self.attributes[i] = self.readStruct(JVMAttributeInfo(self.classReader),"attribute["+str(i)+"]")
            if self.attributes[i].attributeType == "Code":
                self.code_attribute = self.attributes[i]
             
        # register as method if method info has code
        if self.code_attribute != None:
            start_address = self.code_attribute.attribute.start_address
            end_address = self.code_attribute.attribute.end_address
            name = self.classReader.constantPool.poolContent[self.name_index]
            if name in self.classReader.registeredMethodList:
                orig_name = name
                posfix = 1
                name = orig_name+"("+str(posfix)+")"
                while name in self.classReader.registeredMethodList:
                    posfix += 1
                    name = orig_name+"("+str(posfix)+")"
            self.classReader.registeredMethodList.append(name)
            self.classReader.view.add_auto_segment(0x1000000+0x100000*self.index, end_address-start_address, start_address, end_address-start_address, SegmentFlag.SegmentReadable |  SegmentFlag.SegmentExecutable)
            self.classReader.view.add_function(0x1000000+0x100000*self.index) #register function
            self.classReader.view.define_auto_symbol(Symbol(SymbolType.DataSymbol, 0x1000000+0x100000*self.index, name))            
            

class JVMAttributeInfo(JVMStructure):
    
    def __init__(self, r):
        JVMStructure.__init__(self, r)
        self.read()
    
    def read(self):
        self.attribute_name_index = self.readShort("attribute_name_index")
        self.attribute_length   = self.readInt("attribute_length")
        self.attributeType = self.classReader.constantPool.get(self.attribute_name_index)
        self.attribute            = None 
        if self.attributeType == "Code":
            self.attribute = self.readStruct(JVMCodeAttribute(self.classReader),"attribute")
        elif self.attributeType == "BootstrapMethods":
            self.attribute = self.readStruct(JVMBootstrapMethods(self.classReader),"attribute")
        else:
            self.readArray(self.attribute_length, "attribute")
        
class JVMCodeAttribute(JVMStructure):
    
    def __init__(self, r):
        JVMStructure.__init__(self, r)
        self.read()
    
    def read(self):
        self.max_stack = self.readShort("max_stack")
        self.max_locals = self.readShort("max_locals")
        self.code_length = self.readInt("code_length")
        self.start_address = self.classReader.index()
        self.code = self.readArray(self.code_length,"code")
        self.end_address = self.classReader.index()
        self.exception_table_length = self.readShort("exception_table_length")
        self.exception_table = []
        for i in range(self.exception_table_length):
            # TODO Exception structure
            self.exception_table.append((self.readShort(),self.readShort(),self.readShort(),self.readShort()))
        self.attributes_count = self.readShort("attributes_count")
        self.attributes = []
        for i in range(self.attributes_count):
            self.attributes.append(self.readStruct(JVMAttributeInfo(self.classReader),"attribute["+str(i)+"]"))

class JVMBootstrapMethods(JVMStructure):

    def __init__(self, r):
        JVMStructure.__init__(self, r)
        self.read()
        
    def read(self):
        self.num_bootstrap_methods = self.readShort("num_bootstrap_methods")
        self.bootstrap_methods = []
        for i in range(self.num_bootstrap_methods):
            bootstrap_method_ref = self.readShort("bootstrap_method_ref["+str(i)+"]")
            num_bootstrap_arguments = self.readShort("num_bootstrap_arguments["+str(i)+"]")
            bootstrap_arguments = []
            for j in range(num_bootstrap_arguments):
                bootstrap_arguments.append(self.readShort("bootstrap_arguments["+str(j)+"]"))
            self.bootstrap_methods.append([bootstrap_method_ref,num_bootstrap_arguments,bootstrap_arguments])
            
class JVMClassStructure(JVMStructure):

    def __init__(self, r):
        JVMStructure.__init__(self, r)
        self.read()
        
    def read(self):
        self.magic           = self.readInt("magic")
        self.minor_version   = self.readShort("minor_version")
        self.major_version   = self.readShort("major_version")
        self.constant_pool_count = self.readShort("constant_pool_count")
        self.constantPool    = self.readStruct(JVMConstantPool(self.classReader, self.constant_pool_count), "constantPool")
        self.access_flags    = self.readShort("access_flags")
        self.this_class      = self.readShort("this_class")
        self.super_class     = self.readShort("super_class")
        self.interface_count = self.readShort("interface_count")
        self.interfaces      = []
        for i in range(self.interface_count):
            self.interfaces.append(self.readShort("interface["+str(i)+"]"))
        self.fields_count = self.readShort("fields_count")
        self.fields          = []
        for i in range(self.fields_count):
            self.fields.append(self.readStruct(JVMFieldInfo(self.classReader),"field["+str(i)+"]"))
        self.methods_count = self.readShort("methods_count")
        self.methods         = []
        for i in range(self.methods_count):
            self.methods.append(self.readStruct(JVMMethodInfo(self.classReader, i),"method["+str(i)+"]"))
        self.attributes_count = self.readShort("attributes_count")
        self.attributes      = []
        for i in range(self.attributes_count):
            attr = self.readStruct(JVMAttributeInfo(self.classReader),"attribute["+str(i)+"]")
            self.attributes.append(attr)
            if attr.attributeType == "BootstrapMethods":
                self.classReader.setBootstrap(attr)
        
        
class JVMClassReader():
    def __init__(self,vi,da):
        self.view = vi
        self.data = da
        self.idx = 0    
        self.classStruct = None
        self.constantPool = None
        self.bootstrap_attribute = None
        self.registeredMethodList = []
    def reset(self):
        self.idx = 0
    def readLong(self):
        value = struct.unpack(">Q", self.data.read(self.idx,8))[0]
        self.idx += 8
        return value
    def readDouble(self):
        value = struct.unpack(">d", self.data.read(self.idx,8))[0]
        self.idx += 8
        return value
    def readFloat(self):
        value = struct.unpack(">f", self.data.read(self.idx,4))[0]
        self.idx += 4
        return value
    def readInt(self):
        value = struct.unpack(">I", self.data.read(self.idx,4))[0]
        self.idx += 4
        return value
    def readShort(self):
        value = struct.unpack(">H", self.data.read(self.idx,2))[0]
        self.idx += 2
        return value
    def readByte(self):
        value = struct.unpack("B", self.data.read(self.idx,1))[0]
        self.idx += 1
        return value
    def index(self):
        return self.idx
        
    #This is some special Dynamic Invocation code
    def setBootstrap(self,attr):
        self.bootstrap_attribute = attr
      
    def getBootstrap(self,index):
        if self.bootstrap_attribute == None: return None
        return self.bootstrap_attribute.attribute.bootstrap_methods[index]

def completeUpdateWhenDone(self):
    for f in self.view.functions:
        analyze_tables(self.view, f)
        analyze_references(self.view, f)
        
class UpdateReferences(BinaryDataNotification):
    def function_updated(self,view, func):
        analyze_references(view, func)
        pass
        
def analyze_references(view, dispatcher):
    table_constantpool = []
    table_primitives = []
    find_poolRef = []
    find_primRef = []
    for i, name in enumerate(InstructionNames):
        if InstructionFormat[i] == TYPE_LDC:
            find_poolRef.append(name)
        if InstructionFormat[i] == TYPE_2INDEX:
            find_poolRef.append(name)
        if InstructionFormat[i] == TYPE_INTERFACE:
            find_poolRef.append(name)
        if InstructionFormat[i] == TYPE_DYNAMIC:
            find_poolRef.append(name)
        if InstructionFormat[i] == TYPE_ATYPE:
            find_primRef.append(name)
        if InstructionFormat[i] == TYPE_MULTIARRAY:
            find_poolRef.append(name)  
            
    for token,addr in dispatcher.instructions:
        t = str(token[0]).strip()
        if t in find_poolRef:
            table_constantpool.append(addr)
        elif t in find_primRef:
            table_primitives.append(addr)
                
    for addr in table_constantpool:
        decoded = decode_instruction(view.read(addr, 10), addr)
        value = decoded[3]
        if type(value) == type([]): value = value[0]
        if type(value) == type((0,0)): value = value[0]
        if dispatcher.get_int_display_type(addr,value+PSEUDOMEMORY_TABLE,0) != IntegerDisplayType.PointerDisplayType:
            dispatcher.set_int_display_type(addr,value+PSEUDOMEMORY_TABLE,0,IntegerDisplayType.PointerDisplayType)
            
    for addr in table_primitives:
        decoded = decode_instruction(view.read(addr, 10), addr)
        value = decoded[3]
        if type(value) == type([]): value = value[0]
        if type(value) == type((0,0)): value = value[0]
        if dispatcher.get_int_display_type(addr,value+PSEUDOMEMORY_PRIMITIVES,0) != IntegerDisplayType.PointerDisplayType:
            dispatcher.set_int_display_type(addr,value+PSEUDOMEMORY_PRIMITIVES,0,IntegerDisplayType.PointerDisplayType)
        
            
def analyze_tables(view, dispatcher):
    table_jumps = []
    
    for token,addr in dispatcher.instructions:
        if ('lookupswitch' in str(token[0]) or 'tableswitch' in str(token[0])):
            table_jumps.append(addr)
            
    for addr in table_jumps:
        #if len(dispatcher.get_indirect_branches_at(addr)) != 0:
        #    continue
        data = view.read(addr, 128)
        decoded = decode_instruction(data, addr)
        if decoded[0] == None:
            data = view.read(addr, decoded[3])
            decoded = decode_instruction(data, addr)
        if decoded[0] == "lookupswitch":
            pair_array = 2
        elif decoded[0] == "tableswitch":
            pair_array = 3
            
        value = decoded[3]
        branches = []
        for p in value[pair_array]:
            branches.append((view.arch,p[1]))
        branches.append((view.arch, value[0]))
        dispatcher.set_user_indirect_branches(addr, branches)
        
        #Do comments later as they update the binary
        dispatcher.set_comment_at(value[0], "Default Branch")
        for p in value[pair_array]:
            ad = ""
            if p[1] == value[0]:
                ad = " [Default Branch]"
            dispatcher.set_comment_at(p[1], "Branch Condition: "+str(p[0])+ad)
    
class ClassView(BinaryView):
    name = "JVM Class"
    long_name = "JVM Class Format"

    def __init__(self, data):
        BinaryView.__init__(self, parent_view = data, file_metadata = data.file)
        self.platform = Architecture['JVM'].standalone_platform
        
    @classmethod
    def is_valid_for_data(self, data):
        hdr = data.read(0, 6)
        if len(hdr) < 4:
            return False
        if struct.unpack(">I", hdr[0:4])[0] != 0xCAFEBABE:
            return False
        return True

    def init(self):
        try:
            self.cR = JVMClassReader(self,self.parent_view)
            
            self.cR.charType = self.parse_type_string("char")[0] # for some reason in my binary ninja version Type.char() is not accessable
            
            classStruct = JVMClassStructure(self.cR) # read class structure and add symbols
            self.cR.classStruct = classStruct
           
            self.define_data_var(0,  classStruct.resultingType())
                
            
            self.add_auto_segment(0, self.cR.index(), 0, self.cR.index(), SegmentFlag.SegmentReadable)
            self.add_auto_section("<data>",0, self.cR.index(), SectionSemantics.ReadOnlyCodeSectionSemantics)
            
            for i in range(len(self.cR.constantPool.poolContent)):
                content = self.cR.constantPool.poolContent[i]
                t = SymbolType.DataSymbol
                if "instance" in str(type(content)):
                    if content.__class__ == JVMMethodReference or content.__class__ == JVMInterfaceMethodReference or content.__class__ == JVMInvokeDynamic:
                        t = SymbolType.ImportAddressSymbol
                    elif content.__class__ == JVMStringReference:
                        t = SymbolType.DataSymbol
                elif "str" in str(type(content)):
                    t = SymbolType.DataSymbol
                self.define_user_symbol(Symbol(t, i+PSEUDOMEMORY_TABLE, str(content), full_name="pool_"+str(i)))
                
            primitive_names = ["Not Used","Not Used","Not Used","Not Used","Boolean","Char","Float","Double","Byte","Short","Int","Long"]
            for i in range(4,12):
                self.define_user_symbol(Symbol(SymbolType.DataSymbol, i+PSEUDOMEMORY_PRIMITIVES, primitive_names[i], full_name="primitive_"+str(i)))
                
            self.add_analysis_completion_event(completeUpdateWhenDone)
            self.register_notification(UpdateReferences())
            
            return True
        except:
            print(traceback.format_exc())
            return False
        
    def perform_is_executable(self):
        return True

    def perform_get_entry_point(self):
        return 0x10000000
        
    def perform_get_default_endianness():
        return Endianness.BigEndian


JVM.register()
ClassView.register()
