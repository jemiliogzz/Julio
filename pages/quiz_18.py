import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

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
ecs = []

# Obtener cantidad de preguntas (5 por defecto, 3 si es examen)
cantidad_preguntas = obtener_cantidad_preguntas()

for i in range(cantidad_preguntas):
    #Fin
    res_aux = []
    num = random.randint(-2 - i, 2 + i)
    num2 = random.randint(-4 - i, 4 + i)

    if num == 0:
        num = 1
    if num2 == 0:
        num2 = 1

    latex_str = 'y = ' + str(num) + 'x'

    op = random.choice(['+', '-'])

    latex_str += op + str(num2)

    if op == '-':
        num2 = num2 * -1

    for j in range (3):
        ans = num * (0 + 2 * j) + num2
        res_aux.append(str(ans))
        
    ecs.append((num, num2))
    preguntas.append(latex_str)
    respuestas.append(res_aux)

#Reutilizable
with st.form("my_form"):
    st.write("**Instrucciones:** Para cada ecuación lineal, completa los valores de 'y' y verifica si la gráfica es correcta.")
    st.write("---")
    
    #Pregunta 1
    st.latex(preguntas[0])
    
    # Crear datos
    x = np.linspace(0, 5, 10)

    real0 = random.choice(['Verdadero', 'Falso'])

    m = ecs[0][0]
    
    if real0 == 'Falso':
        aux = random.randint(-3, 3)
        if aux == 0:
            aux = 1
        m += aux
        
    y =  m * x + ecs[0][1]
    
    # Crear figura
    fig, ax = plt.subplots()
    ax.axhline(0, color='black', linewidth=1)  # Eje X
    ax.axvline(0, color='black', linewidth=1)  # Eje Y
    ax.plot(x, y, 'r')
    
    # Configurar ticks solo en números enteros
    ax.xaxis.set_major_locator(MultipleLocator(1))  # Paso de 1 en X
    ax.yaxis.set_major_locator(MultipleLocator(1))  # Paso de 1 en Y
    
    # Ajustes de estilo
    ax.set_title("Plano cartesiano")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()
    
    # Mostrar en Streamlit
    st.pyplot(fig)

    row1 = st.columns(2, gap = None)
    row2 = st.columns(2, gap = None)
    row3 = st.columns(2, gap = None)

    res_est00 = []
    a = 0
    for colu in row1 + row2 + row3:
        tile = colu.container(height=100, width = 150, gap = None, vertical_alignment= 'center')
        if a % 2 == 0:
            msg = 'x = ' + str(a)
            tile.write(msg)
        else:
            msg = str(a) + '. y = '
            ans = tile.text_input(msg)
            res_est00.append(ans)
        a += 1
    
    res_est0 = st.radio(
        "1. ¿La gráfica corresponde a tu ecuación?",
        ["Verdadero", "Falso"],
        index=None,
    )

    #Pregunta 2
    st.latex(preguntas[1])

    real1 = random.choice(['Verdadero', 'Falso'])

    m = ecs[1][0]
    
    if real1 == 'Falso':
        aux = random.randint(-3, 3)
        if aux == 0:
            aux = 1
        m += aux
        
    y =  m * x + ecs[1][1]
    
    # Crear figura
    fig, ax = plt.subplots()
    ax.axhline(0, color='black', linewidth=1)  # Eje X
    ax.axvline(0, color='black', linewidth=1)  # Eje Y
    ax.plot(x, y, 'r')
    
    # Configurar ticks solo en números enteros
    ax.xaxis.set_major_locator(MultipleLocator(1))  # Paso de 1 en X
    ax.yaxis.set_major_locator(MultipleLocator(1))  # Paso de 1 en Y
    
    # Ajustes de estilo
    ax.set_title("Plano cartesiano")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()
    
    # Mostrar en Streamlit
    st.pyplot(fig)

    row4 = st.columns(2, gap = None)
    row5 = st.columns(2, gap = None)
    row6 = st.columns(2, gap = None)

    res_est10 = []
    a = 0
    for colu in row4 + row5 + row6:
        tile = colu.container(height=100, width = 150, gap = None, vertical_alignment= 'center')
        if a % 2 == 0:
            msg = 'x = ' + str(a)
            tile.write(msg)
        else:
            msg = str(a + 3) + '. y = '
            ans = tile.text_input(msg)
            res_est10.append(ans)
        a += 1
    
    res_est1 = st.radio("2. ¿La gráfica corresponde a tu ecuación?:",
        ["Verdadero", "Falso"],
        index=None,)

    #Pregunta 3
    st.latex(preguntas[2])

    real2 = random.choice(['Verdadero', 'Falso'])

    m = ecs[2][0]
    
    if real2 == 'Falso':
        aux = random.randint(-3, 3)
        if aux == 0:
            aux = 1
        m += aux
        
    y =  m * x + ecs[2][1]
    
    # Crear figura
    fig, ax = plt.subplots()
    ax.axhline(0, color='black', linewidth=1)  # Eje X
    ax.axvline(0, color='black', linewidth=1)  # Eje Y
    ax.plot(x, y, 'r')
    
    # Configurar ticks solo en números enteros
    ax.xaxis.set_major_locator(MultipleLocator(1))  # Paso de 1 en X
    ax.yaxis.set_major_locator(MultipleLocator(1))  # Paso de 1 en Y
    
    # Ajustes de estilo
    ax.set_title("Plano cartesiano")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()
    
    # Mostrar en Streamlit
    st.pyplot(fig)

    row7 = st.columns(2, gap = None)
    row8 = st.columns(2, gap = None)
    row9 = st.columns(2, gap = None)

    res_est20 = []
    a = 0
    for colu in row7 + row8 + row9:
        tile = colu.container(height=100, width = 150, gap = None, vertical_alignment= 'center')
        if a % 2 == 0:
            msg = 'x = ' + str(a)
            tile.write(msg)
        else:
            msg = str(a + 6) + '. y = '
            ans = tile.text_input(msg)
            res_est20.append(ans)
        a += 1

    res_est2 = st.radio("3. ¿La gráfica corresponde a tu ecuación?:",
        ["Verdadero", "Falso"],
        index=None,)
    
    #Pregunta 4
    st.latex(preguntas[3])

    real3 = random.choice(['Verdadero', 'Falso'])

    m = ecs[3][0]
    
    if real3 == 'Falso':
        aux = random.randint(-3, 3)
        if aux == 0:
            aux = 1
        m += aux
        
    y =  m * x + ecs[3][1]
    
    # Crear figura
    fig, ax = plt.subplots()
    ax.axhline(0, color='black', linewidth=1)  # Eje X
    ax.axvline(0, color='black', linewidth=1)  # Eje Y
    ax.plot(x, y, 'r')
    
    # Configurar ticks solo en números enteros
    ax.xaxis.set_major_locator(MultipleLocator(1))  # Paso de 1 en X
    ax.yaxis.set_major_locator(MultipleLocator(1))  # Paso de 1 en Y
    
    # Ajustes de estilo
    ax.set_title("Plano cartesiano")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()
    
    # Mostrar en Streamlit
    st.pyplot(fig)

    row10 = st.columns(2, gap = None)
    row11 = st.columns(2, gap = None)
    row12 = st.columns(2, gap = None)

    res_est30 = []
    a = 0
    for colu in row10 + row11 + row12:
        tile = colu.container(height=100, width = 150, gap = None, vertical_alignment= 'center')
        if a % 2 == 0:
            msg = 'x = ' + str(a)
            tile.write(msg)
        else:
            msg = str(a + 9) + '. y = '
            ans = tile.text_input(msg)
            res_est30.append(ans)
        a += 1
    
    res_est3 = st.radio("4. ¿La gráfica corresponde a tu ecuación?:",
        ["Verdadero", "Falso"],
        index=None,)

    #Pregunta 5
    st.latex(preguntas[4])

    real4 = random.choice(['Verdadero', 'Falso'])

    m = ecs[4][0]
    
    if real4 == 'Falso':
        aux = random.randint(-3, 3)
        if aux == 0:
            aux = 1
        m += aux
        
    y =  m * x + ecs[4][1]
    
    # Crear figura
    fig, ax = plt.subplots()
    ax.axhline(0, color='black', linewidth=1)  # Eje X
    ax.axvline(0, color='black', linewidth=1)  # Eje Y
    ax.plot(x, y, 'r')
    
    # Configurar ticks solo en números enteros
    ax.xaxis.set_major_locator(MultipleLocator(1))  # Paso de 1 en X
    ax.yaxis.set_major_locator(MultipleLocator(1))  # Paso de 1 en Y
    
    # Ajustes de estilo
    ax.set_title("Plano cartesiano")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()
    
    # Mostrar en Streamlit
    st.pyplot(fig)

    row13 = st.columns(2, gap = None)
    row14 = st.columns(2, gap = None)
    row15 = st.columns(2, gap = None)

    res_est40 = []
    a = 0
    for colu in row13 + row14 + row15:
        tile = colu.container(height=100, width = 150, gap = None, vertical_alignment= 'center')
        if a % 2 == 0:
            msg = 'x = ' + str(a)
            tile.write(msg)
        else:
            msg = str(a + 12) + '. y = '
            ans = tile.text_input(msg)
            res_est40.append(ans)
        a += 1
    
    res_est4 = st.radio("5. ¿La gráfica corresponde a tu ecuación?:",
        ["Verdadero", "Falso"],
        index=None,)

    logrado = st.form_submit_button('Confirmar respuestas', on_click=disable_button, disabled=st.session_state.button_disabled)

