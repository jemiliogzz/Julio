import streamlit as st
import random
import time
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Importar generadores desde módulo compartido
import sys
sys.path.append('..')  # Para poder importar desde la raíz del proyecto
from quiz_generators import generar_pregunta, obtener_temas_disponibles

# Verificar autenticación
if "mat" not in st.session_state:
    st.switch_page("streamlit_app.py")

mat = st.session_state["mat"]

# Conexión a Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Obtener información del estudiante
std_info = session.table("primeroc.public.students").filter(col('matricula') == mat).collect()[0]
std_id = std_info[0]

st.title("🎯 Simulación de Examen")
st.write("Selecciona los temas que deseas practicar y genera un examen personalizado.")

# Inicializar session state para el examen
if 'exam_state' not in st.session_state:
    st.session_state.exam_state = 'selection'  # Estados: selection, taking_exam, results
if 'exam_questions' not in st.session_state:
    st.session_state.exam_questions = []
if 'current_question_idx' not in st.session_state:
    st.session_state.current_question_idx = 0
if 'exam_answers' not in st.session_state:
    st.session_state.exam_answers = []
if 'exam_seed' not in st.session_state:
    st.session_state.exam_seed = random.randint(1, 10000)

# ==================== LÓGICA DE NAVEGACIÓN ====================

if st.session_state.exam_state == 'selection':
    st.subheader("Paso 1: Selección de Temas")
    
    # Obtener todos los temas excepto el 23
    temas = session.table("primeroc.public.subjects") \
        .filter(col('id_tema') != 23) \
        .select(col('id_tema'), col('nombre_tema')) \
        .collect()
    
    st.write("**Selecciona uno o más temas para tu examen:**")
    st.info("💡 Por cada tema seleccionado se generarán 3 ejercicios.")
    
    # Crear checkboxes para cada tema
    temas_seleccionados = []
    for tema in temas:
        if st.checkbox(f"Tema {tema.ID_TEMA}: {tema.NOMBRE_TEMA}", key=f"tema_{tema.ID_TEMA}"):
            temas_seleccionados.append(tema.ID_TEMA)
    
    st.write(f"**Temas seleccionados:** {len(temas_seleccionados)}")
    st.write(f"**Total de preguntas:** {len(temas_seleccionados) * 3}")
    
    if st.button("Generar Examen", type="primary", disabled=len(temas_seleccionados) == 0):
        # Generar preguntas
        preguntas = []
        base_seed = st.session_state.exam_seed
        
        for tema_id in temas_seleccionados:
            # Obtener dificultad del tema
            info_tema = session.table("primeroc.public.subjects") \
                .filter(col('id_tema') == tema_id) \
                .collect()[0]
            dificultad = info_tema.DIFICULTAD
            
            # Generar 3 preguntas por tema usando el módulo compartido
            for i in range(3):
                seed = base_seed + tema_id * 1000 + i
                pregunta = generar_pregunta(tema_id, seed, dificultad)
                pregunta['tema_nombre'] = info_tema.NOMBRE_TEMA
                preguntas.append(pregunta)
        
        # Mezclar preguntas
        random.shuffle(preguntas)
        
        # Guardar en session state
        st.session_state.exam_questions = preguntas
        st.session_state.exam_answers = [None] * len(preguntas)
        st.session_state.current_question_idx = 0
        st.session_state.exam_state = 'taking_exam'
        st.rerun()

elif st.session_state.exam_state == 'taking_exam':
    total_preguntas = len(st.session_state.exam_questions)
    idx = st.session_state.current_question_idx
    
    # Barra de progreso
    progress = (idx) / total_preguntas
    st.progress(progress)
    st.write(f"**Pregunta {idx + 1} de {total_preguntas}**")
    
    if idx < total_preguntas:
        pregunta_actual = st.session_state.exam_questions[idx]
        
        st.write(f"**Tema:** {pregunta_actual['tema_nombre']}")
        st.write("---")
        
        # Mostrar pregunta
        st.latex(pregunta_actual['pregunta'])
        
        # Mostrar instrucciones adicionales si existen
        if 'instruccion' in pregunta_actual:
            st.info(pregunta_actual['instruccion'])
        
        # Campo de respuesta según el tipo
        respuesta_usuario = None
        
        if pregunta_actual['tipo'] == 'texto':
            respuesta_usuario = st.text_input(
                "Tu respuesta:",
                key=f"respuesta_{idx}",
                value=st.session_state.exam_answers[idx] if st.session_state.exam_answers[idx] else ""
            )
        elif pregunta_actual['tipo'] == 'radio':
            respuesta_anterior = st.session_state.exam_answers[idx]
            index_default = None
            if respuesta_anterior and respuesta_anterior in pregunta_actual['opciones']:
                index_default = pregunta_actual['opciones'].index(respuesta_anterior)
            
            respuesta_usuario = st.radio(
                "Selecciona tu respuesta:",
                pregunta_actual['opciones'],
                index=index_default,
                key=f"radio_{idx}"
            )
        elif pregunta_actual['tipo'] == 'slider':
            rango = pregunta_actual.get('rango', (-10, 10))
            valor_anterior = st.session_state.exam_answers[idx]
            valor_default = int(valor_anterior) if valor_anterior and str(valor_anterior).replace('-','').isdigit() else 0
            
            respuesta_usuario = st.slider(
                "Selecciona tu respuesta en la recta numérica:",
                min_value=rango[0],
                max_value=rango[1],
                value=valor_default,
                key=f"slider_{idx}"
            )
        
        # Botones de navegación
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if idx > 0:
                if st.button("⬅️ Anterior"):
                    st.session_state.exam_answers[idx] = respuesta_usuario
                    st.session_state.current_question_idx -= 1
                    st.rerun()
        
        with col2:
            if st.button("💾 Guardar"):
                st.session_state.exam_answers[idx] = respuesta_usuario
                st.success("Respuesta guardada")
                time.sleep(0.5)
        
        with col3:
            if idx < total_preguntas - 1:
                if st.button("Siguiente ➡️"):
                    st.session_state.exam_answers[idx] = respuesta_usuario
                    st.session_state.current_question_idx += 1
                    st.rerun()
            else:
                if st.button("✅ Finalizar Examen", type="primary"):
                    st.session_state.exam_answers[idx] = respuesta_usuario
                    st.session_state.exam_state = 'results'
                    st.rerun()

