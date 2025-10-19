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

if mat == '102626' or mat == '112233':
    st.warning("Te lo voy a permitir, pero, es lo mismo que antes...")

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
#random.seed(new_seed)

# Callback function to disable the button
def disable_button():
    st.session_state.button_disabled = True

preguntas = []
respuestas = []

st.write('Coloquen el punto donde lo pondrían en la grafica. Es lo mejor que pude hacer. Pipipi')
for i in range (5):
    #Fin
    operacion = random.choice(['/', '*'])

    res = random.randint(-5, 5 + i)
    if operacion == '/':
        num = random.randint(-5, 4 + i)
        if num == 0:
            num += 1

        latex_str = str(num * res) + '\div' + str(num)
    else:
        latex_str = str(res)

    preguntas.append(latex_str)
    respuestas.append(res)

#Reutilizable
with st.form("my_form"):
   #Pregunta 1
    st.latex(preguntas[0])
    res_est0 = st.slider("1. Ingresa tu respuesta: ", -10, 10, 0)

    #Pregunta 2
    st.latex(preguntas[1])
    res_est1 = st.slider("2. Ingresa tu respuesta:", -10, 10, 0)

    #Pregunta 3
    st.latex(preguntas[2])
    res_est2 = st.slider("3. Ingresa tu respuesta:", -10, 10, 0)
    
    #Pregunta 4
    st.latex(preguntas[3])
    res_est3 = st.slider("4. Ingresa tu respuesta:", -10, 10, 0)

    #Pregunta 5
    st.latex(preguntas[4])
    res_est4 = st.slider("5. Ingresa tu respuesta:", -10, 10, 0)

    logrado = st.form_submit_button('Confirmar respuestas', on_click=disable_button, disabled=st.session_state.button_disabled)

#Reutilizable
if logrado:
    pts = 0
    
    #Respuesta 0
    if respuestas[0] == res_est0:
        st.success("1. Bravooo")
        pts += 1
    else:
        mensaje_error = "1. La respuesta era: " + str(respuestas[0])
        st.warning(mensaje_error)
    
    time.sleep(0.8)
    #Respuesta 1
    if respuestas[1] == res_est1:
        st.success("2. Bravooo")
        pts += 1
    else:
        mensaje_error = "2. La respuesta era: " + str(respuestas[1])
        st.warning(mensaje_error)
        
    time.sleep(0.8)
    #Respuesta 2
    if respuestas[2] == res_est2:
        st.success("3. Bravooo")
        pts += 1
    else:
        mensaje_error = "3. La respuesta era: " + str(respuestas[2])
        st.warning(mensaje_error)
    
    time.sleep(0.8)
    #Respuesta 3
    if respuestas[3] == res_est3:
        st.success("4. Bravooo")
        pts += 1
    else:
        mensaje_error = "4. La respuesta era: " + str(respuestas[3])
        st.warning(mensaje_error)
    
    time.sleep(0.8)
    #Respuesta 4
    if respuestas[4] == res_est4:
        st.success("5. Bravooo")
        pts += 1
    else:
        mensaje_error = "5. La respuesta era: " + str(respuestas[4])
        st.warning(mensaje_error)

    if pts == 5:
        st.write(f"Felicidades por contestar todo bien. Obtienes", info[2], "punto(s) adicional.")
        pts += info[2]
    
    pts = int((pts * 0.7) + (pts * 0.3 * info[2]) + 0.1) #1 - 6, 1 - 8, 1 - 11, 1 - 13, 2 - 16   
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
    
