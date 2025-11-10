#Reutilizable
import streamlit as st
import random
import time 
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import sys
sys.path.append('..')
from quiz_utils import obtener_cantidad_preguntas, esta_en_modo_examen, obtener_siguiente_tema_examen, avanzar_siguiente_tema_examen, registrar_resultado_examen

if "mat" in st.session_state:
    mat = st.session_state["mat"]
else:
    st.switch_page("streamlit_app.py")

# ========== LOGS DE INICIO (solo en modo examen) ==========
if esta_en_modo_examen():
    with st.expander("🔍 Logs de Inicio (Modo Examen)", expanded=False):
        st.write("**Estado al cargar la página:**")
        st.write(f"- Tema actual: {st.session_state.tema}")
        st.write(f"- exam_mode: {st.session_state.get('exam_mode', 'NO EXISTE')}")
        st.write(f"- exam_temas existe: {'exam_temas' in st.session_state}")
        if 'exam_temas' in st.session_state:
            st.write(f"- exam_temas: {st.session_state.exam_temas}")
            st.write(f"- exam_temas tipo: {type(st.session_state.exam_temas)}")
            st.write(f"- exam_temas longitud: {len(st.session_state.exam_temas)}")
        else:
            st.write("- exam_temas: NO EXISTE")
        st.write(f"- exam_state: {st.session_state.get('exam_state', 'NO EXISTE')}")
# ===========================================================

#st.write(st.session_state.tema)
new_seed = random.randint(1, 10000)

cnx = st.connection("snowflake")
session = cnx.session()

std_info = session.table("primeroc.public.students").filter(col('matricula')==st.session_state.mat).collect()[0]
std_id = std_info[0]

# Consultar puntos acumulados en ese tema
query_total = f"""
    SELECT COALESCE(SUM(PTS),0) AS TOTAL
    FROM PRIMEROC.PUBLIC.DONE_DONE_DONE
    WHERE ID_EST = {std_id} AND ID_TEMA = {st.session_state.tema}
"""
total_actual = session.sql(query_total).collect()[0]["TOTAL"]

# Consultar límite del tema
query_limite = f"""
    SELECT LIMITE FROM PRIMEROC.PUBLIC.SUBJECTS
    WHERE ID_TEMA = {st.session_state.tema}
"""
limite = session.sql(query_limite).collect()[0]["LIMITE"]

# Mostrar info al alumno
st.write(f"Has acumulado {total_actual} puntos en este tema (límite {limite}).")

if total_actual > limite:
    total_actual = limite
st.progress(total_actual / limite)

# Initialize session state variable
if 'button_disabled' not in st.session_state:
    st.session_state.button_disabled = False

if total_actual >= limite:
    st.warning("⚠️ Ya alcanzaste el límite de puntos para este tema.")
    time.sleep(2)
    st.warning("⚠️ Regresa mañana.")
    time.sleep(1)
    st.session_state.s_seed = new_seed
    st.session_state.button_disabled = False
    st.switch_page("pages/inicio.py")
#Fin

info = session.table("primeroc.public.subjects").filter(col('id_tema')==st.session_state.tema).collect()[0]
st.title(info[1])
st.write("Dificultad:", info[2])

random.seed(st.session_state.s_seed)

# Callback function to disable the button
def disable_button():
    st.session_state.button_disabled = True

preguntas = []
respuestas = []

# Obtener cantidad de preguntas (5 por defecto, 3 si es examen)
cantidad_preguntas = obtener_cantidad_preguntas()

for i in range(cantidad_preguntas):
    #Fin
    desigualdad = random.choice(['>', '<', "="])
    operacion = random.choice(['/', '*', '-', '-', '-'])
    num = random.randint(-5, 4 + i)
    
    latex_str = ''
    res_temp = num
    if operacion == '/':
        if num == 0:
            num += 1
            
        res_temp = random.randint(-10, 10 + i)
        latex_str = str(num * res_temp) + '\div'
    elif operacion == '*':
        latex_str = str(num) + '*'
        
        num = random.randint(-5, 5 + i) 
        res_temp *= num
    
    latex_str += str(num) + desigualdad

    num = random.randint(-15, 15 + i)
    latex_str += str(num)
    
    if desigualdad == '>':
        if res_temp > num:
            res = 'Verdadero'
        else:
            res = 'Falso'
    elif desigualdad == '<':
        if res_temp < num:
            res = 'Verdadero'
        else:
            res = 'Falso'
    else:
        if res_temp == num:
            res = 'Verdadero'
        else:
            res = 'Falso'
            
        
    preguntas.append(latex_str)
    respuestas.append(res)

