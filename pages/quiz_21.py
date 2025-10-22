#Reutilizable
import streamlit as st
import random
from datetime import datetime
import time 
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import matplotlib.pyplot as plt
import numpy as np
import io

if "mat" in st.session_state:
    mat = st.session_state["mat"]
else:
    st.switch_page("streamlit_app.py")

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

def generar_grafica(tipo, a, b):
    """Genera una gráfica de la desigualdad y la devuelve como imagen en bytes"""
    fig, ax = plt.subplots(figsize=(3, 1))
    x = np.linspace(-8, 8, 400)
    y = np.zeros_like(x)

    # Fondo
    ax.axhline(0, color='black', linewidth=1)
    ax.set_yticks([])
    ax.set_xlim(-8, 8)
    ax.set_xticks(range(-8, 9))
    ax.grid(True, linestyle='--', alpha=0.4)

    if tipo == "y":
        ax.plot(x, y, 'lightgray')
        ax.plot(x[(x >= a) & (x < b)], y[(x >= a) & (x < b)], color="blue", linewidth=3)
        ax.plot([a], [0], marker='o', color='blue', fillstyle='none', markersize=8)
        ax.plot([b], [0], marker='o', color='blue', markersize=8)
    else:
        ax.plot(x, y, 'lightgray')
        ax.plot(x[(x <= a)], y[(x <= a)], color="blue", linewidth=3)
        ax.plot(x[(x > b)], y[(x > b)], color="blue", linewidth=3)
        ax.plot([a], [0], marker='o', color='blue', markersize=8)
        ax.plot([b], [0], marker='o', color='blue', fillstyle='none', markersize=8)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf

def shuffle_without_alignment(correct_list):
    """Baraja una lista sin que ningún elemento quede en su posición original"""
    shuffled = list(range(len(correct_list)))
    while True:
        random.shuffle(shuffled)
        if all(shuffled[i] != i for i in range(len(correct_list))):
            return shuffled

preguntas = []
respuestas = []

for i in range(5):
    # Generar desigualdad compuesta
    tipo = random.choice(["y", "o"])
    
    if tipo == "y":
        # Desigualdad tipo: a ≤ x < b
        a = random.randint(-8, 5)
        b = a + random.randint(3, 8)
        
        pregunta = f"{a} ≤ x < {b}"
        resp_pares = f"x ≥ {a} y x < {b}"
        resp_grafica = generar_grafica(tipo, a, b)
        resp_notacion = f"[{a}, {b})"
        
    else:  # tipo "o"
        # Desigualdad tipo: x ≤ a o x > b
        a = random.randint(-5, 3)
        b = a + random.randint(4, 10)
        
        pregunta = f"x ≤ {a} o x > {b}"
        resp_pares = f"x ≤ {a} o x > {b}"
        resp_grafica = generar_grafica(tipo, a, b)
        resp_notacion = f"(-∞, {a}] ∪ ({b}, ∞)"
    
    preguntas.append(pregunta)
    respuestas.append({
        'pares': resp_pares,
        'grafica': resp_grafica,
        'notacion': resp_notacion
    })

# Crear índices desordenados para cada columna
indices_pares = shuffle_without_alignment([i for i in range(5)])
indices_graficas = shuffle_without_alignment([i for i in range(5)])
indices_notaciones = shuffle_without_alignment([i for i in range(5)])

# Crear listas desordenadas
pares_desordenados = [respuestas[indices_pares[i]]['pares'] for i in range(5)]
graficas_desordenadas = [respuestas[indices_graficas[i]]['grafica'] for i in range(5)]
notaciones_desordenadas = [respuestas[indices_notaciones[i]]['notacion'] for i in range(5)]

# Mostrar las cuatro columnas
st.write("**Observa las siguientes columnas y relaciona cada desigualdad con su par, gráfica y notación:**")
st.write("---")

cols = st.columns(4)
headers = ["Desigualdad", "Pares de desigualdades", "Gráfica", "Notación"]
for c, h in zip(cols, headers):
    c.markdown(f"**{h}**")

for i in range(5):
    c1, c2, c3, c4 = st.columns(4)
    c1.write(f"**{i+1}.** {preguntas[i]}")
    c2.write(f"**{chr(65+i)}.** {pares_desordenados[i]}")
    with c3:
        st.write(f"**{chr(65+i)}.**")
        st.image(graficas_desordenadas[i], use_container_width=True)
    c4.write(f"**{chr(65+i)}.** {notaciones_desordenadas[i]}")

st.write("---")

#Reutilizable
with st.form("my_form"):
    st.write("**Instrucciones:** Para cada desigualdad (1-5), indica qué letra (A-E) corresponde en cada columna.")
    st.write("---")
    
    respuestas_estudiante = []
    
    for i in range(5):
        st.write(f"**Desigualdad {i+1}:** {preguntas[i]}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            par_letra = st.selectbox(f"Par:", options=['A', 'B', 'C', 'D', 'E'], key=f"par_{i}")
        with col2:
            graf_letra = st.selectbox(f"Gráfica:", options=['A', 'B', 'C', 'D', 'E'], key=f"graf_{i}")
        with col3:
            not_letra = st.selectbox(f"Notación:", options=['A', 'B', 'C', 'D', 'E'], key=f"not_{i}")
        
        respuestas_estudiante.append({
            'par': ord(par_letra) - 65,  # Convertir A-E a 0-4
            'grafica': ord(graf_letra) - 65,
            'notacion': ord(not_letra) - 65
        })
        st.write("---")

    logrado = st.form_submit_button('Confirmar respuestas', on_click=disable_button, disabled=st.session_state.button_disabled)

#Reutilizable
if logrado:
    pts = 0
    
    for i in range(5):
        resp_est = respuestas_estudiante[i]
        
        # Encontrar las posiciones correctas en las listas desordenadas
        # Necesitamos saber en qué posición de las listas desordenadas está la respuesta correcta
        pos_par_correcta = indices_pares.index(i)
        pos_graf_correcta = indices_graficas.index(i)
        pos_not_correcta = indices_notaciones.index(i)
        
        # Verificar si las respuestas son correctas
        par_correcto = resp_est['par'] == pos_par_correcta
        graf_correcta = resp_est['grafica'] == pos_graf_correcta
        not_correcta = resp_est['notacion'] == pos_not_correcta
        
        # Si todas son correctas, suma punto
        if par_correcto and graf_correcta and not_correcta:
            st.success(f"{i+1}. ¡Correcto! Todas las correspondencias son correctas.")
            pts += 1
        else:
            # Mostrar las respuestas correctas
            errores = []
            if not par_correcto:
                errores.append(f"Par: {chr(65+pos_par_correcta)}")
            if not graf_correcta:
                errores.append(f"Gráfica: {chr(65+pos_graf_correcta)}")
            if not not_correcta:
                errores.append(f"Notación: {chr(65+pos_not_correcta)}")
            
            mensaje_error = f"{i+1}. Las respuestas correctas eran → " + " | ".join(errores)
            st.warning(mensaje_error)
        
        time.sleep(0.8)

    if pts == 5:
        st.write(f"Felicidades por contestar todo bien. Obtienes", info[2], "punto(s) adicional.")
        pts += info[2]
    
    pts = int((pts * 0.7) + (pts * 0.3 * info[2]) + 0.1)
    std_ac = std_info[3] + pts 
    std_tot = std_info[4] + pts
    
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