elif st.session_state.exam_state == 'results':
    st.subheader("📊 Resultados del Examen")
    
    total_preguntas = len(st.session_state.exam_questions)
    aciertos = 0
    errores = 0
    
    # Evaluar respuestas
    resultados_detallados = []
    for i, (pregunta, respuesta_usuario) in enumerate(zip(st.session_state.exam_questions, st.session_state.exam_answers)):
        es_correcto = False
        
        if pregunta['tipo'] == 'texto':
            # Normalizar respuestas (quitar espacios)
            respuesta_normalizada = str(respuesta_usuario).replace(" ", "") if respuesta_usuario else ""
            respuesta_correcta_normalizada = str(pregunta['respuesta_correcta']).replace(" ", "")
            es_correcto = respuesta_normalizada == respuesta_correcta_normalizada
        elif pregunta['tipo'] == 'radio':
            es_correcto = respuesta_usuario == pregunta['respuesta_correcta']
        elif pregunta['tipo'] == 'slider':
            # Convertir ambos a int para comparar
            try:
                es_correcto = int(respuesta_usuario) == int(pregunta['respuesta_correcta'])
            except (ValueError, TypeError):
                es_correcto = False
        
        if es_correcto:
            aciertos += 1
        else:
            errores += 1
        
        resultados_detallados.append({
            'numero': i + 1,
            'tema': pregunta['tema_nombre'],
            'correcto': es_correcto,
            'respuesta_usuario': respuesta_usuario,
            'respuesta_correcta': pregunta['respuesta_correcta']
        })
    
    porcentaje = (aciertos / total_preguntas * 100) if total_preguntas > 0 else 0
    
    # Mostrar resumen
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Preguntas", total_preguntas)
    with col2:
        st.metric("Aciertos", aciertos, delta=f"{porcentaje:.1f}%")
    with col3:
        st.metric("Errores", errores)
    with col4:
        st.metric("Calificación", f"{porcentaje:.1f}%")
    
    # Barra de progreso visual
    st.progress(aciertos / total_preguntas if total_preguntas > 0 else 0)
    
    # Mensaje de retroalimentación
    if porcentaje >= 90:
        st.success("🎉 ¡Excelente trabajo! Dominas estos temas.")
    elif porcentaje >= 70:
        st.info("👍 ¡Buen trabajo! Sigue practicando para mejorar.")
    elif porcentaje >= 50:
        st.warning("⚠️ Puedes mejorar. Revisa los temas con más cuidado.")
    else:
        st.error("📚 Necesitas repasar estos temas. ¡No te rindas!")
    
    # Mostrar detalles
    with st.expander("📋 Ver detalles de cada pregunta"):
        for resultado in resultados_detallados:
            if resultado['correcto']:
                st.success(f"✅ Pregunta {resultado['numero']} ({resultado['tema']}): Correcta")
            else:
                st.error(f"❌ Pregunta {resultado['numero']} ({resultado['tema']}): Incorrecta")
                st.write(f"   Tu respuesta: {resultado['respuesta_usuario']}")
                st.write(f"   Respuesta correcta: {resultado['respuesta_correcta']}")
    
    # Botones de acción
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Nuevo Examen"):
            # Resetear estado
            st.session_state.exam_state = 'selection'
            st.session_state.exam_questions = []
            st.session_state.current_question_idx = 0
            st.session_state.exam_answers = []
            st.session_state.exam_seed = random.randint(1, 10000)
            st.rerun()
    
    with col2:
        if st.button("🏠 Volver a Inicio"):
            # Resetear estado
            st.session_state.exam_state = 'selection'
            st.session_state.exam_questions = []
            st.session_state.current_question_idx = 0
            st.session_state.exam_answers = []
            st.session_state.exam_seed = random.randint(1, 10000)
            st.switch_page("pages/inicio.py")
