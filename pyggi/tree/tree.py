import os
import ast
import astor
import random
from abc import abstractmethod
from . import AstorEngine, XmlEngine
from ..base import AbstractProgram, AbstractEdit
from ..utils import get_file_extension

class TreeProgram(AbstractProgram):

    @classmethod
    def get_engine(cls, file_name):
        extension = get_file_extension(file_name)
        if extension in ['.py']:
            return AstorEngine
        elif extension in ['.xml']:
            return XmlEngine
        else:
            raise Exception('{} file is not supported'.format(extension))

"""
Possible Edit Operators
"""

class TreeEdit(AbstractEdit):
    @property
    def domain(self):
        return TreeProgram

#ADD
class VariableReplacement(TreeEdit):
    def __init__(self, target):
        self.target = target
        self.variable = None

    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        self.target, self.variable = engine.random_target_variable(program, self, new_contents, modification_points)

        return engine.do_replace_text(self.target, self.variable, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, method=None):
        if target_file is None:
            target_file = program.random_file()

        return cls((target_file, None))

#ADD
class CmpOperReplacement(TreeEdit):
    def __init__(self, target):
        self.target = target
        self.cmp_oper = None

    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        self.target, self.cmp_oper = engine.random_target_cmp_oper(program, self, new_contents, modification_points)

        return engine.do_replace_text(self.target, self.cmp_oper, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, method=None):
        if target_file is None:
            target_file = program.random_file()

        return cls((target_file, None))



class StmtReplacement(TreeEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        return engine.do_replace(program, self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, method='random'):
        if target_file is None:
            target_file = program.random_file()
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        assert program.engines[target_file] == program.engines[ingr_file]
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'))

class StmtInsertion(TreeEdit):
    def __init__(self, target, ingredient, direction='before'):
        assert direction in ['before', 'after']
        self.target = target
        self.ingredient = ingredient
        self.direction = direction

    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        return engine.do_insert(program, self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction=None, method='random'):
        if target_file is None:
            target_file = program.random_file()
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        assert program.engines[target_file] == program.engines[ingr_file]
        if direction is None:
            direction = random.choice(['before', 'after'])
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'),
                   direction)

class StmtDeletion(TreeEdit):
    def __init__(self, target):
        self.target = target

    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        return engine.do_delete(program, self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        if target_file is None:
            target_file = program.random_file()
        return cls(program.random_target(target_file, method))

class StmtMoving(TreeEdit):
    def __init__(self, target, ingredient, direction='before'):
        assert direction in ['before', 'after']
        self.target = target
        self.ingredient = ingredient
        self.direction = direction

    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        engine.do_insert(program, self, new_contents, modification_points)
        return engine.do_delete(program, self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction=None, method='random'):
        if target_file is None:
            target_file = program.random_file()
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        assert program.engines[target_file] == program.engines[ingr_file]
        if direction is None:
            direction = random.choice(['before', 'after'])
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'),
                   direction)
