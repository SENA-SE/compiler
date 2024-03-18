
# CSM14204 Compilers Project, Spring 2024

This is my implementation of the compiler project for `CSM14204 Compilers, spring 2024` . Here is a brief overview of its structure, installation process, features and limitations, as well as guidance on utilizing its unit tests.


- [Setup](#setup)
- [Running](#running)
- [Structure](#structure)
- [Features](#features)
- [Unit Tests](#unit_tests)
- [Issues](#issues)

## Setup
**Requirements:**
 - [Pyenv](https://github.com/pyenv/pyenv) for installing Python 3.11+
 - Recommended installation method: the "automatic installer"
i.e. `curl https://pyenv.run | bash`

 - [Poetry](https://python-poetry.org/) for installing dependencies
 - Recommended installation method: the "official installer"
i.e. `curl -sSL https://install.python-poetry.org | python3 -`

**Install dependencies:**
 - Install Python 3.11.7
`pyenv install`

- Install dependencies specified in `pyproject.toml`
`poetry install`


## Structure

```
└── compiler_project
    ├── src                 # source files
    ├── tests               # unit tests
    ├── README.md
    └── 
```

## Running the compiler

Use direct input to run the compiler, or run the compiler on a source code file:
`./compiler.sh <command> <<< [input]`
```
COMMANDS:
    interpret, ir, asm, compile

USAGE:
	./compiler.sh interpret <<< [input]
	./compiler.sh ir <<< [input]
	./compiler.sh asm <<< [input]
	./compiler.sh compile <<< [input] && [compiled filename]

USAGE EXAMPLES:
	✅./compiler.sh ir <<< 'if 2>1 then print_int(2*(2+3)) else print_int(3*3)' 
	✅./compiler.sh compile <<< 'var a = -1; while a<2 do a=a+1; print_int(a)' && ./compiled_program
	✅./compiler.sh interpret <<< 'fun square(x: Int): Int {
		    return x * x;
		}

		fun vec_len_squared(x: Int, y: Int): Int {
		    return square(x) + square(y);
		}

		fun print_int_twice(x: Int) {
		    print_int(x);
		    print_int(x);
		}

		print_int_twice(vec_len_squared(3, 4));'
	
```

## Features

Implemented features so far:
- Integer literals
- Boolean literals
- Unary operators `-` and `not`
- Binary operators `+`, `-`, `*`, `/`, `%`, `==`, `!=`, `<`, `<=`, `>`, `>=`, `and`, `or`,`=`
--   Operator  `=`  is right-associative.
--   All other operators are left-associative.
--   With precedence
- Builtin functions `print_int`,  `print_bool`
-   Parentheses
- Blocks of statements
- Variables (typed and untyped)
--   Untyped variable declaration:  `var ID = E`  where  `ID`  is an identifier.
--   Typed variable declaration:  `var ID: T = E`  where  `ID`  is an identifier and  `T`  is a type expression
- Assignments
- if-then and if-then-else
- While loops
- Functions
- `break` and `continue`


## Unit Tests

To run unit tests:
	`poetry  run  pytest  -vv  tests/`



## Issues
  
 Currently, functions passed as arguments during function calls cannot be compiled, although they can be executed without any issue with interpreter. Here's an example:
```
fun square(x: Int): Int {
    return x * x;
}
print_int(square(2))
```
When using the command `interpret` , the output on the console is `4`. However, when attempting to compile, although the intermediate representation (IR) instructions appear to be reasonable, for some reason compilation still fails.