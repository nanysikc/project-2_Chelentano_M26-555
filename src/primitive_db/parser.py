import shlex


def parse_value(value: str):
    """Преобразует текст в значение Python."""

    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    try:
        return int(value)

    except ValueError:
        pass

    if value == "true":
        return True
    if value == "false":
        return False
    
    raise ValueError(f"Некорректное значение: {value}")


def parse_values(values_text: str) -> list:
    """Преобразует список значений команды в данные Python."""
    values_text = values_text.strip()

    if not values_text.startswith("(") or not values_text.endswith(")"):
        raise ValueError("Значения должны быть заключены в скобки")

    content = values_text[1:-1]

    lexer = shlex.shlex(content, posix=False)
    lexer.whitespace = ","
    lexer.whitespace_split = True

    values = []

    for token in lexer:
        values.append(parse_value(token.strip()))

    return values


if __name__ == "__main__":
    print(parse_values('("Maria", 25, true)'))
    print(parse_values('("Ivanov, Petr", 30, false)'))