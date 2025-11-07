#Reutilizable
import streamlit as st
import random
import time 
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

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
limite = session.sql(query_limite).collect()[0]["LIMITE"] * 2

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

# Generar una desigualdad lineal aleatoria
def generar_desigualdad():
    # Generar m y b_val como enteros primero para garantizar resultados enteros
    m = random.randint(-4, 4)
    while m == 0:
        m = random.randint(-4, 4)
    b_val = random.randint(-8, 8)
    
    # Elegir b (usualmente 1 o -1 para simplificar, pero también otros valores)
    b = random.choice([-1, 1, -2, 2, -3, 3])
    
    # Calcular a y c para que m = -a/b y b_val = c/b sean enteros
    a = -m * b
    c = b_val * b
    
    operadores = ['<', '>', '≤', '≥']
    operador = random.choice(operadores)
    
    # Formato: ax + by operador c
    if a == 1:
        term_x = "x"
    elif a == -1:
        term_x = "-x"
    else:
        term_x = f"{a}x"
    
    if b == 1:
        term_y = " + y"
    elif b == -1:
        term_y = " - y"
    elif b > 0:
        term_y = f" + {b}y"
    else:
        term_y = f" - {abs(b)}y"
    
    desigualdad = f"{term_x}{term_y} {operador} {c}"
    
    # Calcular la forma despejada correcta: y = mx + b
    # ax + by operador c
    # by operador c - ax
    # Si b > 0: y operador (c - ax)/b
    # Si b < 0: y operador_inverso (c - ax)/|b|
    
    # Formatear m (siempre entero)
    if m == 1:
        term_m = "x"
    elif m == -1:
        term_m = "-x"
    else:
        term_m = f"{m}x"
    
    # Formatear b_val (siempre entero)
    if b_val == 0:
        term_b = ""
    elif b_val > 0:
        term_b = f" + {b_val}"
    else:
        term_b = f" - {abs(b_val)}"
    
    if b > 0:
        if operador == '<':
            despeje_correcto = f"y < {term_m}{term_b}"
            tipo_linea = "punteada"
            sombrear_arriba = False
        elif operador == '>':
            despeje_correcto = f"y > {term_m}{term_b}"
            tipo_linea = "punteada"
            sombrear_arriba = True
        elif operador == '≤':
            despeje_correcto = f"y ≤ {term_m}{term_b}"
            tipo_linea = "continua"
            sombrear_arriba = False
        else:  # ≥
            despeje_correcto = f"y ≥ {term_m}{term_b}"
            tipo_linea = "continua"
            sombrear_arriba = True
    else:  # b < 0
        if operador == '<':
            despeje_correcto = f"y > {term_m}{term_b}"
            tipo_linea = "punteada"
            sombrear_arriba = True
        elif operador == '>':
            despeje_correcto = f"y < {term_m}{term_b}"
            tipo_linea = "punteada"
            sombrear_arriba = False
        elif operador == '≤':
            despeje_correcto = f"y ≥ {term_m}{term_b}"
            tipo_linea = "continua"
            sombrear_arriba = True
        else:  # ≥
            despeje_correcto = f"y ≤ {term_m}{term_b}"
            tipo_linea = "continua"
            sombrear_arriba = False
    
    return {
        "desigualdad": desigualdad,
        "a": a,
        "b": b,
        "c": c,
        "operador": operador,
        "despeje_correcto": despeje_correcto,
        "m": m,
        "b_val": b_val,
        "tipo_linea": tipo_linea,
        "sombrear_arriba": sombrear_arriba
    }

