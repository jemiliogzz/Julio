"""
Módulo de Generadores de Preguntas
===================================

Este módulo contiene los generadores de preguntas para cada tema del sistema.
Puede ser importado tanto por quizzes individuales como por la simulación de examen.

Cada función generadora debe:
- Recibir: seed (int), dificultad (int)
- Retornar: dict con estructura estándar de pregunta
"""

import random


# ==================== ESTRUCTURA ESTÁNDAR DE PREGUNTA ====================
"""
{
    'pregunta': str,              # LaTeX o texto de la pregunta
    'respuesta_correcta': str,    # Respuesta correcta
    'tipo': str,                  # 'texto', 'radio', o 'slider'
    'opciones': list,             # Solo para tipo 'radio' (opcional)
    'rango': tuple,               # Solo para tipo 'slider' (min, max) (opcional)
    'tema_id': int,               # ID del tema
    'instruccion': str            # Instrucciones adicionales (opcional)
}
"""


# ==================== GENERADORES POR TEMA ====================

def generar_pregunta_tema_1(seed, dificultad):
    """Tema 1: Sumas"""
    random.seed(seed)
    num = random.randint(-25, 25)
    res = num
    latex_str = str(num)
    for j in range(3):
        num = random.randint(-25, 25)
        if num >= 0:
            latex_str += ' +'
        latex_str += str(num) + ' '
        res += num
    latex_str += '='
    return {
        'pregunta': latex_str,
        'respuesta_correcta': str(res),
        'tipo': 'texto',
        'tema_id': 1
    }


def generar_pregunta_tema_2(seed, dificultad):
    """Tema 2: Multiplicación y División"""
    random.seed(seed)
    operacion = random.choice(['/', '*'])
    num = random.randint(-10, 10)
    
    if operacion == '/':
        if num == 0:
            num += 1
        res = random.randint(-10, 11)
        latex_str = str(num * res) + r'\div' + str(num)
    else:
        latex_str = str(num) + '*'
        res = num
        num = random.randint(-10, 11)
        latex_str += str(num)
        res *= num
    
    latex_str += '='
    return {
        'pregunta': latex_str,
        'respuesta_correcta': str(res),
        'tipo': 'texto',
        'tema_id': 2
    }


def generar_pregunta_tema_3(seed, dificultad):
    """Tema 3: Gráfica en recta numérica (slider)"""
    random.seed(seed)
    operacion = random.choice(['/', '*'])
    
    if operacion == '/':
        num = random.randint(-5, 4)
        if num == 0:
            num += 1
        res = random.randint(-10, 10)
        latex_str = str(num * res) + r'\div' + str(num)
    else:
        res = random.randint(-5, 5)
        latex_str = str(res)
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': str(res),
        'tipo': 'slider',
        'rango': (-10, 10),
        'tema_id': 3
    }


def generar_pregunta_tema_4(seed, dificultad):
    """Tema 4: Desigualdades"""
    random.seed(seed)
    desigualdad = random.choice(['>', '<', "="])
    operacion = random.choice(['/', '*', '-', '-', '-'])
    num = random.randint(-5, 4)
    
    latex_str = ''
    res_temp = num
    if operacion == '/':
        if num == 0:
            num += 1
        res_temp = random.randint(-10, 10)
        latex_str = str(num * res_temp) + r'\div'
    elif operacion == '*':
        latex_str = str(num) + '*'
        num = random.randint(-5, 5)
        res_temp *= num
    
    latex_str += str(num) + desigualdad
    num = random.randint(-15, 15)
    latex_str += str(num)
    
    if desigualdad == '>':
        res = 'Verdadero' if res_temp > num else 'Falso'
    elif desigualdad == '<':
        res = 'Verdadero' if res_temp < num else 'Falso'
    else:
        res = 'Verdadero' if res_temp == num else 'Falso'
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': res,
        'tipo': 'radio',
        'opciones': ['Verdadero', 'Falso'],
        'tema_id': 4
    }


