import unittest
import tempfile
import os
from fraction import Fraction
from expression import Expression
from validator import ExpressionValidator
from grader import ExerciseGrader
from utils import parse_arguments, generate_exercises, save_to_file
import sys
from io import StringIO


class TestFraction(unittest.TestCase):
    """测试分数类的各种功能"""

    def test_init(self):
        """测试分数初始化"""
        f = Fraction(2, 4)
        self.assertEqual(f.numerator, 1)
        self.assertEqual(f.denominator, 2)

        f = Fraction(-3, -6)
        self.assertEqual(f.numerator, 1)
        self.assertEqual(f.denominator, 2)

        f = Fraction(-2, 4)
        self.assertEqual(f.numerator, -1)
        self.assertEqual(f.denominator, 2)

        with self.assertRaises(ValueError):
            Fraction(1, 0)

    def test_from_string(self):
        """测试从字符串创建分数"""
        f = Fraction.from_string("3/5")
        self.assertEqual(f.numerator, 3)
        self.assertEqual(f.denominator, 5)

        f = Fraction.from_string("2'3/8")
        self.assertEqual(f.numerator, 19)
        self.assertEqual(f.denominator, 8)

        f = Fraction.from_string("5")
        self.assertEqual(f.numerator, 5)
        self.assertEqual(f.denominator, 1)

    def test_to_string(self):
        """测试分数转换为字符串"""
        f = Fraction(3, 5)
        self.assertEqual(f.to_string(), "3/5")

        f = Fraction(19, 8)
        self.assertEqual(f.to_string(), "2'3/8")

        f = Fraction(5, 1)
        self.assertEqual(f.to_string(), "5")

        f = Fraction(6, 4)
        self.assertEqual(f.to_string(), "1'1/2")

    def test_arithmetic_operations(self):
        """测试分数的四则运算"""
        a = Fraction(1, 2)
        b = Fraction(1, 3)

        # 加法
        self.assertEqual((a + b).to_string(), "5/6")

        # 减法
        self.assertEqual((a - b).to_string(), "1/6")

        # 乘法
        self.assertEqual((a * b).to_string(), "1/6")

        # 除法
        self.assertEqual((a / b).to_string(), "1'1/2")

    def test_comparison(self):
        """测试分数比较"""
        a = Fraction(1, 2)
        b = Fraction(1, 3)
        c = Fraction(2, 4)

        self.assertTrue(a > b)
        self.assertTrue(b < a)
        self.assertTrue(a == c)
        self.assertTrue(a != b)

    def test_is_proper_fraction(self):
        """测试是否为真分数"""
        self.assertTrue(Fraction(1, 2).is_proper_fraction())
        self.assertFalse(Fraction(3, 2).is_proper_fraction())
        self.assertFalse(Fraction(5, 1).is_proper_fraction())

    def test_is_positive(self):
        """测试是否为正数"""
        self.assertTrue(Fraction(1, 2).is_positive())
        self.assertFalse(Fraction(-1, 2).is_positive())
        self.assertFalse(Fraction(0, 1).is_positive())

    def test_random_fraction(self):
        """测试随机分数生成"""
        for _ in range(100):
            f = Fraction.random_fraction(10)
            if f.denominator == 1:  # 整数
                self.assertTrue(0 <= f.numerator < 10)
            else:  # 真分数
                self.assertTrue(1 <= f.numerator < f.denominator <= 10)


