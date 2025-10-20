import random
from typing import List, Tuple, Optional
from fraction import Fraction


class Expression:
    def __init__(self):
        self.operators = ['+', '-', '×', '÷']
        self.priority = {'+': 1, '-': 1, '×': 2, '÷': 2}

    def generate_expression(self, max_range: int, max_operators: int = 3) -> Tuple[str, Fraction]:
        """生成表达式和结果"""
        while True:
            try:
                num_operators = random.randint(1, max_operators)
                num_operands = num_operators + 1

                # 生成操作数
                operands = [Fraction.random_fraction(max_range) for _ in range(num_operands)]

                # 生成运算符
                operators = [random.choice(self.operators) for _ in range(num_operators)]

                # 构建表达式树
                expr_str, result = self._build_expression(operands, operators)

                # 验证结果有效性
                if self._is_valid_expression(expr_str, result):
                    return expr_str, result
            except (ValueError, ZeroDivisionError):
                continue

    def _build_expression(self, operands: List[Fraction], operators: List[str]) -> Tuple[str, Fraction]:
        """构建表达式树"""
        if len(operands) == 1:
            return operands[0].to_string(), operands[0]

        # 随机选择分割点
        split_point = random.randint(1, len(operands) - 1)

        # 递归构建左右子树
        left_expr, left_val = self._build_expression(
            operands[:split_point], operators[:split_point - 1]
        )
        right_expr, right_val = self._build_expression(
            operands[split_point:], operators[split_point - 1:]
        )

        op = operators[split_point - 1]

        # 计算结果
        if op == '+':
            result = left_val + right_val
        elif op == '-':
            result = left_val - right_val
        elif op == '×':
            result = left_val * right_val
        elif op == '÷':
            result = left_val / right_val

        # 添加括号
        left_needs_paren = self._needs_parentheses(left_expr, op, is_left=True)
        right_needs_paren = self._needs_parentheses(right_expr, op, is_left=False)

        left_str = f"({left_expr})" if left_needs_paren else left_expr
        right_str = f"({right_expr})" if right_needs_paren else right_expr

        expr_str = f"{left_str} {op} {right_str}"
        return expr_str, result

    def _needs_parentheses(self, expr: str, parent_op: str, is_left: bool) -> bool:
        """判断是否需要添加括号"""
        if '(' in expr and ')' in expr:
            return False

        # 简单判断：如果表达式包含运算符且优先级低于父运算符，需要括号
        for op in self.operators:
            if op in expr and self.priority[op] < self.priority[parent_op]:
                return True

        # 对于减法和除法，右操作数需要特殊处理
        if not is_left and parent_op in ['-', '÷']:
            for op in self.operators:
                if op in expr:
                    return True

        return False

    def _is_valid_expression(self, expr: str, result: Fraction) -> bool:
        """验证表达式有效性"""
        # 检查结果是否为真分数（对于除法）
        if '÷' in expr and not result.is_proper_fraction():
            return False

        # 检查计算过程中是否产生负数（通过模拟计算验证）
        try:
            # 这里简化验证，实际应该遍历所有子表达式
            if not result.is_positive() and result != Fraction(0):
                return False
        except:
            return False

        return True

    def evaluate_expression(self, expr: str) -> Fraction:
        """计算表达式值"""
        # 移除空格
        expr = expr.replace(' ', '')

        def parse_expression(tokens):
            values = []
            ops = []

            i = 0
            while i < len(tokens):
                token = tokens[i]

                if token == '(':
                    # 处理子表达式
                    j = i + 1
                    paren_count = 1
                    while j < len(tokens) and paren_count > 0:
                        if tokens[j] == '(':
                            paren_count += 1
                        elif tokens[j] == ')':
                            paren_count -= 1
                        j += 1

                    sub_expr = tokens[i + 1:j - 1]
                    values.append(parse_expression(sub_expr))
                    i = j
                    continue

                elif token in self.operators:
                    while (ops and ops[-1] != '(' and
                           self.priority[ops[-1]] >= self.priority[token]):
                        self._apply_operator(values, ops)
                    ops.append(token)

                else:
                    # 解析数字或分数
                    values.append(Fraction.from_string(token))

                i += 1

            while ops:
                self._apply_operator(values, ops)

            return values[0] if values else Fraction(0)

        # 分词
        tokens = self._tokenize(expr)
        return parse_expression(tokens)

    def _tokenize(self, expr: str) -> List[str]:
        """将表达式分词"""
        tokens = []
        i = 0
        while i < len(expr):
            if expr[i] in '()+-×÷':
                tokens.append(expr[i])
                i += 1
            else:
                # 解析数字或分数
                j = i
                while j < len(expr) and expr[j] not in '()+-×÷':
                    j += 1
                token = expr[i:j]
                if token:
                    tokens.append(token)
                i = j

        return tokens

    def _apply_operator(self, values: List[Fraction], ops: List[str]):
        """应用运算符"""
        if len(values) < 2 or not ops:
            return

        op = ops.pop()
        right = values.pop()
        left = values.pop()

        if op == '+':
            values.append(left + right)
        elif op == '-':
            values.append(left - right)
        elif op == '×':
            values.append(left * right)
        elif op == '÷':
            values.append(left / right)