# Calculator

**A small arithmetic CLI—and the working project for [Workbench](../README.md).**

Evaluate whitespace-separated numbers and operators. Multiplication and division take precedence over addition and subtraction; operators with equal precedence are evaluated from left to right.

## Run an expression

From the repository root:

```bash
uv run calculator/main.py "3 + 5 * 2"
```

```json
{
  "expression": "3 + 5 * 2",
  "result": 13
}
```

Supported operators: **`+` · `-` · `*` · `/`**. Separate every number and operator with spaces. Parentheses are not supported. Invalid tokens, missing operands, and division by zero produce an error message.

## How it works

| Source | Responsibility |
| --- | --- |
| `main.py` | Accept an expression and report errors |
| `pkg/calculator.py` | Tokenize input and evaluate with value/operator stacks |
| `pkg/render.py` | Format the result as JSON |
| `tests.py` | Calculator unit tests |

Run the calculator tests from its directory:

```bash
cd calculator
python3 tests.py
```

The surrounding agent can read, modify, and execute files here. This README describes the calculator independently of any model or API service.