class TestExpression(unittest.TestCase):
    """测试表达式生成和计算"""

    def setUp(self):
        self.expression = Expression()

    def test_generate_expression(self):
        """测试生成表达式"""
        for _ in range(100):
            expr, result = self.expression.generate_expression(10)
            self.assertIsInstance(expr, str)
            self.assertIsInstance(result, Fraction)
            # 检查运算符数量不超过3个
            op_count = sum(1 for c in expr if c in ['+', '-', '×', '÷'])
            self.assertLessEqual(op_count, 3)

    def test_evaluate_expression(self):
        """测试表达式计算"""
        test_cases = [
            ("1 + 2", Fraction(3)),
            ("3 - 1", Fraction(2)),
            ("2 × 3", Fraction(6)),
            ("6 ÷ 2", Fraction(3)),
            ("1/2 + 1/3", Fraction(5, 6)),
            ("1 - 1/2", Fraction(1, 2)),
            ("2 × 1/3", Fraction(2, 3)),
            ("1/2 ÷ 3", Fraction(1, 6)),
            ("(1 + 2) × 3", Fraction(9)),
            ("1 + (2 × 3)", Fraction(7)),
            ("2'1/2 + 1'1/3", Fraction(23, 6)),
        ]

        for expr, expected in test_cases:
            result = self.expression.evaluate_expression(expr)
            self.assertEqual(result, expected, f"表达式 {expr} 计算错误")

    def test_needs_parentheses(self):
        """测试是否需要添加括号"""
        test_cases = [
            ("1 + 2", "+", True, False),
            ("1 × 2", "+", True, True),
            ("1 + 2", "×", True, True),
            ("1 × 2", "×", True, False),
            ("1 - 2", "-", False, True),
            ("1 ÷ 2", "÷", False, True),
        ]

        for expr, parent_op, is_left, expected in test_cases:
            result = self.expression._needs_parentheses(expr, parent_op, is_left)
            self.assertEqual(result, expected,
                             f"表达式 {expr} 对于运算符 {parent_op} 判断错误")

    def test_tokenize(self):
        """测试表达式分词"""
        test_cases = [
            ("1 + 2 × 3", ["1", "+", "2", "×", "3"]),
            ("(1/2 + 3) ÷ 4", ["(", "1/2", "+", "3", ")", "÷", "4"]),
            ("2'3/8 - 1", ["2'3/8", "-", "1"]),
        ]

        for expr, expected in test_cases:
            tokens = self.expression._tokenize(expr)
            self.assertEqual(tokens, expected, f"表达式 {expr} 分词错误")


class TestValidator(unittest.TestCase):
    """测试表达式验证器"""

    def setUp(self):
        self.validator = ExpressionValidator()

    def test_is_duplicate(self):
        """测试表达式重复判断"""
        expr1 = "1 + 2"
        expr2 = "2 + 1"
        expr3 = "3 - 1"

        self.assertFalse(self.validator.is_duplicate(expr1))
        self.validator.add_expression(expr1)
        self.assertTrue(self.validator.is_duplicate(expr2))  # 加法交换律视为重复
        self.assertFalse(self.validator.is_duplicate(expr3))

    def test_normalize_expression(self):
        """测试表达式规范化"""
        test_cases = [
            ("1 + 2", "1+2"),
            ("2 + 1", "1+2"),  # 加法交换后规范化结果相同
            ("3 × 4", "3×4"),
            ("4 × 3", "3×4"),  # 乘法交换后规范化结果相同
            ("5 - 3", "5-3"),
            ("3 - 5", "3-5"),  # 减法不交换
        ]

        for expr, expected in test_cases:
            normalized = self.validator._normalize_expression(expr)
            self.assertEqual(normalized, expected, f"表达式 {expr} 规范化错误")

    def test_validate_constraints(self):
        """测试表达式约束验证"""
        expr1 = "1 + 2 + 3 + 4"  # 3个运算符，符合要求
        expr2 = "1 + 2 + 3 + 4 + 5"  # 4个运算符，不符合要求
        result = Fraction(1)

        self.assertTrue(self.validator.validate_constraints(expr1, result))
        self.assertFalse(self.validator.validate_constraints(expr2, result))

        # 测试重复检查
        self.validator.add_expression(expr1)
        self.assertFalse(self.validator.validate_constraints(expr1, result))


