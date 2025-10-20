import math
import random
from typing import Tuple


class Fraction:
    def __init__(self, numerator: int, denominator: int = 1):
        if denominator == 0:
            raise ValueError("分母不能为0")
        if denominator < 0:
            numerator = -numerator
            denominator = -denominator

        gcd_val = math.gcd(abs(numerator), abs(denominator))  # 修复gcd计算（取绝对值）
        self.numerator = numerator // gcd_val
        self.denominator = denominator // gcd_val

    @classmethod
    def from_string(cls, frac_str: str) -> 'Fraction':
        frac_str = frac_str.strip()
        if "'" in frac_str:
            whole_part, frac_part = frac_str.split("'", 1)
            whole = int(whole_part)
            num, denom = map(int, frac_part.split('/'))
            # 支持负数带分数解析
            if whole < 0:
                return cls(whole * denom - num, denom)
            return cls(whole * denom + num, denom)
        elif '/' in frac_str:
            num, denom = map(int, frac_str.split('/'))
            return cls(num, denom)
        else:
            return cls(int(frac_str))

    def to_string(self) -> str:
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

    # 运算符重载方法保持不变
    def __add__(self, other: 'Fraction') -> 'Fraction':
        new_num = self.numerator * other.denominator + other.numerator * self.denominator
        new_denom = self.denominator * other.denominator
        return Fraction(new_num, new_denom)

    def __sub__(self, other: 'Fraction') -> 'Fraction':
        new_num = self.numerator * other.denominator - other.numerator * self.denominator
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
        return self.numerator * other.denominator == other.numerator * self.denominator

    def __lt__(self, other: 'Fraction') -> bool:
        return self.numerator * other.denominator < other.numerator * self.denominator

    def __le__(self, other: 'Fraction') -> bool:
        return self.numerator * other.denominator <= other.numerator * self.denominator

    def is_proper_fraction(self) -> bool:
        """判断是否为真分数（绝对值小于1）"""
        return abs(self.numerator) < self.denominator

    def is_positive(self) -> bool:
        return self.numerator > 0


    @classmethod
    def random_fraction(cls, max_range: int) -> 'Fraction':
        """生成随机分数（减少0的生成概率，降低无效除法）"""
        # 降低整数中0的生成概率（从50%→20%）
        if random.random() < 0.2:
            # 生成整数（0的概率为1/3，非零为2/3）
            if random.random() < 1 / 3:
                return cls(0)
            else:
                return cls(random.randint(1, max_range - 1))  # 非零整数
        else:
            # 生成真分数（保持不变）
            denominator = random.randint(2, max_range)
            max_numerator = min(denominator - 1, max_range - 1)
            numerator = random.randint(1, max_numerator)
            return cls(numerator, denominator)