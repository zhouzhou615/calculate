import re
from typing import List, Set
from fraction import Fraction


class ExpressionValidator:
    def __init__(self):
        self.generated_expressions: Set[str] = set()
        # 预编译运算符分割正则
        self.op_split_pattern = re.compile(r'([+\-×÷])')

    def _normalize_expression(self, expr: str) -> str:
        """规范化表达式（支持多层括号和多运算符）"""
        expr = expr.replace(' ', '')
        # 递归处理最内层括号，逐层规范化
        while '(' in expr:
            match = re.search(r'\(([^\(\)]+)\)', expr)  # 匹配最内层括号
            if not match:
                break
            inner = match.group(1)
            normalized_inner = self._normalize_simple_expression(inner)
            expr = expr.replace(f'({inner})', normalized_inner)
        # 规范化最终无括号表达式
        return self._normalize_simple_expression(expr)

    def _normalize_simple_expression(self, expr: str) -> str:
        """规范化无括号表达式（支持多运算符，按优先级处理）"""
        tokens = self.op_split_pattern.split(expr)
        operands = [t for t in tokens[::2] if t]  # 提取操作数（偶数位）
        operators = [t for t in tokens[1::2] if t]  # 提取运算符（奇数位）

        # 先处理乘除（优先级高）
        i = 0
        while i < len(operators):
            op = operators[i]
            if op in ['×', '÷']:
                left = operands[i]
                right = operands[i+1]
                # 乘法交换律：交换操作数使表达式一致
                if op == '×':
                    merged = f"{min(left, right)}×{max(left, right)}"
                else:  # 除法不满足交换律，保持顺序
                    merged = f"{left}÷{right}"
                # 合并操作数和运算符
                operands = operands[:i] + [merged] + operands[i+2:]
                operators.pop(i)
            else:
                i += 1

        # 再处理加减（优先级低）
        i = 0
        while i < len(operators):
            op = operators[i]
            if op == '+':
                # 加法交换律：交换操作数
                left = operands[i]
                right = operands[i+1]
                merged = f"{min(left, right)}+{max(left, right)}"
                operands = operands[:i] + [merged] + operands[i+2:]
                operators.pop(i)
            else:  # 减法不满足交换律，保持顺序
                i += 1

        return operands[0] if operands else expr
    def is_duplicate(self, expr: str) -> bool:
        """检查表达式是否重复"""
        # 规范化表达式
        normalized = self._normalize_expression(expr)
        return normalized in self.generated_expressions

    def add_expression(self, expr: str):
        """添加表达式到已生成集合"""
        normalized = self._normalize_expression(expr)
        self.generated_expressions.add(normalized)



    def _build_normalized_tree(self, expr: str) -> str:
        """构建规范化的表达式树表示"""
        if '(' not in expr and ')' not in expr:
            # 简单表达式，直接排序操作数
            return self._normalize_simple_expression(expr)

        # 处理带括号的表达式
        # 这里简化处理，实际应该解析表达式树
        return expr


    def validate_constraints(self, expr: str, result: Fraction, max_operators: int = 3) -> bool:
        """验证表达式约束"""
        # 检查运算符数量
        operator_count = sum(1 for char in expr if char in ['+', '-', '×', '÷'])
        if operator_count > max_operators:
            return False

        # 检查是否重复
        if self.is_duplicate(expr):
            return False

        return True