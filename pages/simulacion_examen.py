import streamlit as st
import random
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import sys
sys.path.append('..')
from quiz_utils import esta_en_modo_examen

# Verificar autenticación
if "mat" not in st.session_state:
    st.switch_page("streamlit_app.py")

mat = st.session_state["mat"]

# Restricción de acceso: Solo matrícula 112233
if mat != '112233':
    st.title("🔒 Acceso Restringido")
    st.error("⚠️ Esta funcionalidad está en fase de prueba.")
    st.info("La Simulación de Examen estará disponible próximamente para todos los estudiantes.")
    
    if st.button("🏠 Volver a Inicio"):
        st.switch_page("pages/inicio.py")
    
    st.stop()

# Conexión a Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Inicializar session state para el examen
if 'exam_state' not in st.session_state:
    st.session_state.exam_state = 'selection'  # Estados: selection, in_progress, results
if 'exam_resultados' not in st.session_state:
    st.session_state.exam_resultados = []

# ==================== LÓGICA DE NAVEGACIÓN ====================

if st.session_state.exam_state == 'selection':
    st.title("🎯 Simulación de Examen")
    st.write("Selecciona los temas que deseas practicar y genera un examen personalizado.")
    
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
        if len(temas_seleccionados) > 0:
            # Configurar modo examen
            st.session_state.exam_mode = True
            st.session_state.exam_temas = temas_seleccionados
            st.session_state.exam_tema_actual_idx = 0  # Empezar en 0 (primer tema)
            st.session_state.exam_resultados = []
            st.session_state.exam_state = 'in_progress'
            
            # Ir al primer tema
            primer_tema = temas_seleccionados[0]
            st.session_state.tema = primer_tema
            st.session_state.s_seed = random.randint(1, 10000)
            st.session_state.button_disabled = False
            
            # Navegar al primer quiz
            ubi_quiz = f"pages/quiz_{primer_tema}.py"
            st.switch_page(ubi_quiz)

elif st.session_state.exam_state == 'results':
    st.title("📊 Resultados del Examen")
    
    if not st.session_state.exam_resultados:
        st.warning("No hay resultados para mostrar.")
        if st.button("🔄 Nuevo Examen"):
            st.session_state.exam_state = 'selection'
            st.session_state.exam_mode = False
            st.rerun()
    else:
        # Calcular estadísticas totales
        total_temas = len(st.session_state.exam_resultados)
        total_preguntas = sum(r['total'] for r in st.session_state.exam_resultados)
        total_aciertos = sum(r['aciertos'] for r in st.session_state.exam_resultados)
        total_errores = sum(r['errores'] for r in st.session_state.exam_resultados)
        porcentaje = (total_aciertos / total_preguntas * 100) if total_preguntas > 0 else 0
        
        # Mostrar resumen general
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Temas", total_temas)
        with col2:
            st.metric("Total de Preguntas", total_preguntas)
        with col3:
            st.metric("Aciertos", total_aciertos, delta=f"{porcentaje:.1f}%")
        with col4:
            st.metric("Errores", total_errores)
        
        # Barra de progreso visual
        st.progress(total_aciertos / total_preguntas if total_preguntas > 0 else 0)
        
        # Mensaje de retroalimentación
        if porcentaje >= 90:
            st.success("🎉 ¡Excelente trabajo! Dominas estos temas.")
        elif porcentaje >= 70:
            st.info("👍 ¡Buen trabajo! Sigue practicando para mejorar.")
        elif porcentaje >= 50:
            st.warning("⚠️ Puedes mejorar. Revisa los temas con más cuidado.")
        else:
            st.error("📚 Necesitas repasar estos temas. ¡No te rindas!")
        
        st.divider()
        
        # Mostrar resultados por tema
        st.subheader("📋 Resultados por Tema")
        
        # Obtener nombres de temas desde BD
        temas_dict = {}
        for resultado in st.session_state.exam_resultados:
            tema_id = resultado['tema_id']
            if tema_id not in temas_dict:
                tema_info = session.table("primeroc.public.subjects") \
                    .filter(col('id_tema') == tema_id) \
                    .select(col('nombre_tema')) \
                    .collect()
                if tema_info:
                    temas_dict[tema_id] = tema_info[0].NOMBRE_TEMA
        
        # Mostrar cada tema
        temas_con_errores = []
        for resultado in st.session_state.exam_resultados:
            tema_id = resultado['tema_id']
            tema_nombre = temas_dict.get(tema_id, f"Tema {tema_id}")
            aciertos = resultado['aciertos']
            total = resultado['total']
            errores = resultado['errores']
            porcentaje_tema = (aciertos / total * 100) if total > 0 else 0
            
            # Colores según desempeño
            if porcentaje_tema == 100:
                st.success(f"✅ **{tema_nombre}**: {aciertos}/{total} ({porcentaje_tema:.0f}%)")
            elif porcentaje_tema >= 70:
                st.info(f"👍 **{tema_nombre}**: {aciertos}/{total} ({porcentaje_tema:.0f}%)")
            elif porcentaje_tema >= 50:
                st.warning(f"⚠️ **{tema_nombre}**: {aciertos}/{total} ({porcentaje_tema:.0f}%)")
            else:
                st.error(f"❌ **{tema_nombre}**: {aciertos}/{total} ({porcentaje_tema:.0f}%)")
                temas_con_errores.append(tema_nombre)
        
        # Mostrar temas con errores
        if temas_con_errores:
            st.divider()
            st.subheader("📚 Temas para Repasar")
            st.write("Los siguientes temas requieren más práctica:")
            for tema in temas_con_errores:
                st.write(f"- {tema}")
        
        # Botones de acción
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Nuevo Examen", type="primary", use_container_width=True):
                # Resetear estado
                st.session_state.exam_state = 'selection'
                st.session_state.exam_mode = False
                st.session_state.exam_resultados = []
                st.session_state.exam_temas = []
                st.session_state.exam_tema_actual_idx = -1
                st.rerun()
        
        with col2:
            if st.button("🏠 Volver a Inicio", use_container_width=True):
                # Resetear estado
                st.session_state.exam_state = 'selection'
                st.session_state.exam_mode = False
                st.session_state.exam_resultados = []
                st.session_state.exam_temas = []
                st.session_state.exam_tema_actual_idx = -1
                st.switch_page("pages/inicio.py")

else:
    # Estado in_progress - esto no debería mostrarse, pero por si acaso
    st.info("El examen está en progreso. Completa los temas para ver los resultados.")
    if st.button("🏠 Volver a Inicio"):
        st.session_state.exam_state = 'selection'
        st.session_state.exam_mode = False
        st.switch_page("pages/inicio.py")
