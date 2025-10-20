from typing import List, Tuple
from fraction import Fraction
from expression import Expression


class ExerciseGrader:
    def __init__(self):
        self.expression_parser = Expression()

    def grade_exercises(self, exercise_file: str, answer_file: str) -> Tuple[List[int], List[int]]:
        """批改练习题"""
        correct_indices = []
        wrong_indices = []

        try:
            with open(exercise_file, 'r', encoding='utf-8') as ex_file, \
                    open(answer_file, 'r', encoding='utf-8') as ans_file:

                exercises = ex_file.readlines()
                answers = ans_file.readlines()

                for i, (exercise, answer) in enumerate(zip(exercises, answers), 1):
                    exercise = exercise.strip()
                    answer = answer.strip()

                    if not exercise or not answer:
                        continue

                    # 提取表达式（去掉等号）
                    if '=' in exercise:
                        expr = exercise.split('=')[0].strip()
                    else:
                        expr = exercise.strip()

                    try:
                        # 计算表达式值
                        computed_result = self.expression_parser.evaluate_expression(expr)

                        # 解析答案
                        expected_result = Fraction.from_string(answer)

                        # 比较结果
                        if computed_result == expected_result:
                            correct_indices.append(i)
                        else:
                            wrong_indices.append(i)
                    except Exception:
                        wrong_indices.append(i)

        except FileNotFoundError as e:
            raise FileNotFoundError(f"文件未找到: {e}")
        except Exception as e:
            raise Exception(f"批改过程中发生错误: {e}")

        return correct_indices, wrong_indices

    def generate_grade_report(self, correct_indices: List[int], wrong_indices: List[int]) -> str:
        """生成批改报告"""
        correct_str = ", ".join(map(str, correct_indices))
        wrong_str = ", ".join(map(str, wrong_indices))

        report = f"Correct: {len(correct_indices)} ({correct_str})\n"
        report += f"Wrong: {len(wrong_indices)} ({wrong_str})"

        return report