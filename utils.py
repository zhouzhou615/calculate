import argparse
import sys
from typing import List, Tuple
from fraction import Fraction
from expression import Expression
from validator import ExpressionValidator


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='小学四则运算题目生成器')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-n', type=int, help='生成题目的数量')
    group.add_argument('-e', type=str, help='练习题文件路径')

    parser.add_argument('-r', type=int, help='数值范围')
    parser.add_argument('-a', type=str, help='答案文件路径')

    args = parser.parse_args()

    # 验证参数
    if args.n is not None and args.r is None:
        parser.error("使用 -n 参数时必须指定 -r 参数")

    if args.e is not None and args.a is None:
        parser.error("使用 -e 参数时必须指定 -a 参数")

    return args


def generate_exercises(num_exercises: int, max_range: int) -> List[Tuple[str, str]]:
    """生成练习题和答案"""
    exercises = []
    expression_gen = Expression()
    validator = ExpressionValidator()

    generated_count = 0
    attempt_count = 0
    max_attempts = num_exercises * 100  # 防止无限循环

    while generated_count < num_exercises and attempt_count < max_attempts:
        attempt_count += 1

        try:
            expr, result = expression_gen.generate_expression(max_range)

            # 验证表达式
            if validator.validate_constraints(expr, result):
                # 检查是否重复
                if not validator.is_duplicate(expr):
                    exercise_str = f"{expr} = "
                    answer_str = result.to_string()

                    exercises.append((exercise_str, answer_str))
                    validator.add_expression(expr)
                    generated_count += 1
        except (ValueError, ZeroDivisionError):
            continue

    if generated_count < num_exercises:
        print(f"警告: 只生成了 {generated_count} 个有效题目")

    return exercises


def save_to_file(data: List[str], filename: str):
    """保存数据到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for line in data:
                f.write(line + '\n')
    except Exception as e:
        print(f"保存文件 {filename} 时出错: {e}")
        sys.exit(1)