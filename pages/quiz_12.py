#Reutilizable
import streamlit as st
import random
import time 
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

if "mat" in st.session_state:
    mat = st.session_state["mat"]
else:
    st.switch_page("streamlit_app.py")

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

if total_actual >= limite:
    st.warning("⚠️ Ya alcanzaste el límite de puntos para este tema.")
    time.sleep(2)
    st.warning("⚠️ Regresa mañana.")
    time.sleep(2)
    st.switch_page("pages/inicio.py")

#st.write(st.session_state.tema)
info = session.table("primeroc.public.subjects").filter(col('id_tema')==st.session_state.tema).collect()[0]
st.title(info[1])
st.write("Dificultad:", info[2])

new_seed = random.randint(1, 10000)

random.seed(st.session_state.s_seed)

# Initialize session state variable
if 'button_disabled' not in st.session_state:
    st.session_state.button_disabled = False

# Callback function to disable the button
def disable_button():
    st.session_state.button_disabled = True

preguntas = []
respuestas = []

nums = ['2', '3', '4', '5', '6', '7', '8', '9']
multi = ['veces', 'por', 'multiplicado por']
divi = ['entre', 'divido entre', 'partido entre']
suma = ['aumentado en', 'más', 'sumado con']
resta = ['sustraido en', 'menos', 'restado con']
equis = ['lo desconocido', 'algún número', 'cualquier nÚmero']

for i in range (5):
    #Fin
    elec = random.choice(['x', 'n'])
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

    if elec == 'n':
        latex_str = num + ' ' + elec + ' ' + desconocido
    else:
        latex_str = desconocido + ' ' + elec + ' ' + num

    preguntas.append(latex_str)
    respuestas.append(res)

#Reutilizable
with st.form("my_form"):
    st.write("**Instrucciones:** Para cada expresión verbal, escribe la expresión algebraica correspondiente.")
    st.write("---")
    
    respuestas_estudiante = []
    
    for i in range(5):
        st.write(f"**Pregunta {i+1}:**")
        st.write(preguntas[i])
        res_est = st.text_input(f"{i+1}. Ingresa tu respuesta:", key=f"resp_{i}")
        if res_est:
            res_est = "".join(sorted(res_est))
        respuestas_estudiante.append(res_est)
        st.write("---")

    logrado = st.form_submit_button('Confirmar respuestas', on_click=disable_button, disabled=st.session_state.button_disabled)

#Reutilizable
if logrado:
    pts = 0
    
    for i in range(5):
        if respuestas[i] == respuestas_estudiante[i].replace(" ", ""):
            st.success(f"{i+1}. Bravooo")
            pts += 1
        else:
            mensaje_error = f"{i+1}. La respuesta era: " + str(respuestas[i])
            st.warning(mensaje_error)
        
        time.sleep(0.8)

    if pts == 5:
        st.write(f"Felicidades por contestar todo bien. Obtienes", info[2], "punto(s) adicional.")
        pts += info[2]
    
    pts = int((pts * 0.7) + (pts * 0.3 * info[2])) #1 - 6, 1 - 8, 1 - 11, 1 - 13, 2 - 16   
    std_ac = std_info[3] + pts 
    std_tot = std_info[4] + pts

    # if total_actual >= limite:
    #     st.warning("⚠️ Ya alcanzaste el límite de puntos para este tema.")
    #     sleep(1)
    #     st.switch_page("pages/inicio.py")
    
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
    