# Generar opciones de despeje (una correcta y 4 incorrectas)
def generar_opciones_despeje(desigualdad_info):
    opciones = [desigualdad_info["despeje_correcto"]]
    
    # Generar 4 opciones incorrectas (solo enteros)
    for _ in range(4):
        m_incorrecto = desigualdad_info["m"] + random.randint(-3, 3)
        while m_incorrecto == desigualdad_info["m"]:
            m_incorrecto = desigualdad_info["m"] + random.randint(-3, 3)
        if m_incorrecto == 0:
            m_incorrecto = random.choice([-1, 1])
        
        b_incorrecto = desigualdad_info["b_val"] + random.randint(-4, 4)
        while b_incorrecto == desigualdad_info["b_val"]:
            b_incorrecto = desigualdad_info["b_val"] + random.randint(-4, 4)
        
        # Formatear m_incorrecto
        if m_incorrecto == 1:
            term_m_inc = "x"
        elif m_incorrecto == -1:
            term_m_inc = "-x"
        else:
            term_m_inc = f"{m_incorrecto}x"
        
        # Formatear b_incorrecto
        if b_incorrecto == 0:
            term_b_inc = ""
        elif b_incorrecto > 0:
            term_b_inc = f" + {b_incorrecto}"
        else:
            term_b_inc = f" - {abs(b_incorrecto)}"
        
        # Variar el operador también
        operadores_incorrectos = ['<', '>', '≤', '≥']
        operador_incorrecto = random.choice(operadores_incorrectos)
        
        opcion_incorrecta = f"y {operador_incorrecto} {term_m_inc}{term_b_inc}"
        opciones.append(opcion_incorrecta)
    
    random.shuffle(opciones)
    indice_correcto = opciones.index(desigualdad_info["despeje_correcto"])
    
    return opciones, indice_correcto

# Generar gráfica de desigualdad
def generar_grafica(m, b_val, tipo_linea, sombrear_arriba, es_correcta=False):
    fig, ax = plt.subplots(figsize=(6, 6))
    
    x = np.linspace(-10, 10, 400)
    y_linea = m * x + b_val
    
    # Crear una región de sombreado más precisa
    x_fill = np.linspace(-10, 10, 400)
    y_fill_line = m * x_fill + b_val
    
    # Sombreado
    if sombrear_arriba:
        # Sombrear arriba de la línea
        y_fill_top = np.full_like(x_fill, 10)  # Límite superior del gráfico
        ax.fill_between(x_fill, y_fill_line, y_fill_top, alpha=0.3, color='lightblue', 
                       where=(y_fill_line <= 10))
    else:
        # Sombrear abajo de la línea
        y_fill_bottom = np.full_like(x_fill, -10)  # Límite inferior del gráfico
        ax.fill_between(x_fill, y_fill_bottom, y_fill_line, alpha=0.3, color='lightblue',
                       where=(y_fill_line >= -10))
    
    # Dibujar la línea después del sombreado para que se vea encima
    if tipo_linea == "continua":
        ax.plot(x, y_linea, 'b-', linewidth=2.5)
    else:  # punteada
        ax.plot(x, y_linea, 'b--', linewidth=2.5, dashes=(5, 5))
    
    # Agregar puntos para x = -1, 0, 1
    x_puntos = [-1, 0, 1]
    y_puntos = [m * x_p + b_val for x_p in x_puntos]
    
    # Marcar los puntos con círculos rojos más grandes y visibles
    ax.scatter(x_puntos, y_puntos, color='red', s=100, zorder=5, edgecolors='darkred', linewidths=2)
    
    # Agregar etiquetas a los puntos
    for i, (x_p, y_p) in enumerate(zip(x_puntos, y_puntos)):
        ax.annotate(f'({x_p}, {int(y_p)})', 
                   xy=(x_p, y_p), 
                   xytext=(5, 5), 
                   textcoords='offset points',
                   fontsize=9,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                   zorder=6)
    
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.axhline(y=0, color='k', linewidth=0.8, zorder=0)
    ax.axvline(x=0, color='k', linewidth=0.8, zorder=0)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.set_title('Gráfica de la desigualdad', fontsize=14, fontweight='bold')
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf

