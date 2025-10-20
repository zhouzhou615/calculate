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

        # 尝试多种编码读取文件（优先UTF-8，其次GBK）
        encodings = ['utf-8', 'gbk', 'gb2312']

        def read_file_with_encoding(file_path: str) -> List[str]:
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.readlines()
                except UnicodeDecodeError:
                    continue
            raise Exception(f"文件 {file_path} 无法用以下编码解析: {encodings}")

        try:
            # 使用容错编码方式读取文件
            exercises = read_file_with_encoding(exercise_file)
            answers = read_file_with_encoding(answer_file)

            for i, (exercise, answer) in enumerate(zip(exercises, answers), 1):
                # 后续逻辑保持不变...
                exercise = exercise.strip()
                answer = answer.strip()

                if not exercise or not answer:
                    continue

                if '=' in exercise:
                    expr = exercise.split('=')[0].strip()
                else:
                    expr = exercise.strip()

                try:
                    computed_result = self.expression_parser.evaluate_expression(expr)
                    expected_result = Fraction.from_string(answer)

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