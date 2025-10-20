#!/usr/bin/env python3
import sys
import os
from utils import parse_arguments, generate_exercises, save_to_file
from grader import ExerciseGrader


def main():
    """主程序"""
    args = parse_arguments()

    if args.n is not None:
        # 生成模式
        print(f"生成 {args.n} 个题目，数值范围: {args.r}")

        exercises = generate_exercises(args.n, args.r)

        if not exercises:
            print("无法生成有效的题目")
            sys.exit(1)

        # 保存题目和答案
        exercise_list = [ex[0] for ex in exercises]
        answer_list = [ex[1] for ex in exercises]

        save_to_file(exercise_list, "Exercises.txt")
        save_to_file(answer_list, "Answers.txt")

        print(f"题目已保存到 Exercises.txt")
        print(f"答案已保存到 Answers.txt")

    else:
        # 批改模式
        print(f"批改练习题: {args.e}")
        print(f"答案文件: {args.a}")

        grader = ExerciseGrader()

        try:
            correct_indices, wrong_indices = grader.grade_exercises(args.e, args.a)
            report = grader.generate_grade_report(correct_indices, wrong_indices)

            # 保存批改结果
            with open("Grade.txt", 'w', encoding='utf-8') as f:
                f.write(report)

            print(report)
            print("批改结果已保存到 Grade.txt")

        except Exception as e:
            print(f"批改过程中发生错误: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()