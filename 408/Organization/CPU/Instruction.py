import random
from typing import List, Dict, Tuple, Optional


class Instruction:
    """表示计算机指令的类"""

    def __init__(self, name: str, description: str, operand_types: List[str]):
        """
        初始化指令

        参数:
            name: 指令名称
            description: 指令描述
            operand_types: 操作数类型列表
        """
        self.name = name
        self.description = description
        self.operand_types = operand_types

    def __str__(self) -> str:
        return self.name


class MicroOperation:
    """表示微操作的类"""

    def __init__(self, step: int, description: str, control_signals: Optional[List[str]] = None):
        """
        初始化微操作

        参数:
            step: 步骤序号
            description: 微操作描述
            control_signals: 控制信号列表
        """
        self.step = step
        self.description = description
        self.control_signals = control_signals or []

    def __str__(self) -> str:
        signal_str = f"，控制信号：{', '.join(self.control_signals)}" if self.control_signals else ""
        return f"步骤{self.step}：{self.description}{signal_str}"


class ExamGenerator:
    """考研408微操作流程题目生成器"""

    def __init__(self):
        # 定义常见指令
        self.instructions = [
            Instruction("MOV", "数据传送指令", ["寄存器到寄存器", "立即数到寄存器", "内存到寄存器", "寄存器到内存"]),
            Instruction("ADD", "加法指令", ["寄存器加寄存器", "寄存器加立即数", "内存加寄存器"]),
            Instruction("SUB", "减法指令", ["寄存器减寄存器", "寄存器减立即数", "内存减寄存器"]),
            Instruction("JMP", "无条件跳转指令", ["直接跳转", "间接跳转"]),
            Instruction("BEQ", "相等则跳转指令", ["基于寄存器比较"]),
            Instruction("LOAD", "加载指令", ["内存到寄存器"]),
            Instruction("STORE", "存储指令", ["寄存器到内存"])
        ]

        # 定义取指周期微操作模板
        self.fetch_cycle_templates = [
            MicroOperation(1, "PC → MAR", ["PCout", "MARin"]),
            MicroOperation(2, "1 → R", ["Read"]),
            MicroOperation(3, "M(MAR) → MDR", []),
            MicroOperation(4, "MDR → IR", ["MDRout", "IRin"]),
            MicroOperation(5, "PC + 1 → PC", ["PC+1"])
        ]

    def generate_question(self) -> Tuple[str, Dict]:
        """生成题目及答案"""
        # 随机选择一条指令
        instruction = random.choice(self.instructions)

        # 随机选择一种操作数类型
        operand_type = random.choice(instruction.operand_types)

        # 生成题目
        question = f"针对{instruction.name}指令（{operand_type}），写出取指周期和执行周期的微操作流程，并列出每个步骤的控制信号。"

        # 生成答案
        answer = self._generate_answer(instruction, operand_type)

        return question, answer

    def _generate_answer(self, instruction: Instruction, operand_type: str) -> Dict:
        """生成答案"""
        # 获取取指周期微操作
        fetch_operations = self.fetch_cycle_templates

        # 根据指令类型生成执行周期微操作
        execute_operations = self._generate_execute_operations(instruction, operand_type)

        return {
            "fetch_cycle": fetch_operations,
            "execute_cycle": execute_operations
        }

    @staticmethod
    def _generate_execute_operations(instruction: Instruction, operand_type: str) -> List[MicroOperation]:
        """根据指令类型生成执行周期微操作"""
        operations = []

        if instruction.name == "MOV":
            if operand_type == "寄存器到寄存器":
                operations = [
                    MicroOperation(1, "R1 → Y", ["R1out", "Yin"]),
                    MicroOperation(2, "Y → R2", ["Yout", "R2in"])
                ]
            elif operand_type == "立即数到寄存器":
                operations = [
                    MicroOperation(1, "IR(地址码) → MAR", ["IRout", "MARin"]),
                    MicroOperation(2, "1 → R", ["Read"]),
                    MicroOperation(3, "M(MAR) → MDR", []),
                    MicroOperation(4, "MDR → R", ["MDRout", "Rin"])
                ]
            elif operand_type == "内存到寄存器":
                operations = [
                    MicroOperation(1, "R1 → MAR", ["R1out", "MARin"]),
                    MicroOperation(2, "1 → R", ["Read"]),
                    MicroOperation(3, "M(MAR) → MDR", []),
                    MicroOperation(4, "MDR → R2", ["MDRout", "R2in"])
                ]
            elif operand_type == "寄存器到内存":
                operations = [
                    MicroOperation(1, "R1 → MAR", ["R1out", "MARin"]),
                    MicroOperation(2, "R2 → MDR", ["R2out", "MDRin"]),
                    MicroOperation(3, "1 → W", ["Write"])
                ]

        elif instruction.name == "ADD":
            if operand_type == "寄存器加寄存器":
                operations = [
                    MicroOperation(1, "R1 → X", ["R1out", "Xin"]),
                    MicroOperation(2, "R2 → Y", ["R2out", "Yin"]),
                    MicroOperation(3, "X + Y → Z", ["Add", "Zin"]),
                    MicroOperation(4, "Z → R3", ["Zout", "R3in"])
                ]
            elif operand_type == "寄存器加立即数":
                operations = [
                    MicroOperation(1, "R1 → X", ["R1out", "Xin"]),
                    MicroOperation(2, "IR(立即数) → Y", ["IRout", "Yin"]),
                    MicroOperation(3, "X + Y → Z", ["Add", "Zin"]),
                    MicroOperation(4, "Z → R1", ["Zout", "R1in"])
                ]

        elif instruction.name == "SUB":
            if operand_type == "寄存器减寄存器":
                operations = [
                    MicroOperation(1, "R1 → X", ["R1out", "Xin"]),
                    MicroOperation(2, "R2 → Y", ["R2out", "Yin"]),
                    MicroOperation(3, "X - Y → Z", ["Sub", "Zin"]),
                    MicroOperation(4, "Z → R1", ["Zout", "R1in"])
                ]

        elif instruction.name == "JMP":
            if operand_type == "直接跳转":
                operations = [
                    MicroOperation(1, "IR(地址码) → PC", ["IRout", "PCin"])
                ]

        elif instruction.name == "BEQ":
            operations = [
                MicroOperation(1, "R1 → X", ["R1out", "Xin"]),
                MicroOperation(2, "R2 → Y", ["R2out", "Yin"]),
                MicroOperation(3, "X - Y → Z", ["Sub", "Zin"]),
                MicroOperation(4, "Z=0? 是则 IR(地址码) → PC", ["Zero", "IRout", "PCin"])
            ]

        elif instruction.name == "LOAD":
            operations = [
                MicroOperation(1, "R1 → MAR", ["R1out", "MARin"]),
                MicroOperation(2, "1 → R", ["Read"]),
                MicroOperation(3, "M(MAR) → MDR", []),
                MicroOperation(4, "MDR → R2", ["MDRout", "R2in"])
            ]

        elif instruction.name == "STORE":
            operations = [
                MicroOperation(1, "R1 → MAR", ["R1out", "MARin"]),
                MicroOperation(2, "R2 → MDR", ["R2out", "MDRin"]),
                MicroOperation(3, "1 → W", ["Write"])
            ]

        return operations

    def display_question_and_answer(self):
        """显示题目及答案"""
        question, answer = self.generate_question()

        print("=" * 50)
        print("考研408微操作流程与控制信号题目")
        print("=" * 50)
        print(f"题目：{question}")
        print("\n答案：")

        # 显示取指周期
        print("\n一、取指周期微操作流程：")
        for op in answer["fetch_cycle"]:
            print(op)

        # 显示执行周期
        print("\n二、执行周期微操作流程：")
        for op in answer["execute_cycle"]:
            print(op)

        print("\n" + "=" * 50)


if __name__ == "__main__":
    generator = ExamGenerator()
    generator.display_question_and_answer()
