from flask import Flask, request, render_template
import re

app = Flask(__name__)

# Analizador Léxico
def lexical_analysis(code):
    tokens = []
    errors = []
    token_specification = [
        ('FOR', r'\bfor\b'),
        ('INT', r'\bint\b'),
        ('PRINTLN', r'\bSystem\.out\.println\b'),
        ('NUMBER', r'\b\d+\b'),
        ('ID', r'\b[a-zA-Z_]\w*\b'),
        ('OP', r'[+\-*/]'),
        ('RELOP', r'[<>]=?|==|!='),
        ('ASSIGN', r'='),
        ('END', r';'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACE', r'{'),
        ('RBRACE', r'}'),
        ('STRING', r'\".*?\"'),
        ('SKIP', r'[ \t\r\n]+'),  # Saltar espacios, tabs y nuevas líneas
        ('MISMATCH', r'.')    # Cualquier otro carácter
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    line_num = 1
    line_start = 0

    # Para validar el punto y coma después de System.out.println
    inside_println = False

    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == 'NUMBER':
            value = int(value)
        elif kind == 'ID' and value in ('for', 'int', 'System.out.println'):
            kind = value.upper()
        elif kind == 'SKIP':
            if '\n' in value:
                line_num += value.count('\n')
                line_start = mo.end()
            continue
        elif kind == 'MISMATCH':
            errors.append(f'Error léxico: {value!r} inesperado en la línea {line_num}, columna {column}')
            continue
        
        tokens.append((kind, value, line_num, column))

        # Comprobación especial para el punto y coma después de System.out.println
        if kind == 'PRINTLN':
            inside_println = True
        elif inside_println and kind == 'RPAREN':
            inside_println = False
            # Verificar el próximo token si es punto y coma
            next_pos = mo.end()
            if next_pos < len(code) and code[next_pos] != ';':
                errors.append(f'Error sintáctico: Falta punto y coma después de System.out.println en la línea {line_num}, columna {column + 1}')
        
    return tokens, errors

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        code = request.form['code']
        tokens, errors = lexical_analysis(code)
        return render_template('index.html', tokens=tokens, errors=errors, code=code)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

