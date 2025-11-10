"""
Utilidades compartidas para los quizzes
========================================

Funciones comunes que pueden ser usadas por todos los archivos quiz_##.py
"""

import streamlit as st


def obtener_cantidad_preguntas():
    """
    Determina la cantidad de preguntas a generar.
    
    - Si viene del modo examen: 3 preguntas
    - Si es práctica normal: 5 preguntas (default)
    
    Returns:
        int: Cantidad de preguntas (3 o 5)
    """
    # Verificar si está en modo examen
    if 'exam_mode' in st.session_state and st.session_state.exam_mode:
        return 3
    return 5


def esta_en_modo_examen():
    """
    Verifica si el estudiante está en modo examen.
    
    Returns:
        bool: True si está en modo examen, False si es práctica normal
    """
    return 'exam_mode' in st.session_state and st.session_state.exam_mode


def obtener_siguiente_tema_examen():
    """
    Obtiene el siguiente tema del examen si está en modo examen.
    Retorna el tema en el índice actual + 1 (el siguiente después del actual).
    
    Returns:
        int or None: ID del siguiente tema, o None si no hay más temas
    """
    if not esta_en_modo_examen():
        return None
    
    if 'exam_temas' not in st.session_state:
        return None
    
    if 'exam_tema_actual_idx' not in st.session_state:
        st.session_state.exam_tema_actual_idx = 0
    
    idx = st.session_state.exam_tema_actual_idx + 1  # Siguiente tema
    temas = st.session_state.exam_temas
    
    if idx < len(temas):
        return temas[idx]
    
    return None


def obtener_tema_actual_examen():
    """
    Obtiene el tema actual del examen basado en el índice.
    
    Returns:
        int or None: ID del tema actual, o None si no está en modo examen
    """
    if not esta_en_modo_examen():
        return None
    
    if 'exam_temas' not in st.session_state:
        return None
    
    if 'exam_tema_actual_idx' not in st.session_state:
        st.session_state.exam_tema_actual_idx = 0
    
    idx = st.session_state.exam_tema_actual_idx
    temas = st.session_state.exam_temas
    
    if 0 <= idx < len(temas):
        return temas[idx]
    
    return None


def avanzar_siguiente_tema_examen():
    """
    Avanza al siguiente tema del examen incrementando el índice.
    
    Returns:
        bool: True si hay más temas después de avanzar, False si terminó el examen
    """
    if not esta_en_modo_examen():
        return False
    
    if 'exam_temas' not in st.session_state:
        return False
    
    if 'exam_tema_actual_idx' not in st.session_state:
        st.session_state.exam_tema_actual_idx = 0
    
    # Avanzar al siguiente tema
    st.session_state.exam_tema_actual_idx += 1
    
    # Verificar si hay más temas
    if st.session_state.exam_tema_actual_idx >= len(st.session_state.exam_temas):
        return False  # Terminó el examen
    
    return True  # Hay más temas


def registrar_resultado_examen(tema_id, aciertos, total_preguntas):
    """
    Registra el resultado de un tema en el examen.
    
    Args:
        tema_id (int): ID del tema
        aciertos (int): Número de aciertos
        total_preguntas (int): Total de preguntas
    """
    if not esta_en_modo_examen():
        return
    
    if 'exam_resultados' not in st.session_state:
        st.session_state.exam_resultados = []
    
    st.session_state.exam_resultados.append({
        'tema_id': tema_id,
        'aciertos': aciertos,
        'total': total_preguntas,
        'errores': total_preguntas - aciertos
    })