# Generar gráficas incorrectas
def generar_graficas_incorrectas(desigualdad_info):
    graficas = []
    
    # Gráfica 1: Tipo de línea incorrecto
    tipo_linea_incorrecto = "continua" if desigualdad_info["tipo_linea"] == "punteada" else "punteada"
    graficas.append({
        "imagen": generar_grafica(desigualdad_info["m"], desigualdad_info["b_val"], 
                                  tipo_linea_incorrecto, desigualdad_info["sombrear_arriba"]),
        "descripcion": "Tipo de línea incorrecto"
    })
    
    # Gráfica 2: Región sombreada incorrecta
    sombrear_incorrecto = not desigualdad_info["sombrear_arriba"]
    graficas.append({
        "imagen": generar_grafica(desigualdad_info["m"], desigualdad_info["b_val"], 
                                  desigualdad_info["tipo_linea"], sombrear_incorrecto),
        "descripcion": "Región sombreada incorrecta"
    })
    
    # Gráfica 3: Pendiente incorrecta
    m_incorrecto = desigualdad_info["m"] + random.randint(-2, 2)
    while m_incorrecto == desigualdad_info["m"]:
        m_incorrecto = desigualdad_info["m"] + random.randint(-2, 2)
    if m_incorrecto == 0:
        m_incorrecto = random.choice([-1, 1])
    graficas.append({
        "imagen": generar_grafica(m_incorrecto, desigualdad_info["b_val"], 
                                  desigualdad_info["tipo_linea"], desigualdad_info["sombrear_arriba"]),
        "descripcion": "Pendiente incorrecta"
    })
    
    # Gráfica 4: Intersección incorrecta
    b_incorrecto = desigualdad_info["b_val"] + random.randint(-3, 3)
    while b_incorrecto == desigualdad_info["b_val"]:
        b_incorrecto = desigualdad_info["b_val"] + random.randint(-3, 3)
    graficas.append({
        "imagen": generar_grafica(desigualdad_info["m"], b_incorrecto, 
                                  desigualdad_info["tipo_linea"], desigualdad_info["sombrear_arriba"]),
        "descripcion": "Intersección incorrecta"
    })
    
    # Gráfica correcta
    grafica_correcta = {
        "imagen": generar_grafica(desigualdad_info["m"], desigualdad_info["b_val"], 
                                  desigualdad_info["tipo_linea"], desigualdad_info["sombrear_arriba"], 
                                  es_correcta=True),
        "descripcion": "Gráfica correcta"
    }
    
    graficas.append(grafica_correcta)
    random.shuffle(graficas)
    
    indice_correcto = next(i for i, g in enumerate(graficas) if g["descripcion"] == "Gráfica correcta")
    
    return graficas, indice_correcto

# Generar el ejercicio
desigualdad_info = generar_desigualdad()
opciones_despeje, indice_despeje_correcto = generar_opciones_despeje(desigualdad_info)
graficas, indice_grafica_correcta = generar_graficas_incorrectas(desigualdad_info)

# --- Mostrar formulario ---
st.write("**Instrucciones:** Resuelve la desigualdad paso a paso y selecciona la gráfica correcta.")
st.write("---")

