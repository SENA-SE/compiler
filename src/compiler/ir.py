from dataclasses import dataclass

@dataclass(frozen=True)
class IRVar:
    name: str
    def __repr__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Instruction():
    """Base class for IR instructions."""

@dataclass(frozen=True)
class Label(Instruction):
    name: str
    def __repr__(self) -> str:
        return self.name
@dataclass(frozen=True)
class Call(Instruction):
    fun: IRVar
    args: list[IRVar]
    dest: IRVar

@dataclass(frozen=True)
class LoadIntConst(Instruction):
    value: int
    dest: IRVar

@dataclass(frozen=True)
class Copy(Instruction):
    source: IRVar
    dest: IRVar

@dataclass(frozen=True)
class LoadBoolConst(Instruction):
    """Loads a boolean constant value to `dest`."""
    value: bool
    dest: IRVar


@dataclass(frozen=True)
class Jump(Instruction):
    """Unconditionally continues execution from the given label."""
    label: Label

@dataclass(frozen=True)
class CondJump(Instruction):
    """Continues execution from `then_label` if `cond` is true, otherwise from `else_label`."""
    condition: IRVar
    then_label: Label
    else_label: Label

