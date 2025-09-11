#!/usr/bin/env python3
#
# Please look for "TODO" in the comments, which indicate where you
# need to write your code.
#
# Part 2: Integer Negation and Subtraction Using NAND Gates (1 point)
#
# * Objective:
#   Implement a function that performs integer negation using only NAND
#   gates and use it to implement subtraction.
# * Details:
#   The description of the problem and the solution template can be
#   found in `hw1/p2.py`.
#
# From lecture `01w`, we learned that NAND is a universal gate, that
# any binary operations can be built by using only NAND gates.
# Following the lecture notes, we define the "NAND gate" as


def NAND(a, b):
    '''
    与非门:
        | A | B | （A & B） | NAND(A, B) |
        |---|---|---------|------------|
        | 0 | 0 |    0    | 1          |
        | 0 | 1 |    0    | 1          |
        | 1 | 0 |    0    | 1          |
        | 1 | 1 |    1    | 0          |
        任何布尔函数都能用与非门实现。
    '''
    return 1 - (a & b)  # NOT (a AND b)


# Following the notes again, we define also other basic operations:

def NOT(a):
    return NAND(a, a)

def AND(a, b):
    return NOT(NAND(a, b))

def OR(a, b):
    return NAND(NOT(a), NOT(b))

def XOR(a, b): 
    '''
    异或门：
        A   B	A XOR B
        0	0	0
        0	1	1
        1	0	1
        1	1	0
        若两个输入的电平相异，则输出为高电平（1）；
        若两个输入的电平相同，则输出为低电平（0）。
        这一函数能实现模为2的加法，因此，异或门可以实现计算机中的二进制加法。
    '''
    c = NAND(a, b)
    return NAND(NAND(a, c), NAND(b, c))

# We also implemented the half, full, and multi-bit adders:

def half_adder(A, B):
    '''
    半加器：
        A	B	C	S
        0	0	0	0
        1	0	0	1
        0	1	0	1
        1	1	1	0
        将两个一位二进制数相加。
        和：  记作 S，来自对应的英语Sum；
        进位：记作 C，来自对应的英语Carry一位的数字。
    '''
    S = XOR(A, B)  # Sum using XOR
    C = AND(A, B)  # Carry using AND
    return S, C

def full_adder(A, B, Cin):
    '''
    全加器：
        A	B	Cin	Cout	S
        0	0	0	0		0
        1	0	0	0		1
        0	1	0	0		1
        1	1	0	1		0
        0	0	1	0		1
        1	0	1	1		0
        0	1	1	1		0
        1	1	1	1		1
        将两个一位二进制数相加，
        并根据接收到的低位进位信号，输出和、进位输出。
    '''
    s, c = half_adder(A,   B)
    S, C = half_adder(Cin, s)
    Cout = OR(c, C)
    return S, Cout

def multibit_adder(A, B, carrybit=False):
    '''
    多位全加器：
        在此基础上多了一个进位输入，
        所以多个全加器可以串联起来，就能处理多位二进制数的加法。
        
    举例：4位二进制加法器
        要加两个4位数： ABCD + HIJK
        构造方式：
            第 0 位：用一个半加器 或 全加器 (Cin=0) 处理 D + K。
            第 1 位：用全加器，输入是 C、J、以及前一位的进位。
            第 2 位：同理，用全加器。
            第 3 位：同理，用全加器。
        这样一串下来，就得到整个4位的和（S₃S₂S₁S₀）和最终进位Cout。
    '''
    assert(len(A) == len(B))

    n = len(A)
    c = 0
    S = []
    for i in range(n):
        s, c = full_adder(A[i], B[i], c)
        S.append(s)
    if carrybit:
        S.append(c)  # add the extra carry bit
    return S

# Now, getting into the assignment, we would like to first implement a
# negative function.
#
# Please keep the following function prototype, otherwise the
# auto-tester would fail, and you will not obtain point for this
# assigment.

def multibit_negative(A):
    """Multi-bit integer negative operator

    This function take the binary number A and return negative A using
    two's complement （补码，即取反加一）.
    In other words, if the input
        A = 3 = 0b011,
    then the output is
        -A = -3 = 0b101.

    Args:
        A: input number in binary represented as a python list, with
           the least significant digit be the first.
           That is, the binary 0b011 should be given by [1,1,0].

    Returns:
        Negative A using two's complement represented as a python
        list, with the least significant (rightmost) digit be the first.

    """
    # Done: implement the function here
    if any(A) == False: # i.e. [0, 0, 0, 0]
        return A
    
    N, B = [], []
    A.reverse() # I like this digit order, left to right
    for d in range(len(A)):
        N.append(NOT(A[d]))
        B.append(0)
    B[-1] = 1
    
    Cin = 0
    for i in range(len(N)):
        n, b      = N[-(i+1)], B[-(i+1)]
        S, Cout   = full_adder(n, b, Cin)
        N[-(i+1)] = S
        Cin = Cout
    
    N.reverse()
    
    return N

# We are now ready to implement subtraction using multibit_adder() and
# multibit_negative().

def multibit_subtractor(A, B):
    """Multi-bit integer subtraction operator

    This function take the binary numbers A and B, and return A - B.
    Be careful on how the carrying bit is handled in multibit_adder().
    Make sure that when A == B, the result A - B should be zero.

    Args:
        A, B: input number in binary represented as a python list,
           with the least significant digit be the first.
           That is, the binary 0b011 should be given by [1,1,0].

    Returns:
        A - B represented as a python list, with the least significant
        digit be the first.

    """
    # Done: implement the function here
    assert(len(A) == len(B))
    
    if A == B:
        return [0] * len(A)
    
    D   = []
    Cin = 0
    nB  = multibit_negative(B)
    for i in range(len(A)):
        a, nb     = A[i], nB[i]
        S, Cout   = full_adder(a, nb, Cin)
        D.append(S)
        Cin = Cout
    
    return D