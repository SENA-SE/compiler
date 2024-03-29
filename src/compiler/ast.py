
from dataclasses import dataclass, field



@dataclass
class Type:
    "basic class"

@dataclass
class FunType(Type):
    name:str

Int = FunType('Int')
Bool = FunType('Bool')
Unit = FunType('Unit')

@dataclass
class Expression:
    "Base class for expression AST nodes"
    type: Type = field(kw_only=True, default_factory=lambda: Unit)

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class Literal(Expression):
    value: int | bool

@dataclass
class BinaryOp(Expression):
    left:Expression
    operation: str
    right: Expression
    arg_variables: Expression = None

@dataclass
class IfExpression(Expression):
    condition: Expression
    then_branch: Expression
    else_branch: Expression = None  





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
    assignment: Expression = None
    variable_type: Type = None

@dataclass
class Function(Expression):
    name: str
    args: list[VariableDeclaration]
    return_type: Type = None
    body: Block = None

@dataclass
class LibraryFunctionCalled(Expression):
    name: str
    args: list[VariableDeclaration]
    return_type: Type = None
    # operation: Expression = None

@dataclass
class FunctionCalled(Expression):
    name: str
    return_type: Type = None
    body: Block = None
    arg_variables: list[VariableDeclaration] = None
    
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

@dataclass
class Break(Expression):
    "break"
    test: str=None

@dataclass
class Continue(Expression):
    "continue"

@dataclass
class Return(Expression):
    value: Expression

@dataclass
class PointerType(Type):
    base_type: Type
@dataclass
class AddressOf(Expression):
    operand: Expression

@dataclass
class Dereference(Expression):
    operand: Expression

