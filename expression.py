import random
import re
from typing import List, Tuple
from fraction import Fraction


class Expression:
    def __init__(self):
        self.operators = ['+', '-', '×', '÷']
        self.priority = {'+': 1, '-': 1, '×': 2, '÷': 2}
        # 新增：预编译分词正则，替代循环分词
        self.token_pattern = re.compile(r'(\d+/?\d*\'?\d*|\d+|\(|\)|[+\-×÷])')

    def generate_expression(self, max_range: int, max_operators: int = 3) -> Tuple[str, Fraction]:
        """生成表达式（主动规避无效运算符，减少重试）"""
        while True:
            try:
                num_operators = random.randint(1, max_operators)
                num_operands = num_operators + 1

                # 生成操作数（优先非零值，减少除法无效性）
                operands = [Fraction.random_fraction(max_range) for _ in range(num_operands)]
                # 生成符合约束的运算符（核心优化）
                operators = self._generate_valid_operators(operands, num_operators)

                # 构建表达式树
                expr_str, result = self._build_expression(operands, operators)

                if self._is_valid_expression(expr_str, result):
                    return expr_str, result
            except (ValueError, ZeroDivisionError):
                continue

    def _generate_valid_operators(self, operands: List[Fraction], num_ops: int) -> List[str]:
        """主动生成符合约束的运算符，减少后续异常"""
        operators = []
        for i in range(num_ops):
            left, right = operands[i], operands[i+1]
            # 20%概率尝试减法（确保left >= right）
            if random.random() < 0.2 and left >= right:
                operators.append('-')
                continue
            # 20%概率尝试除法（确保结果为真分数）
            if random.random() < 0.2:
                if right.numerator != 0:
                    div_result = left / right
                    if div_result.is_proper_fraction():
                        operators.append('÷')
                        continue
            # 默认使用加法/乘法（无约束风险）
            operators.append(random.choice(['+', '×']))
        # 若运算符数量不足，补充（应对上述条件均不满足的情况）
        while len(operators) < num_ops:
            operators.append(random.choice(['+', '×']))
        return operators

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
        # 如果表达式已经是单个数字，不需要括号
        if not any(op in expr for op in self.operators):
            return False

        # 提取子表达式的主要运算符
        sub_op = None
        for op in self.operators:
            if self._is_main_operator(expr, op):
                sub_op = op
                break

        if sub_op is None:
            return False

        # 比较优先级
        if self.priority[sub_op] < self.priority[parent_op]:
            return True

        # 相同优先级时的特殊情况
        if self.priority[sub_op] == self.priority[parent_op]:
            # 对于 + 和 ×，左操作数不需要括号，右操作数需要括号
            if parent_op in ['+', '×']:
                return not is_left
            # 对于 - 和 ÷，右操作数总是需要括号
            elif parent_op in ['-', '÷']:
                return not is_left

        # 如果子表达式优先级更高，不需要括号
        return False

    def _is_main_operator(self, expr: str, op: str) -> bool:
        """检查运算符是否是表达式的主要（最外层）运算符"""
        # 移除最外层的括号（如果有）
        stripped_expr = expr.strip()
        if stripped_expr.startswith('(') and stripped_expr.endswith(')'):
            # 检查括号是否匹配
            bracket_count = 0
            for i, char in enumerate(stripped_expr):
                if char == '(':
                    bracket_count += 1
                elif char == ')':
                    bracket_count -= 1
                    if bracket_count == 0 and i < len(stripped_expr) - 1:
                        # 括号没有包围整个表达式
                        break
            if bracket_count == 0:
                stripped_expr = stripped_expr[1:-1].strip()

        # 查找不在括号内的运算符
        bracket_count = 0
        for i, char in enumerate(stripped_expr):
            if char == '(':
                bracket_count += 1
            elif char == ')':
                bracket_count -= 1
            elif bracket_count == 0 and char == op:
                # 检查这个运算符是否真的是主要运算符
                # 确保它不在其他运算符的范围内
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

    # 优化分词方法：用预编译正则替代循环
    def _tokenize(self, expr: str) -> List[str]:
        expr = expr.replace(' ', '')
        return [t for t in self.token_pattern.findall(expr) if t]  # 过滤空字符串


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