#Reutilizable
with st.form("my_form"):
    st.write("**Instrucciones:** Para cada desigualdad, indica si es Verdadero o Falso.")
    st.write("---")
    
    respuestas_estudiante = []
    
    for i in range(cantidad_preguntas):
        st.write(f"**Pregunta {i+1}:**")
        st.latex(preguntas[i])
        res_est = st.radio(
            f"{i+1}. Ingresa tu respuesta:",
            ["Verdadero", "Falso"],
            index=None,
            key=f"resp_{i}"
        )
        respuestas_estudiante.append(res_est)
        st.write("---")

    logrado = st.form_submit_button('Confirmar respuestas', on_click=disable_button, disabled=st.session_state.button_disabled)

#Reutilizable
if logrado:
    pts = 0
    
    for i in range(cantidad_preguntas):
        if respuestas[i] == respuestas_estudiante[i]:
            st.success(f"{i+1}. Bravooo")
            pts += 1
        else:
            mensaje_error = f"{i+1}. La respuesta era: " + str(respuestas[i])
            st.warning(mensaje_error)
        
        time.sleep(0.8)

    pts_extra = 0
    if pts == cantidad_preguntas:
        st.write(f"Felicidades por contestar todo bien. Obtienes", info[2], "punto(s) adicional.")
        pts_extra += info[2]
    
    # Si está en modo examen, registrar resultado pero NO guardar puntos en BD
    if esta_en_modo_examen():
        registrar_resultado_examen(st.session_state.tema, pts, cantidad_preguntas)
        st.write(f"**Aciertos en este tema: {pts}/{cantidad_preguntas}**")
        
        # ========== LOGS DE DEPURACIÓN ==========
        st.divider()
        st.subheader("🔍 Logs de Depuración")
        
        # Log 1: Estado inicial
        st.write("**1. Estado inicial:**")
        st.write(f"- Tema actual: {st.session_state.tema}")
        st.write(f"- exam_temas existe: {'exam_temas' in st.session_state}")
        if 'exam_temas' in st.session_state:
            st.write(f"- exam_temas contenido: {st.session_state.exam_temas}")
            st.write(f"- exam_temas longitud: {len(st.session_state.exam_temas)}")
        else:
            st.write("- exam_temas: NO EXISTE")
        
        # Log 2: Verificación de condición
        st.write("**2. Verificación de condición:**")
        tiene_exam_temas = 'exam_temas' in st.session_state
        longitud_exam_temas = len(st.session_state.exam_temas) if tiene_exam_temas else 0
        condicion = tiene_exam_temas and longitud_exam_temas > 1
        st.write(f"- Tiene exam_temas: {tiene_exam_temas}")
        st.write(f"- Longitud exam_temas: {longitud_exam_temas}")
        st.write(f"- Condición (len > 1): {condicion}")
        st.divider()
        # ==========================================
        
        # Verificar si hay más temas (más de 1 elemento en el arreglo significa que hay un siguiente tema)
        if 'exam_temas' in st.session_state and len(st.session_state.exam_temas) > 1:
            # Hay más temas después del actual
            if st.button("➡️ Continuar al siguiente tema", type="primary", key="continuar_tema"):
                # ========== LOGS ANTES DE HACER POP ==========
                st.write("**3. ANTES de avanzar_siguiente_tema_examen():**")
                st.write(f"- exam_temas ANTES: {st.session_state.exam_temas}")
                st.write(f"- Tema actual ANTES: {st.session_state.tema}")
                # =============================================
                
                # Hacer pop del primer tema (tema actual) y obtener el siguiente
                siguiente_tema = avanzar_siguiente_tema_examen()
                
                # ========== LOGS DESPUÉS DE HACER POP ==========
                st.write("**4. DESPUÉS de avanzar_siguiente_tema_examen():**")
                st.write(f"- exam_temas DESPUÉS: {st.session_state.exam_temas}")
                st.write(f"- siguiente_tema retornado: {siguiente_tema}")
                st.write(f"- Tipo de siguiente_tema: {type(siguiente_tema)}")
                # ===============================================
                
                if siguiente_tema is not None:
                    # ========== LOGS ANTES DE REDIRIGIR ==========
                    st.write("**5. ANTES de redirigir:**")
                    st.write(f"- siguiente_tema: {siguiente_tema}")
                    st.write(f"- siguiente_tema (int): {int(siguiente_tema)}")
                    st.session_state.tema = int(siguiente_tema)
                    st.write(f"- st.session_state.tema actualizado: {st.session_state.tema}")
                    st.session_state.s_seed = random.randint(1, 10000)
                    st.session_state.button_disabled = False
                    ubi_quiz = f"pages/quiz_{siguiente_tema}.py"
                    st.write(f"- ubi_quiz: {ubi_quiz}")
                    st.write(f"- exam_temas final: {st.session_state.exam_temas}")
                    st.write("**⏳ Esperando 3 segundos antes de redirigir...**")
                    # ============================================
                    
                    time.sleep(3)
                    st.write("**🚀 Redirigiendo ahora...**")
                    st.switch_page(ubi_quiz)
                else:
                    # ========== LOG CUANDO NO HAY MÁS TEMAS ==========
                    st.write("**5. No hay más temas:**")
                    st.write(f"- siguiente_tema es None")
                    st.write(f"- exam_temas final: {st.session_state.exam_temas}")
                    st.write("**⏳ Redirigiendo a resumen...**")
                    # ================================================
                    st.session_state.exam_state = 'results'
                    time.sleep(2)
                    st.switch_page("pages/simulacion_examen.py")
        else:
            # ========== LOG CUANDO ES EL ÚLTIMO TEMA ==========
            st.write("**3. Es el último tema:**")
            if 'exam_temas' in st.session_state:
                st.write(f"- exam_temas: {st.session_state.exam_temas}")
                st.write(f"- Longitud: {len(st.session_state.exam_temas)}")
            else:
                st.write("- exam_temas: NO EXISTE")
            # ==================================================
            
            # Este es el último tema, al completarlo ir al resumen
            if st.button("📊 Ver Resumen del Examen", type="primary", key="ver_resumen"):
                # ========== LOG ANTES DE LIMPIAR ==========
                st.write("**4. ANTES de limpiar arreglo:**")
                if 'exam_temas' in st.session_state:
                    st.write(f"- exam_temas ANTES: {st.session_state.exam_temas}")
                # ===========================================
                
                # Limpiar el arreglo (hacer pop del último tema)
                if 'exam_temas' in st.session_state and len(st.session_state.exam_temas) > 0:
                    st.session_state.exam_temas.pop(0)
                
                # ========== LOG DESPUÉS DE LIMPIAR ==========
                st.write("**5. DESPUÉS de limpiar arreglo:**")
                if 'exam_temas' in st.session_state:
                    st.write(f"- exam_temas DESPUÉS: {st.session_state.exam_temas}")
                st.write("**⏳ Redirigiendo a resumen...**")
                # =============================================
                
                st.session_state.exam_state = 'results'
                time.sleep(2)
                st.switch_page("pages/simulacion_examen.py")
    else:
        # Modo práctica normal: guardar puntos en BD
        st.info("Obtuviste: " + str(pts) + " puntos extra por esta práctica!")
        
        pts = int((pts * 0.7) + (pts * 0.3 * info[2])) + pts_extra #1 - 6, 1 - 8, 1 - 11, 1 - 13, 2 - 16   
        std_ac = std_info[3] + pts 
        std_tot = std_info[4] + pts
        std_id = std_info[0]
        
        st.write("En esta práctica, obtuviste: **" + str(pts) + "pts.**")
        st.write("Puntos Actuales: " + str(std_ac) + "pts.")
        st.write("Puntos Totales: " + str(std_tot) + "pts.")
        
        my_insert_stmt = """update students
        set puntos_act = """ + str(std_ac) + """, puntos_tot = """ + str(std_tot) + """
        WHERE matricula = """ + mat
        session.sql(my_insert_stmt).collect()

        my_insert_stmt = insert_stmt = f"""
        INSERT INTO PRIMEROC.PUBLIC.DONE_DONE_DONE VALUES
        ({std_id}, '{st.session_state.tema}', {pts}, CURRENT_TIMESTAMP)
        """
        session.sql(my_insert_stmt).collect()
        
        regresar = st.button("Volver a inicio")
        if regresar:
            st.session_state.s_seed = new_seed
            st.session_state.button_disabled = False
            st.switch_page("pages/inicio.py")
#Fin
    