def generar_pregunta_tema_5(seed, dificultad):
    """Tema 5: Fracciones"""
    random.seed(seed)
    operador = random.choice(['<', '<', '>', '>', '='])
    fracs = []
    for j in range(4):
        num = random.randint(-5, 5)
        if num == 0:
            num = 1
        fracs.append(num)
    
    latex_str = r'\frac{' + str(fracs[0]) + '}{' + str(fracs[1]) + '}' + operador + r'\frac{' + str(fracs[2]) + '}{' + str(fracs[3]) + '}'
    
    if operador == '>':
        res = 'Verdadero' if (fracs[0] / fracs[1]) > (fracs[2] / fracs[3]) else 'Falso'
    elif operador == '<':
        res = 'Verdadero' if (fracs[0] / fracs[1]) < (fracs[2] / fracs[3]) else 'Falso'
    else:
        res = 'Verdadero' if (fracs[0] / fracs[1]) == (fracs[2] / fracs[3]) else 'Falso'
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': res,
        'tipo': 'radio',
        'opciones': ['Verdadero', 'Falso'],
        'tema_id': 5
    }


def generar_pregunta_tema_6(seed, dificultad):
    """Tema 6: Operaciones con fracciones (multiplicación/división)"""
    random.seed(seed)
    operador = random.choice(['*', r'\div'])
    fracs = []
    for j in range(4):
        num = random.randint(-5, 5)
        if num == 0:
            num = 1
        fracs.append(num)
    
    if operador == '*':
        res = str(round((fracs[0] / fracs[1]) * (fracs[2] / fracs[3]), 2))
    else:
        res = str(round((fracs[0] / fracs[1]) / (fracs[2] / fracs[3]), 2))
    
    latex_str = r'\frac{' + str(fracs[0]) + '}{' + str(fracs[1]) + '}' + operador + r'\frac{' + str(fracs[2]) + '}{' + str(fracs[3]) + '}'
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': res,
        'tipo': 'texto',
        'tema_id': 6
    }


def generar_pregunta_tema_7(seed, dificultad):
    """Tema 7: Suma/resta de fracciones"""
    random.seed(seed)
    operador = random.choice(['+', '-'])
    fracs = []
    for j in range(4):
        num = random.randint(-5, 5)
        if num == 0:
            num = 1
        fracs.append(num)
    
    if operador == '+':
        res = str(round((fracs[0] / fracs[1]) + (fracs[2] / fracs[3]), 2))
    else:
        res = str(round((fracs[0] / fracs[1]) - (fracs[2] / fracs[3]), 2))
    
    latex_str = r'\frac{' + str(fracs[0]) + '}{' + str(fracs[1]) + '}' + operador + r'\frac{' + str(fracs[2]) + '}{' + str(fracs[3]) + '}'
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': res,
        'tipo': 'texto',
        'tema_id': 7
    }


def generar_pregunta_tema_9(seed, dificultad):
    """Tema 9: Conjuntos numéricos (simplificado)"""
    random.seed(seed)
    num = random.randint(1, 4)
    sig = random.choice(['sip', 'nop'])
    
    res = ['Natural', 'Entero', 'Racional', 'Real']
    
    if sig == 'sip':
        num *= -1
        res.remove('Natural')
        latex_str = str(num)
    else:
        latex_str = str(num)
    
    res.sort()
    return {
        'pregunta': latex_str,
        'respuesta_correcta': ', '.join(res),
        'tipo': 'texto',
        'tema_id': 9,
        'instruccion': 'Escribe los conjuntos separados por comas (Natural, Entero, Racional, Real)'
    }