#Reutilizable
with st.form("my_form"):
    st.subheader("Paso 1: Despejar la desigualdad")
    st.write("**Desigualdad inicial:**")
    st.latex(desigualdad_info["desigualdad"])
    
    # Tooltip/info sobre la regla de cambio de signo
    with st.expander("💡¡Recuerda!", expanded=False):
        st.info("""
        **¡No olvides cambiar la desigualdad!** 
        
        Si multiplicas o divides por un número negativo, ¡tienes que voltear la desigualdad!
        
        **Ejemplo paso a paso:**
        
        Si tienes: **-y < 2 + x**
        
        1. Para dejar la 'y' positiva, multiplica toda la desigualdad por **-1**
        2. **-y × (-1) < (2 + x) × (-1)**
        3. **y > -2 - x**  ← ¡El signo cambió de '<' a '>'!
        
        **Regla general:**
        - Si tienes **<** y multiplicas/divides por negativo → se convierte en **>**
        - Si tienes **>** y multiplicas/divides por negativo → se convierte en **<**
        - Si tienes **≤** y multiplicas/divides por negativo → se convierte en **≥**
        - Si tienes **≥** y multiplicas/divides por negativo → se convierte en **≤**
        """)
    
    st.write("**Selecciona la forma despejada correcta (y = mx + b):**")
    
    despeje_seleccionado = st.radio(
        "Opciones de despeje:",
        opciones_despeje,
        key="despeje"
    )
    
    st.write("---")
    st.subheader("Paso 2: Completar la tabla")
    st.write("**Usando la forma despejada, completa la siguiente tabla calculando los valores de y:**")
    
    # Mostrar la tabla
    st.markdown("""
    | x | y |
    |---|---|
    | -1 |   |
    | 0  |   |
    | 1  |   |
    """)
    
    # Campos de entrada para los valores de y
    y_menos1 = st.number_input("Para x = -1, y =", value=None, step=1, key="y_menos1")
    y_0 = st.number_input("Para x = 0, y =", value=None, step=1, key="y_0")
    y_1 = st.number_input("Para x = 1, y =", value=None, step=1, key="y_1")
    
    st.write("---")
    st.subheader("Paso 3: Tipo de línea")
    st.write("**¿Qué tipo de línea se debe usar?**")
    st.write("- **Línea continua** (para ≤ o ≥)")
    st.write("- **Línea punteada** (para < o >)")
    
    tipo_linea_seleccionado = st.radio(
        "Tipo de línea:",
        ["Línea continua", "Línea punteada"],
        key="tipo_linea"
    )
    
    st.write("---")
    st.subheader("Paso 4: Región a sombrear")
    st.write("**¿Qué región se debe sombrear?**")
    
    region_seleccionada = st.radio(
        "Región:",
        ["Arriba de la línea", "Abajo de la línea"],
        key="region"
    )
    
    st.write("---")
    st.subheader("Paso 5: Seleccionar la gráfica correcta")
    st.write("**Observa las siguientes gráficas y selecciona la que representa correctamente la desigualdad:**")
    
    # Mostrar gráficas en columnas (3 columnas, 2 filas)
    opciones_graficas = []
    
    # Primera fila (3 gráficas)
    cols1 = st.columns(3)
    for i in range(3):
        with cols1[i]:
            st.image(graficas[i]["imagen"], use_container_width=True)
            opciones_graficas.append(f"Gráfica {i+1}")
    
    # Segunda fila (2 gráficas)
    cols2 = st.columns(3)
    for i in range(3, 5):
        with cols2[i - 3]:
            st.image(graficas[i]["imagen"], use_container_width=True)
            opciones_graficas.append(f"Gráfica {i+1}")
    
    grafica_seleccionada = st.radio(
        "Selecciona la gráfica correcta:",
        opciones_graficas,
        key="grafica"
    )
    
    logrado = st.form_submit_button('Confirmar respuestas', on_click=disable_button, disabled=st.session_state.button_disabled)

