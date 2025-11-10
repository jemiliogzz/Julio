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

    res = ['Natural', 'Entero', 'Racional', 'Real']

    num = random.randint(1, 4 + i)

    sig = random.choice(['sip', 'nop'])

    if sig == 'sip':
        num  *= -1
        res.remove('Natural')
        sig = random.choice(['ent', 'rac', 'irr'])
        if sig == 'rac':
            res.remove('Entero')
            num1 = random.randint(-4, 5 + i)
            if num1 == 0:
                num1 = 1

            if num % num1 == 0:
                res.append('Entero')
                if num1 < 0:
                    res.append('Natural')
                latex_str = str(int(num / num1))
            else: 
                disp = random.choice(['\div', 'num'])
                if disp == '\div':
                    latex_str = str(num) + disp + str(num1)
                else:
                    num = num / num1
                    latex_str = str(round(num, 14))
                    if len(str(num)) > 16:
                        latex_str += '...'
        elif sig == 'irr':
            num *= -1
            res.remove('Entero')
            res.remove('Racional')
            res.append('Irracional')
            if num == 1 or num == 4 or num == 9:
                num += 1
            #\sqrt{x}
            disp = random.choice(['\sqrt', 'num'])
            if disp == '\sqrt':
                latex_str = '\sqrt{' + str(num) + '}'
            else:
                num = num ** (1/2)
                latex_str = str(round(num, 14))
                if len(str(num)) > 16:
                    latex_str += '...'
        else:
            latex_str = str(num)
    else:
        latex_str = str(num)

    preguntas.append(latex_str)
    res.sort()
    respuestas.append(res)
    
#Reutilizable
with st.form("my_form"):
    st.write("**Instrucciones:** Para cada número, selecciona TODOS los conjuntos numéricos a los que pertenece.")
    st.write("---")
    
    respuestas_estudiante = []
    
    for i in range(cantidad_preguntas):
        st.write(f"**Pregunta {i+1}:**")
        st.latex(preguntas[i])
        res_est = st.multiselect(
            f"{i+1}. Selecciona TODOS los que correspondan",
            ['Natural', 'Entero', 'Racional', 'Irracional', 'Real'],
            default=["Real"],
            key=f"resp_{i}"
        )
        res_est.sort()
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
        
        # Botón para continuar al siguiente tema
        siguiente_tema = obtener_siguiente_tema_examen()
        if siguiente_tema is not None:
            if st.button("➡️ Continuar al siguiente tema", type="primary"):
                if avanzar_siguiente_tema_examen():
                    # Obtener el tema actual desde el índice (después de avanzar)
                    idx_actual = st.session_state.exam_tema_actual_idx
                    tema_actual = st.session_state.exam_temas[idx_actual]
                    st.session_state.tema = tema_actual
                    st.session_state.s_seed = random.randint(1, 10000)
                    st.session_state.button_disabled = False
                    st.switch_page(f"pages/quiz_{tema_actual}.py")
        else:
            # Terminó el examen, mostrar resumen
            st.success("✅ Has completado todos los temas del examen!")
            if st.button("📊 Ver Resumen del Examen", type="primary"):
                st.switch_page("pages/simulacion_examen.py")
    else:
        # Modo práctica normal: guardar puntos en BD
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
    