#Reutilizable
if logrado:
    pts = 0
    
    #Respuesta 0
    if respuestas[0] == res_est00:
        st.success("1. Valores de 'y' correctos!")
        if real0 == res_est0:
            st.success('1. Bravooo')
            pts += 1
        else:
            mensaje_error = "1. La respuesta era: " + str(real0)
            st.warning(mensaje_error)
    else:
        mensaje_error = "1. La respuesta era: " + str(respuestas[0])
        st.warning(mensaje_error)
    
    time.sleep(0.8)
    #Respuesta 1
    if respuestas[1] == res_est10:
        st.success("2. Valores de 'y' correctos!")
        if real1 == res_est1:
            st.success("2. Bravooo")
            pts += 1
        else:
            mensaje_error = "2. La respuesta era: " + str(real1)
            st.warning(mensaje_error)
    else:
        mensaje_error = "2. La respuesta era: " + str(respuestas[1])
        st.warning(mensaje_error)
        
    time.sleep(0.8)
    #Respuesta 2
    if respuestas[2] == res_est20:
        st.success("3. Valores de 'y' correctos!")
        if real2 == res_est2:
            st.success("3. Bravooo")
            pts += 1
        else:
            mensaje_error = "3. La respuesta era: " + str(real2)
            st.warning(mensaje_error)
    else:
        mensaje_error = "3. La respuesta era: " + str(respuestas[2])
        st.warning(mensaje_error)
    
    time.sleep(0.8)
    #Respuesta 3
    if respuestas[3] == res_est30:
        if real3 == res_est3:
            st.success("4. Bravooo")
            pts += 1
        else:
            mensaje_error = "4. La respuesta era: " + str(real3)
            st.warning(mensaje_error)
    else:
        mensaje_error = "4. La respuesta era: " + str(respuestas[3])
        st.warning(mensaje_error)
    
    time.sleep(0.8)
    #Respuesta 4
    if respuestas[4] == res_est40:
        if real4 == res_est4:
            st.success("5. Bravooo")
            pts += 1
        else:
            mensaje_error = "5. La respuesta era: " + str(real4)
            st.warning(mensaje_error)
    else:
        mensaje_error = "5. La respuesta era: " + str(respuestas[4])
        st.warning(mensaje_error)

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
    
