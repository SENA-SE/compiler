
from dataclasses import dataclass


@dataclass
class Expression:
    "Base class for expression AST nodes"

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class Literal(Expression):
    value: int

@dataclass
class BinaryOp(Expression):
    left:Expression
    operation: str
    right: Expression

@dataclass
class IfExpression(Expression):
    condition: Expression
    then_branch: Expression
    else_branch: Expression = None  

@dataclass
class Function(Expression):
    name: str
    args: list[Expression]

@dataclass
class UnaryOp(Expression):
    operation: str
    right: Expression

@dataclass
class Block(Expression):
    expressions: list[Expression]

    def ends_with_block(self) -> bool:
        return True
    
@dataclass
class VariableDeclaration(Expression):
    name: str
    assignment: Expression

@dataclass
class WhileExpression(Expression):
    condition: Expression
    do: Expression

@dataclass
class SymTab():
    variables: dict

@dataclass
class HierarchicalSymTab(SymTab):
    parent: SymTab