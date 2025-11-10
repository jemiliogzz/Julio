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

    res_pos = random.randint(2, 4 + i)
    mul = random.randint(3, 4 + i)
    sum = random.randint(-2, 2)
    if sum == 0:
      sum = 1
    sum = sum * mul
    fin = res_pos * mul + sum
    latex_str = '|' + str(mul) + 'x'
    if sum > 0:
      latex_str += '+'

    latex_str += str(sum) + '|=' + str(fin)
    
    res_neg = int(((fin * -1) - sum) / mul)

    preguntas.append(latex_str)
    respuestas.append((str(res_pos), str(res_neg)))

#Reutilizable
with st.form("my_form"):
    st.write("**Instrucciones:** Para cada ecuación con valor absoluto, encuentra las dos soluciones posibles.")
    st.write("---")
    
    respuestas_estudiante = []
    
    for i in range(cantidad_preguntas):
        st.write(f"**Pregunta {i+1}:**")
        st.latex(preguntas[i])
        res_est0 = st.text_input(f"{i+1}. Ingresa la solución #1:", key=f"sol1_{i}")
        res_est1 = st.text_input(f"{i+1}. Ingresa la solución #2:", key=f"sol2_{i}")
        respuestas_estudiante.append((res_est0, res_est1))
        st.write("---")

    logrado = st.form_submit_button('Confirmar respuestas', on_click=disable_button, disabled=st.session_state.button_disabled)

#Reutilizable
if logrado:
    pts = 0
    
    for i in range(cantidad_preguntas):
        res_est0 = respuestas_estudiante[i][0].replace(" ", "")
        res_est1 = respuestas_estudiante[i][1].replace(" ", "")
        
        # Verificar si las dos soluciones son correctas (en cualquier orden)
        if (respuestas[i][0] == res_est0 and respuestas[i][1] == res_est1) or \
           (respuestas[i][1] == res_est0 and respuestas[i][0] == res_est1):
            st.success(f"{i+1}. Bravooo")
            pts += 1
        else:
            mensaje_error = f"{i+1}. La respuesta era: {respuestas[i][0]} y {respuestas[i][1]}"
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
        
        # Botón para continuar al siguiente tema
        siguiente_tema = obtener_siguiente_tema_examen()
        if siguiente_tema is not None:
            if st.button("➡️ Continuar al siguiente tema", type="primary"):
                if avanzar_siguiente_tema_examen():
                    st.session_state.tema = siguiente_tema
                    st.session_state.s_seed = random.randint(1, 10000)
                    st.session_state.button_disabled = False
                    st.rerun()
        else:
            # Terminó el examen, mostrar resumen
            st.success("✅ Has completado todos los temas del examen!")
            if st.button("📊 Ver Resumen del Examen", type="primary"):
                st.switch_page("pages/simulacion_examen.py")
    else:
        # Modo práctica normal: guardar puntos en BD
        pts = int((pts * 0.7) + (pts * 0.3 * info[2]) + 0.1) + pts_extra #1 - 6, 1 - 8, 1 - 11, 1 - 13, 2 - 16   
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
    