class TestGrader(unittest.TestCase):
    """测试批改功能"""

    def setUp(self):
        self.grader = ExerciseGrader()
        self.test_exercises = [
            "1 + 2 = ",
            "3 - 1 = ",
            "2 × 3 = ",
            "6 ÷ 2 = ",
            "1/2 + 1/3 = ",
        ]
        self.test_answers = [
            "3",
            "2",
            "6",
            "3",
            "5/6",
        ]
        self.wrong_answers = [
            "4",  # 错误
            "2",  # 正确
            "5",  # 错误
            "3",  # 正确
            "1/2",  # 错误
        ]

    def test_grade_exercises(self):
        """测试批改功能"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as ex_file, \
                tempfile.NamedTemporaryFile(mode='w', delete=False) as ans_file:
            ex_file.write('\n'.join(self.test_exercises))
            ans_file.write('\n'.join(self.test_answers))
            ex_filename = ex_file.name
            ans_filename = ans_file.name

        # 测试全对的情况
        correct, wrong = self.grader.grade_exercises(ex_filename, ans_filename)
        self.assertEqual(len(correct), 5)
        self.assertEqual(len(wrong), 0)
        self.assertEqual(correct, [1, 2, 3, 4, 5])

        # 测试有错误的情况
        with open(ans_filename, 'w') as f:
            f.write('\n'.join(self.wrong_answers))

        correct, wrong = self.grader.grade_exercises(ex_filename, ans_filename)
        self.assertEqual(len(correct), 2)
        self.assertEqual(len(wrong), 3)
        self.assertEqual(correct, [2, 4])
        self.assertEqual(wrong, [1, 3, 5])

        # 清理临时文件
        os.unlink(ex_filename)
        os.unlink(ans_filename)

    def test_generate_grade_report(self):
        """测试生成报告"""
        correct = [1, 3, 5]
        wrong = [2, 4]
        report = self.grader.generate_grade_report(correct, wrong)
        expected = "Correct: 3 (1, 3, 5)\nWrong: 2 (2, 4)"
        self.assertEqual(report, expected)


class TestUtils(unittest.TestCase):
    """测试工具函数"""

    def test_parse_arguments(self):
        """测试命令行参数解析"""
        # 测试生成模式
        sys.argv = ["main.py", "-n", "10", "-r", "5"]
        args = parse_arguments()
        self.assertEqual(args.n, 10)
        self.assertEqual(args.r, 5)
        self.assertIsNone(args.e)
        self.assertIsNone(args.a)

        # 测试批改模式
        sys.argv = ["main.py", "-e", "ex.txt", "-a", "ans.txt"]
        args = parse_arguments()
        self.assertIsNone(args.n)
        self.assertIsNone(args.r)
        self.assertEqual(args.e, "ex.txt")
        self.assertEqual(args.a, "ans.txt")

        # 测试错误参数（缺少-r）
        sys.argv = ["main.py", "-n", "10"]
        with self.assertRaises(SystemExit):
            parse_arguments()

        # 测试错误参数（缺少-a）
        sys.argv = ["main.py", "-e", "ex.txt"]
        with self.assertRaises(SystemExit):
            parse_arguments()

    def test_generate_exercises(self):
        """测试生成练习题"""
        # 测试生成少量题目
        exercises = generate_exercises(10, 10)
        self.assertEqual(len(exercises), 10)

        # 测试生成大量题目
        exercises = generate_exercises(10000, 10)
        self.assertEqual(len(exercises), 10000)

        # 检查题目格式
        for expr, ans in exercises:
            self.assertTrue(expr.endswith(" = "))
            self.assertIsInstance(ans, str)

    def test_save_to_file(self):
        """测试保存文件"""
        data = ["line1", "line2", "line3"]
        with tempfile.NamedTemporaryFile(mode='r', delete=False) as f:
            filename = f.name

        save_to_file(data, filename)

        with open(filename, 'r') as f:
            content = f.read().splitlines()

        self.assertEqual(content, data)
        os.unlink(filename)


class TestMainFunctionality(unittest.TestCase):
    """测试整体功能流程"""

    def test_full_workflow(self):
        """测试从生成题目到批改的完整流程"""
        # 生成题目
        num_exercises = 10
        max_range = 10
        exercises = generate_exercises(num_exercises, max_range)

        # 保存题目和答案到临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as ex_file, \
                tempfile.NamedTemporaryFile(mode='w', delete=False) as ans_file:
            ex_filename = ex_file.name
            ans_filename = ans_file.name

            exercise_list = [ex[0] for ex in exercises]
            answer_list = [ex[1] for ex in exercises]

            save_to_file(exercise_list, ex_filename)
            save_to_file(answer_list, ans_filename)

        # 批改题目（应该全对）
        grader = ExerciseGrader()
        correct, wrong = grader.grade_exercises(ex_filename, ans_filename)
        self.assertEqual(len(correct), num_exercises)
        self.assertEqual(len(wrong), 0)

        # 清理临时文件
        os.unlink(ex_filename)
        os.unlink(ans_filename)


if __name__ == '__main__':
    unittest.main()