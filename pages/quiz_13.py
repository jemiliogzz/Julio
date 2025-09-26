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

if mat != '112233':
    st.switch_page("pages/inicio.py")

st.warning("ACTIVIDAD EN MANTENIMIENTO")
time.sleep(0.8)
st.warning("ACTIVIDAD EN MANTENIMIENTO")
time.sleep(0.8)
st.warning("ACTIVIDAD EN MANTENIMIENTO")
time.sleep(0.8)

#st.write(st.session_state.tema)
cnx = st.connection("snowflake")
session = cnx.session()
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

for i in range (5):
    #Fin

    op = random.choice(['*', '\div'])
    op2 = random.choice(['+', '-'])

    num = random.randint(-6 - i, 6 + i)
    num2 = random.randint(-8 - i, 8 + 1)
    res = random.randint(-2 - i, 2 + i)

    if num == 0:
        num = 1
    if num2 == 0:
        num2 = 1
    if res == 0:
        res = 1

    if op == '*':
        latex_str = str(num) + 'x'
        str_fin = str(num * res)
    else:
        op = random.choice(['t', 't', 'b'])

        if op == 'b':
            latex_str = r'\frac {' + str(num) + '}{x}'
            fin = num / res
            
            if op2 == '+':
                num = num + (num2 * res)
            else:
                num = num - (num2 * res)
                
            str_fin = r'\frac{' + str(num) + '}{' + str(res) + '}'
        else:
            latex_str = r'\frac{x}{' + str(num) + '}'
            fin = res / num

            if op2 == '+':
                res_aux = res + num2 * res
            else:
                res_aux = res - num2 * res
            
            str_fin = r'\frac{' + str(res_aux) + '}{' + str(num) + '}'

    st.write(str_fin)
    
    latex_str += op2 + str(num2) + '=' + str_fin

    preguntas.append(latex_str)
    respuestas.append(str(res))
    

#Reutilizable
with st.form("my_form"):
    #Pregunta 1
    st.latex(preguntas[0])
    res_est0 = st.text_input("1. Ingresa el valor de x:")

    #Pregunta 2
    st.latex(preguntas[1])
    res_est1 = st.text_input("2. Ingresa el valor de x:")

    #Pregunta 3
    st.latex(preguntas[2])
    res_est2 = st.text_input("3. Ingresa el valor de x:")
    
    #Pregunta 4
    st.latex(preguntas[3])
    res_est3 = st.text_input("4. Ingresa el valor de x:")

    #Pregunta 5
    st.latex(preguntas[4])
    res_est4 = st.text_input("5. Ingresa el valor de x:")

    logrado = st.form_submit_button('Confirmar respuestas', on_click=disable_button, disabled=st.session_state.button_disabled)

#Reutilizable
if logrado:
    pts = 0
    
    #Respuesta 0
    if respuestas[0] == res_est0.replace(" ", ""):
        st.success("1. Bravooo")
        pts += 1
    else:
        mensaje_error = "1. La respuesta era: " + str(respuestas[0])
        st.warning(mensaje_error)
    
    time.sleep(0.8)
    #Respuesta 1
    if respuestas[1] == res_est1.replace(" ", ""):
        st.success("2. Bravooo")
        pts += 1
    else:
        mensaje_error = "2. La respuesta era: " + str(respuestas[1])
        st.warning(mensaje_error)
        
    time.sleep(0.8)
    #Respuesta 2
    if respuestas[2] == res_est2.replace(" ", ""):
        st.success("3. Bravooo")
        pts += 1
    else:
        mensaje_error = "3. La respuesta era: " + str(respuestas[2])
        st.warning(mensaje_error)
    
    time.sleep(0.8)
    #Respuesta 3
    if respuestas[3] == res_est3.replace(" ", ""):
        st.success("4. Bravooo")
        pts += 1
    else:
        mensaje_error = "4. La respuesta era: " + str(respuestas[3])
        st.warning(mensaje_error)
    
    time.sleep(0.8)
    #Respuesta 4
    if respuestas[4] == res_est4.replace(" ", ""):
        st.success("5. Bravooo")
        pts += 1
    else:
        mensaje_error = "5. La respuesta era: " + str(respuestas[4])
        st.warning(mensaje_error)

    std_info = session.table("primeroc.public.students").filter(col('matricula')==st.session_state.mat).collect()[0]

    if pts == 5:
        st.write(f"Felicidades por contestar todo bien. Obtienes", info[2], "punto(s) adicional.")
        pts += info[2]
    
    pts = int((pts * 0.7) + (pts * 0.3 * info[2])) #1 - 6, 1 - 8, 1 - 11, 1 - 13, 2 - 16   
    std_ac = std_info[3] + pts 
    std_tot = std_info[4] + pts
    
    st.write("En esta práctica, obtuviste: **" + str(pts) + "pts.**")
    st.write("Puntos actuales: " + str(std_tot) + "pts.")
    
    my_insert_stmt = """update students
    set puntos_act = """ + str(std_ac) + """, puntos_tot = """ + str(std_tot) + """
    WHERE matricula = """ + mat
    session.sql(my_insert_stmt).collect()

regresar = st.button("Volver a inicio")
if regresar:
    st.session_state.s_seed = new_seed
    st.session_state.button_disabled = False
    st.switch_page("pages/inicio.py")
#Fin
    
