import re
from typing import List, Set
from fraction import Fraction


class ExpressionValidator:
    def __init__(self):
        self.generated_expressions: Set[str] = set()

    def is_duplicate(self, expr: str) -> bool:
        """检查表达式是否重复"""
        # 规范化表达式
        normalized = self._normalize_expression(expr)
        return normalized in self.generated_expressions

    def add_expression(self, expr: str):
        """添加表达式到已生成集合"""
        normalized = self._normalize_expression(expr)
        self.generated_expressions.add(normalized)

    def _normalize_expression(self, expr: str) -> str:
        """规范化表达式以检查重复"""
        # 移除空格
        expr = expr.replace(' ', '')

        # 构建表达式树并规范化
        return self._build_normalized_tree(expr)

    def _build_normalized_tree(self, expr: str) -> str:
        """构建规范化的表达式树表示"""
        if '(' not in expr and ')' not in expr:
            # 简单表达式，直接排序操作数
            return self._normalize_simple_expression(expr)

        # 处理带括号的表达式
        # 这里简化处理，实际应该解析表达式树
        return expr

    def _normalize_simple_expression(self, expr: str) -> str:
        """规范化简单表达式（无括号）"""
        operators = []
        operands = []

        # 分割操作数和运算符
        tokens = re.split(r'([+\-×÷])', expr)

        i = 0
        while i < len(tokens):
            token = tokens[i].strip()
            if not token:
                i += 1
                continue

            if token in ['+', '-', '×', '÷']:
                operators.append(token)
            else:
                operands.append(token)
            i += 1

        # 对于加法和乘法，排序操作数
        if len(operators) == 1 and operators[0] in ['+', '×']:
            operands.sort()

        # 重新构建表达式
        result = operands[0]
        for i in range(len(operators)):
            result += operators[i] + operands[i + 1]

        return result

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