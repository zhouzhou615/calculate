import math
import random
from typing import Tuple, Union


class Fraction:
    def __init__(self, numerator: int, denominator: int = 1):
        if denominator == 0:
            raise ValueError("分母不能为0")
        if denominator < 0:
            numerator = -numerator
            denominator = -denominator

        gcd_val = math.gcd(numerator, denominator)
        self.numerator = numerator // gcd_val
        self.denominator = denominator // gcd_val

        # 确保分母为正
        if self.denominator < 0:
            self.numerator = -self.numerator
            self.denominator = -self.denominator

    @classmethod
    def from_string(cls, frac_str: str) -> 'Fraction':
        """从字符串创建分数，支持 '3/5' 和 '2'3/8' 格式"""
        if "'" in frac_str:
            # 带分数格式
            whole_part, frac_part = frac_str.split("'")
            whole = int(whole_part)
            num, denom = map(int, frac_part.split('/'))
            return cls(whole * denom + num, denom)
        elif '/' in frac_str:
            # 真分数格式
            num, denom = map(int, frac_str.split('/'))
            return cls(num, denom)
        else:
            # 整数格式
            return cls(int(frac_str))

    def to_string(self) -> str:
        """转换为字符串表示"""
        if self.denominator == 1:
            return str(self.numerator)

        if abs(self.numerator) < self.denominator:
            return f"{self.numerator}/{self.denominator}"
        else:
            whole = self.numerator // self.denominator
            remainder = abs(self.numerator) % self.denominator
            if remainder == 0:
                return str(whole)
            else:
                return f"{whole}'{remainder}/{self.denominator}"

    def __add__(self, other: 'Fraction') -> 'Fraction':
        new_num = (self.numerator * other.denominator +
                   other.numerator * self.denominator)
        new_denom = self.denominator * other.denominator
        return Fraction(new_num, new_denom)

    def __sub__(self, other: 'Fraction') -> 'Fraction':
        new_num = (self.numerator * other.denominator -
                   other.numerator * self.denominator)
        new_denom = self.denominator * other.denominator
        return Fraction(new_num, new_denom)

    def __mul__(self, other: 'Fraction') -> 'Fraction':
        new_num = self.numerator * other.numerator
        new_denom = self.denominator * other.denominator
        return Fraction(new_num, new_denom)

    def __truediv__(self, other: 'Fraction') -> 'Fraction':
        if other.numerator == 0:
            raise ValueError("除数不能为0")
        new_num = self.numerator * other.denominator
        new_denom = self.denominator * other.numerator
        return Fraction(new_num, new_denom)

    def __eq__(self, other: 'Fraction') -> bool:
        return (self.numerator * other.denominator ==
                other.numerator * self.denominator)

    def __lt__(self, other: 'Fraction') -> bool:
        return (self.numerator * other.denominator <
                other.numerator * self.denominator)

    def __le__(self, other: 'Fraction') -> bool:
        return (self.numerator * other.denominator <=
                other.numerator * self.denominator)

    def is_proper_fraction(self) -> bool:
        """判断是否为真分数（绝对值小于1）"""
        return abs(self.numerator) < self.denominator

    def is_positive(self) -> bool:
        """判断是否为正数"""
        return self.numerator > 0

    @classmethod
    def random_fraction(cls, max_range: int) -> 'Fraction':
        """生成随机分数"""
        # 50%概率生成整数，50%概率生成真分数
        if random.random() < 0.5:
            return cls(random.randint(0, max_range - 1))
        else:
            denominator = random.randint(2, max_range)
            numerator = random.randint(1, denominator - 1)
            return cls(numerator, denominator)