def generar_pregunta_tema_10(seed, dificultad):
    """Tema 10: Propiedades"""
    random.seed(seed)
    prop = random.choice(['Inversa', 'Conmutativa', 'Asociativa', 'Identidad', 'Distributiva'])
    op = random.choice(['+', '*'])
    
    num_str = str(random.randint(1, 5))
    latex_str = ''
    res = prop + ' '
    if op == '+':
        res += 'Aditiva'
    else:
        res += 'Multiplicativa'
    
    if prop == 'Inversa':
        if op == '+':
            latex_str += num_str + ' + (-' + num_str + ') = 0'
        else:
            latex_str += num_str + r' * \frac{1}{' + num_str + '} = 1'
    elif prop == 'Conmutativa':
        num1_str = str(random.randint(1, 6))
        latex_str += num_str + op + num1_str + ' = ' + num1_str + op + num_str
    elif prop == 'Asociativa':
        num1_str = str(random.randint(1, 6))
        num2_str = str(random.randint(1, 7))
        latex_str += num_str + op + '(' + num1_str + op + num2_str + ') = ' + num1_str + op + '(' + num_str + op + num2_str + ')'
    elif prop == 'Identidad':
        latex_str += num_str + op
        if op == '+':
            latex_str += '0 = ' + num_str
        else:
            latex_str += '1 = ' + num_str
    else:
        res = prop
        num1_str = str(random.randint(1, 6))
        num2_str = str(random.randint(1, 7))
        latex_str = num_str + '(' + num1_str + '+' + num2_str + ') = ' + num_str + '*' + num1_str + ' + ' + num_str + '*' + num2_str
    
    opciones = ['Inversa Aditiva', 'Inversa Multiplicativa', 'Asociativa Aditiva', 'Asociativa Multiplicativa',
                'Conmutativa Aditiva', 'Conmutativa Multiplicativa', 'Identidad Aditiva', 'Identidad Multiplicativa',
                'Distributiva']
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': res,
        'tipo': 'radio',
        'opciones': opciones,
        'tema_id': 10
    }


def generar_pregunta_tema_11(seed, dificultad):
    """Tema 11: Valor absoluto"""
    random.seed(seed)
    operacion = random.choice(['/', '*', '-', '-', '-'])
    num = random.randint(-5, 4)
    
    latex_str = '|'
    res = num
    if operacion == '/':
        if num == 0:
            num += 1
        res = random.randint(-10, 10)
        latex_str += str(num * res) + r'\div'
    elif operacion == '*':
        latex_str += str(num) + '*'
        num = random.randint(-5, 5)
        res *= num
    
    latex_str += str(num) + '| = '
    
    if res < 0:
        res = res * (-1)
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': str(res),
        'tipo': 'texto',
        'tema_id': 11
    }


def generar_pregunta_tema_12(seed, dificultad):
    """Tema 12: Expresiones verbales a algebraicas"""
    random.seed(seed)
    nums = ['2', '3', '4', '5', '6', '7', '8', '9']
    multi = ['veces', 'por', 'multiplicado por']
    divi = ['entre', 'divido entre', 'partido entre']
    suma = ['aumentado en', 'más', 'sumado con']
    resta = ['sustraido en', 'menos', 'restado con']
    equis = ['lo desconocido', 'algún número', 'cualquier número']
    
    num = random.choice(nums)
    desconocido = random.choice(equis)
    op = random.choice(['+', '-', '/', '*'])
    res = op + num + 'x'
    
    if op == '+':
        elec = random.choice(suma)
    elif op == '-':
        elec = random.choice(resta)
    elif op == '*':
        elec = random.choice(multi)
        res = num + 'x'
    else:
        elec = random.choice(divi)
    
    latex_str = desconocido + ' ' + elec + ' ' + num
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': res,
        'tipo': 'texto',
        'tema_id': 12,
        'instruccion': 'Escribe la expresión algebraica (ej: 2x, x+3, x-5, x/4)'
    }


def generar_pregunta_tema_13(seed, dificultad):
    """Tema 13: Ecuaciones simples"""
    random.seed(seed)
    a = random.randint(-5, 5)
    if a == 0:
        a = 1
    b = random.randint(-10, 10)
    x_sol = random.randint(-10, 10)
    c = a * x_sol + b
    
    if a == 1:
        latex_str = 'x'
    elif a == -1:
        latex_str = '-x'
    else:
        latex_str = str(a) + 'x'
    
    if b >= 0:
        latex_str += '+' + str(b)
    else:
        latex_str += str(b)
    
    latex_str += '=' + str(c)
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': str(x_sol),
        'tipo': 'texto',
        'tema_id': 13
    }


