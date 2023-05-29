def extract_short_answer(full_answer) -> str:
    str_before_point = full_answer.split('.', maxsplit=1)[0]
    str_before_bracket = str_before_point.split('(', maxsplit=1)[0]
    return str_before_bracket
