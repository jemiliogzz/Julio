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
    Obtiene el siguiente tema del examen (primer elemento del arreglo).
    
    Returns:
        int or None: ID del siguiente tema, o None si no hay más temas
    """
    if not esta_en_modo_examen():
        return None
    
    if 'exam_temas' not in st.session_state:
        return None
    
    temas = st.session_state.exam_temas
    
    if len(temas) > 0:
        return temas[0]  # Retornar el primer tema del arreglo
    
    return None


def avanzar_siguiente_tema_examen():
    """
    Hace pop del primer tema del arreglo y retorna el siguiente tema.
    
    Returns:
        int or None: ID del siguiente tema después de hacer pop, o None si no hay más temas
    """
    if not esta_en_modo_examen():
        return None
    
    if 'exam_temas' not in st.session_state:
        return None
    
    temas = st.session_state.exam_temas
    
    # Hacer pop del primer elemento
    if len(temas) > 0:
        temas.pop(0)  # Eliminar el primer tema del arreglo
        st.session_state.exam_temas = temas  # Actualizar el arreglo
    
    # Retornar el siguiente tema (ahora el primero del arreglo)
    if len(temas) > 0:
        return temas[0]
    
    return None  # No hay más temas


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

