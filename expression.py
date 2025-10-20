import random
from typing import List, Tuple
from fraction import Fraction


class Expression:
    def __init__(self):
        self.operators = ['+', '-', '×', '÷']
        self.priority = {'+': 1, '-': 1, '×': 2, '÷': 2}

    def generate_expression(self, max_range: int, max_operators: int = 3) -> Tuple[str, Fraction]:
        """生成表达式和结果（确保所有子步骤符合约束）"""
        while True:
            try:
                num_operators = random.randint(1, max_operators)
                num_operands = num_operators + 1

                # 生成操作数
                operands = [Fraction.random_fraction(max_range) for _ in range(num_operands)]

                # 生成运算符
                operators = [random.choice(self.operators) for _ in range(num_operators)]

                # 构建表达式树（带中间结果校验）
                expr_str, result = self._build_expression(operands, operators)

                # 最终验证
                if self._is_valid_expression(expr_str, result):
                    return expr_str, result
            except (ValueError, ZeroDivisionError):
                continue

    def _build_expression(self, operands: List[Fraction], operators: List[str]) -> Tuple[str, Fraction]:
        """构建表达式树（递归检查所有子表达式约束）"""
        if len(operands) == 1:
            return operands[0].to_string(), operands[0]

        # 随机选择分割点
        split_point = random.randint(1, len(operands) - 1)

        # 递归构建左右子树（确保子表达式已满足约束）
        left_expr, left_val = self._build_expression(
            operands[:split_point], operators[:split_point - 1]
        )
        right_expr, right_val = self._build_expression(
            operands[split_point:], operators[split_point - 1:]
        )

        op = operators[split_point - 1]

        # 计算结果并检查约束
        if op == '+':
            result = left_val + right_val
        elif op == '-':
            # 核心约束：减法必须满足 e1 ≥ e2（禁止中间结果为负数）
            if left_val < right_val:
                raise ValueError("减法子表达式结果为负数")
            result = left_val - right_val
        elif op == '×':
            result = left_val * right_val
        elif op == '÷':
            # 核心约束：除法结果必须为真分数
            if right_val.numerator == 0:
                raise ZeroDivisionError("除数为0")
            result = left_val / right_val
            if not result.is_proper_fraction():
                raise ValueError("除法子表达式结果非真分数")

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

        # 检查子表达式运算符优先级
        for op in self.operators:
            if op in expr and self.priority[op] < self.priority[parent_op]:
                return True

        # 减法/除法的右操作数特殊处理
        if not is_left and parent_op in ['-', '÷']:
            for op in self.operators:
                if op in expr:
                    return True

        return False

    def _is_valid_expression(self, expr: str, result: Fraction) -> bool:
        """最终验证（确保无遗漏约束）"""
        # 确保最终结果非负（因中间步骤已约束，此处为双重保障）
        if result.numerator < 0:
            return False
        # 确保除法结果为真分数（子步骤已约束，此处为双重保障）
        if '÷' in expr and not result.is_proper_fraction():
            return False
        return True

    # 以下方法（evaluate_expression、_tokenize、_apply_operator）保持不变
    def evaluate_expression(self, expr: str) -> Fraction:
        expr = expr.replace(' ', '')

        def parse_expression(tokens):
            values = []
            ops = []
            i = 0
            while i < len(tokens):
                token = tokens[i]
                if token == '(':
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
                elif token in self.operators:
                    while (ops and ops[-1] != '(' and
                           self.priority[ops[-1]] >= self.priority[token]):
                        self._apply_operator(values, ops)
                    ops.append(token)
                    i += 1
                else:
                    values.append(Fraction.from_string(token))
                    i += 1
            while ops:
                self._apply_operator(values, ops)
            return values[0] if values else Fraction(0)

        tokens = self._tokenize(expr)
        return parse_expression(tokens)

    def _tokenize(self, expr: str) -> List[str]:
        tokens = []
        i = 0
        while i < len(expr):
            if expr[i] in '()+-×÷':
                tokens.append(expr[i])
                i += 1
            else:
                j = i
                while j < len(expr) and expr[j] not in '()+-×÷':
                    j += 1
                token = expr[i:j]
                if token:
                    tokens.append(token)
                i = j
        return tokens

    def _apply_operator(self, values: List[Fraction], ops: List[str]):
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