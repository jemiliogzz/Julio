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
letras = ['x', 'y', 'z']

for i in range (5):
    #Fin

    aux_list = []
    latex_str = ''
    x = 0
    y = 0
    z = 0
    for j in range (2):
        for k in range (3):
            num = random.randint(-3, 4 + i)
            
            if num != 0:
                if num > 0:
                    latex_str += '+' + str(num) + letras[k]
                else:
                    latex_str += str(num) + letras[k]

                if k == 0:
                    x += num
                elif k == 1:
                    y += num
                else:
                    z += num
                    
    if latex_str.find('+') == 0:
        latex_str = latex_str[1:]
        
    aux_list.append(str(x))
    aux_list.append(str(y))
    aux_list.append(str(z))

    preguntas.append(latex_str)
    respuestas.append(aux_list)
        
#Reutilizable
with st.form("my_form"):
    #Pregunta 1
    res_est0 = []
    st.latex(preguntas[0])
    res_est0x = st.text_input("1. Cantidad de 'x':")
    res_est0y = st.text_input("1. Cantidad de 'y':")
    res_est0z = st.text_input("1. Cantidad de 'z':")

    res_est0.append(res_est0x.replace(" ", ""))
    res_est0.append(res_est0y.replace(" ", ""))
    res_est0.append(res_est0z.replace(" ", ""))
    
    #Pregunta 2
    res_est1 = []
    st.latex(preguntas[1])
    res_est1x = st.text_input("2. Cantidad de 'x':")
    res_est1y = st.text_input("2. Cantidad de 'y':")
    res_est1z = st.text_input("2. Cantidad de 'z':")

    res_est1.append(res_est1x.replace(" ", ""))
    res_est1.append(res_est1y.replace(" ", ""))
    res_est1.append(res_est1z.replace(" ", ""))

    #Pregunta 3
    res_est2 = []
    st.latex(preguntas[2])
    res_est2x = st.text_input("3. Cantidad de 'x':")
    res_est2y = st.text_input("3. Cantidad de 'y':")
    res_est2z = st.text_input("3. Cantidad de 'z':")

    res_est2.append(res_est2x.replace(" ", ""))
    res_est2.append(res_est2y.replace(" ", ""))
    res_est2.append(res_est2z.replace(" ", ""))
    
    #Pregunta 4
    res_est3 = []
    st.latex(preguntas[3])
    res_est3x = st.text_input("4. Cantidad de 'x':")
    res_est3y = st.text_input("4. Cantidad de 'y':")
    res_est3z = st.text_input("4. Cantidad de 'z':")

    res_est3.append(res_est3x.replace(" ", ""))
    res_est3.append(res_est3y.replace(" ", ""))
    res_est3.append(res_est3z.replace(" ", ""))

    #Pregunta 5
    res_est4 = []
    st.latex(preguntas[4])
    res_est4x = st.text_input("5. Cantidad de 'x':")
    res_est4y = st.text_input("5. Cantidad de 'y':")
    res_est4z = st.text_input("5. Cantidad de 'z':")

    res_est4.append(res_est4x.replace(" ", ""))
    res_est4.append(res_est4y.replace(" ", ""))
    res_est4.append(res_est4z.replace(" ", ""))

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
    