def generar_pregunta_tema_14(seed, dificultad):
    """Tema 14: Ecuaciones con paréntesis"""
    random.seed(seed)
    a = random.randint(-5, 5)
    if a == 0:
        a = 1
    b = random.randint(-8, 8)
    c = random.randint(-6, 6)
    if c == 0:
        c = 1
    d = random.randint(-8, 8)
    
    if a - c != 0:
        x_sol = round((c * d - b) / (a - c), 2)
    else:
        a = c + 1
        x_sol = round((c * d - b) / (a - c), 2)
    
    if a == 1:
        latex_str = 'x'
    elif a == -1:
        latex_str = '-x'
    else:
        latex_str = str(a) + 'x'
    
    if b >= 0:
        latex_str += '+' + str(b)
    else:
        latex_str += str(b)
    
    latex_str += '=' + str(c) + '(x'
    if d >= 0:
        latex_str += '+' + str(d)
    else:
        latex_str += str(d)
    latex_str += ')'
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': str(x_sol),
        'tipo': 'texto',
        'tema_id': 14
    }


def generar_pregunta_tema_15(seed, dificultad):
    """Tema 15: Ecuaciones lineales complejas"""
    random.seed(seed)
    op2 = random.choice(['+', '-'])
    num = random.randint(-6, 6)
    num2 = random.randint(-8, 8)
    res = random.randint(-2, 2)
    
    if num == 0:
        num = 1
    if num2 == 0:
        num2 = 1
    if res == 0:
        res = 1
    
    latex_str = str(num) + 'x' + op2 + str(num2)
    
    return {
        'pregunta': latex_str + '(2x+1)=10',
        'respuesta_correcta': str(res),
        'tipo': 'texto',
        'tema_id': 15
    }


def generar_pregunta_tema_16(seed, dificultad):
    """Tema 16: Pendiente de una recta"""
    random.seed(seed)
    x1 = random.randint(-5, 5)
    y1 = random.randint(-5, 5)
    x2 = random.randint(-5, 5)
    while x2 == x1:
        x2 = random.randint(-5, 5)
    y2 = random.randint(-5, 5)
    
    m = round((y2 - y1) / (x2 - x1), 2)
    latex_str = f"P_1({x1},{y1}), P_2({x2},{y2})"
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': str(m),
        'tipo': 'texto',
        'tema_id': 16,
        'instruccion': 'Calcula la pendiente m = (y2-y1)/(x2-x1)'
    }


def generar_pregunta_tema_17(seed, dificultad):
    """Tema 17: Ecuación de la recta"""
    random.seed(seed)
    m = random.randint(-5, 5)
    if m == 0:
        m = 1
    b = random.randint(-8, 8)
    
    x0 = random.randint(-3, 3)
    y0 = m * x0 + b
    
    latex_str = f"m={m}, punto({x0},{y0})"
    
    respuesta = f"y={m}x"
    if b >= 0:
        respuesta += f"+{b}"
    else:
        respuesta += str(b)
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': respuesta,
        'tipo': 'texto',
        'tema_id': 17,
        'instruccion': 'Escribe la ecuación de la recta en forma y=mx+b'
    }


def generar_pregunta_tema_19(seed, dificultad):
    """Tema 19: Sistemas de ecuaciones (simplificado)"""
    random.seed(seed)
    x_sol = random.randint(-5, 5)
    y_sol = random.randint(-5, 5)
    
    a1 = random.randint(1, 5)
    b1 = random.randint(1, 5)
    c1 = a1 * x_sol + b1 * y_sol
    
    a2 = random.randint(1, 5)
    b2 = random.randint(1, 5)
    c2 = a2 * x_sol + b2 * y_sol
    
    latex_str = f"{a1}x+{b1}y={c1}, {a2}x+{b2}y={c2}"
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': f"x={x_sol},y={y_sol}",
        'tipo': 'texto',
        'tema_id': 19,
        'instruccion': 'Encuentra x e y (formato: x=a,y=b)'
    }


