from typing import Callable

class comparison(Callable):
    def __init__(self, f):
        self.f = f
    
    def __call__(self, x):
        return self.f(x)
    
    def __and__(self, other):
        return comparison(lambda x: self(x) & other(x))
    
    def __or__(self, other):
        return comparison(lambda x: self(x) | other(x))
    
    def __xor__(self, other):
        return comparison(lambda x: self(x) ^ other(x))
    
    def __invert__(self):
        return comparison(lambda x: not self(x))
    
    @classmethod
    def make(cls, f):
        return cls(f)