#Reutilizable
if logrado:
    pts = 0
    respuestas_correctas = 0
    
    # Verificar despeje
    despeje_correcto = (despeje_seleccionado == desigualdad_info["despeje_correcto"])
    if despeje_correcto:
        st.success("✅ Paso 1: Despeje correcto")
        respuestas_correctas += 1
    else:
        st.warning(f"❌ Paso 1: Despeje incorrecto. La respuesta correcta era: {desigualdad_info['despeje_correcto']}")
    time.sleep(0.8)
    
    # Verificar tabla (calcular valores correctos de y)
    m = desigualdad_info["m"]
    b_val = desigualdad_info["b_val"]
    y_correcto_menos1 = m * (-1) + b_val
    y_correcto_0 = m * 0 + b_val
    y_correcto_1 = m * 1 + b_val
    
    tabla_correcta = True
    tabla_respuestas = []
    
    if y_menos1 is not None and int(y_menos1) == int(y_correcto_menos1):
        tabla_respuestas.append(True)
    else:
        tabla_respuestas.append(False)
        tabla_correcta = False
    
    if y_0 is not None and int(y_0) == int(y_correcto_0):
        tabla_respuestas.append(True)
    else:
        tabla_respuestas.append(False)
        tabla_correcta = False
    
    if y_1 is not None and int(y_1) == int(y_correcto_1):
        tabla_respuestas.append(True)
    else:
        tabla_respuestas.append(False)
        tabla_correcta = False
    
    if tabla_correcta:
        st.success("✅ Paso 2: Tabla correcta")
        respuestas_correctas += 1
    else:
        mensaje_tabla = f"❌ Paso 2: Tabla incorrecta. Los valores correctos eran: "
        mensaje_tabla += f"x=-1 → y={int(y_correcto_menos1)}, "
        mensaje_tabla += f"x=0 → y={int(y_correcto_0)}, "
        mensaje_tabla += f"x=1 → y={int(y_correcto_1)}"
        st.warning(mensaje_tabla)
    time.sleep(0.8)
    
    # Verificar tipo de línea
    tipo_linea_correcto = False
    if desigualdad_info["tipo_linea"] == "continua" and tipo_linea_seleccionado == "Línea continua":
        tipo_linea_correcto = True
    elif desigualdad_info["tipo_linea"] == "punteada" and tipo_linea_seleccionado == "Línea punteada":
        tipo_linea_correcto = True
    
    if tipo_linea_correcto:
        st.success(f"✅ Paso 3: Tipo de línea correcto ({desigualdad_info['tipo_linea']})")
        respuestas_correctas += 1
    else:
        st.warning(f"❌ Paso 3: Tipo de línea incorrecto. La respuesta correcta era: Línea {desigualdad_info['tipo_linea']}")
    time.sleep(0.8)
    
    # Verificar región
    region_correcta = False
    if desigualdad_info["sombrear_arriba"] and region_seleccionada == "Arriba de la línea":
        region_correcta = True
    elif not desigualdad_info["sombrear_arriba"] and region_seleccionada == "Abajo de la línea":
        region_correcta = True
    
    if region_correcta:
        st.success(f"✅ Paso 4: Región correcta ({'Arriba' if desigualdad_info['sombrear_arriba'] else 'Abajo'})")
        respuestas_correctas += 1
    else:
        st.warning(f"❌ Paso 4: Región incorrecta. La respuesta correcta era: {'Arriba' if desigualdad_info['sombrear_arriba'] else 'Abajo'} de la línea")
    time.sleep(0.8)
    
    # Verificar gráfica
    indice_seleccionado = opciones_graficas.index(grafica_seleccionada)
    grafica_correcta = (indice_seleccionado == indice_grafica_correcta)
    
    if grafica_correcta:
        st.success("✅ Paso 5: Gráfica correcta")
        respuestas_correctas += 1
    else:
        st.warning(f"❌ Paso 5: Gráfica incorrecta. La gráfica correcta era la Gráfica {indice_grafica_correcta + 1}")
    time.sleep(0.8)
    
    # Calcular puntos
    pts = respuestas_correctas
    
    pts_extra = 0
    if pts == 5:
        st.write(f"Felicidades por contestar todo bien. Obtienes", info[2], "punto(s) adicional.")
        pts_extra += info[2]
    
    st.info("Obtuviste: " + str(int(pts * 0.8)) + " puntos extra por esta práctica!")
    
    pts = int((pts * 0.7) + (pts * 0.3 * info[2]) + 0.1 + (pts * 0.8) + pts_extra)
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