def generar_pregunta_tema_21(seed, dificultad):
    """Tema 21: Factorización"""
    random.seed(seed)
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    
    coef_x = a + b
    coef_const = a * b
    
    latex_str = f"x^2"
    if coef_x >= 0:
        latex_str += f"+{coef_x}x"
    else:
        latex_str += f"{coef_x}x"
    
    if coef_const >= 0:
        latex_str += f"+{coef_const}"
    else:
        latex_str += str(coef_const)
    
    respuesta = f"(x"
    if a >= 0:
        respuesta += f"+{a}"
    else:
        respuesta += str(a)
    respuesta += ")(x"
    if b >= 0:
        respuesta += f"+{b}"
    else:
        respuesta += str(b)
    respuesta += ")"
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': respuesta,
        'tipo': 'texto',
        'tema_id': 21,
        'instruccion': 'Factoriza el trinomio (ej: (x+2)(x+3))'
    }


def generar_pregunta_tema_22(seed, dificultad):
    """Tema 22: Ecuaciones cuadráticas"""
    random.seed(seed)
    x1 = random.randint(-5, 5)
    x2 = random.randint(-5, 5)
    
    b = -(x1 + x2)
    c = x1 * x2
    
    latex_str = "x^2"
    if b >= 0:
        latex_str += f"+{b}x"
    else:
        latex_str += f"{b}x"
    
    if c >= 0:
        latex_str += f"+{c}"
    else:
        latex_str += str(c)
    latex_str += "=0"
    
    sols = sorted([x1, x2])
    respuesta = f"x={sols[0]},x={sols[1]}"
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': respuesta,
        'tipo': 'texto',
        'tema_id': 22,
        'instruccion': 'Encuentra las soluciones (formato: x=a,x=b)'
    }


def generar_pregunta_generica(seed, tema_id, dificultad):
    """Generador genérico para temas no implementados específicamente"""
    random.seed(seed)
    num1 = random.randint(-20, 20)
    num2 = random.randint(-20, 20)
    operacion = random.choice(['+', '-', '*'])
    
    if operacion == '+':
        res = num1 + num2
        latex_str = f"{num1} + {num2} ="
    elif operacion == '-':
        res = num1 - num2
        latex_str = f"{num1} - {num2} ="
    else:
        res = num1 * num2
        latex_str = f"{num1} \\times {num2} ="
    
    return {
        'pregunta': latex_str,
        'respuesta_correcta': str(res),
        'tipo': 'texto',
        'tema_id': tema_id
    }


# ==================== REGISTRO DE GENERADORES ====================

GENERADORES_POR_TEMA = {
    1: generar_pregunta_tema_1,
    2: generar_pregunta_tema_2,
    3: generar_pregunta_tema_3,
    4: generar_pregunta_tema_4,
    5: generar_pregunta_tema_5,
    6: generar_pregunta_tema_6,
    7: generar_pregunta_tema_7,
    9: generar_pregunta_tema_9,
    10: generar_pregunta_tema_10,
    11: generar_pregunta_tema_11,
    12: generar_pregunta_tema_12,
    13: generar_pregunta_tema_13,
    14: generar_pregunta_tema_14,
    15: generar_pregunta_tema_15,
    16: generar_pregunta_tema_16,
    17: generar_pregunta_tema_17,
    19: generar_pregunta_tema_19,
    21: generar_pregunta_tema_21,
    22: generar_pregunta_tema_22,
}


def generar_pregunta(tema_id, seed, dificultad):
    """
    Función principal para generar una pregunta de cualquier tema.
    
    Args:
        tema_id (int): ID del tema
        seed (int): Semilla para generación aleatoria
        dificultad (int): Nivel de dificultad del tema
    
    Returns:
        dict: Diccionario con la estructura estándar de pregunta
    """
    generador = GENERADORES_POR_TEMA.get(tema_id, generar_pregunta_generica)
    if generador == generar_pregunta_generica:
        return generador(seed, tema_id, dificultad)
    return generador(seed, dificultad)


def obtener_temas_disponibles():
    """
    Retorna la lista de IDs de temas con generadores específicos.
    
    Returns:
        list: Lista de IDs de temas disponibles
    """
    return sorted(GENERADORES_POR_TEMA.keys())

