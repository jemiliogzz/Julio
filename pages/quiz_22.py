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

bases = ['a', 'b', 'x', 'y']
leyes = [
    ("a^m * a^n = a^(m+n)", "Producto de potencias de igual base"),
    ("(a^m)^n = a^(m*n)", "Potencia de una potencia"),
    ("(ab)^n = a^n * b^n", "Potencia de un producto"),
    ("(a/b)^n = a^n / b^n", "Potencia de un cociente"),
    ("a^m / a^n = a^(m-n)", "Cociente de potencias de igual base"),
    ("a^-n = 1/a^n", "Exponente negativo"),
    ("a^0 = 1", "Exponente cero"),
]

# Seleccionamos 5 leyes al azar
seleccionadas = random.sample(leyes, 5)

ejercicios = []
for ley, nombre in seleccionadas:
    base = random.choice(bases)
    m = random.randint(1, 5)
    n = random.randint(1, 5)

    if "m+n" in ley:
        expr = f"{base}^{m} * {base}^{n}"
        res = f"{base}^{m+n}"
    elif "m*n" in ley:
        expr = f"({base}^{m})^{n}"
        res = f"{base}^{m*n}"
    elif "(ab)" in ley:
        expr = f"({bases[0]}{bases[1]})^{n}"
        res = f"{bases[0]}^{n} * {bases[1]}^{n}"
    elif "(a/b)" in ley:
        expr = f"({bases[0]}/{bases[1]})^{n}"
        res = f"{bases[0]}^{n}/{bases[1]}^{n}"
    elif "m-n" in ley:
        expr = f"{base}^{m} / {base}^{n}"
        res = f"{base}^{m-n}"
    elif "1/a^n" in ley:
        expr = f"{base}^-{n}"
        res = f"1/{base}^{n}"
    elif "a^0" in ley:
        expr = f"{base}^0"
        res = "1"

    ejercicios.append({
        "expresion": expr,
        "resultado": res,
        "ley": nombre
    })

# Mezclamos resultados y leyes (sin repetir)
resultados_mezclados = random.sample([e["resultado"] for e in ejercicios], len(ejercicios))
leyes_mezcladas = random.sample([e["ley"] for e in ejercicios], len(ejercicios))

# --- Mostrar formulario ---
st.write("### 🧠 Une la expresión con su resultado y la ley correspondiente")

#Reutilizable
with st.form("my_form"):
    respuestas = []
    for i, e in enumerate(ejercicios):
        st.write(f"#### Ejercicio {i+1}")
        st.latex(e['expresion'])

        col1, col2 = st.columns(2)
        with col1:
            r_sel = st.selectbox(f"Resultado {i+1}", resultados_mezclados, key=f"res_{i}")
        with col2:
            l_sel = st.selectbox(f"Ley {i+1}", leyes_mezcladas, key=f"ley_{i}")

        respuestas.append((r_sel, l_sel))
        st.write("---")

    logrado = st.form_submit_button('Confirmar respuestas', on_click=disable_button, disabled=st.session_state.button_disabled)

#Reutilizable
if logrado:
    pts = 0
    for i, e in enumerate(ejercicios):
        correcto = (respuestas[i][0] == e["resultado"]) and (respuestas[i][1] == e["ley"])
        if correcto:
            st.success(f"✅ Ejercicio {i+1}: Correcto ({e['ley']})")
            pts += 1
        else:
            st.warning(f"❌ Ejercicio {i+1}: Era {e['resultado']} – {e['ley']}")
        time.sleep(0.5)

    if pts == 5:
        st.write(f"Felicidades por contestar todo bien. Obtienes", info[2], "punto(s) adicional.")
        pts += info[2]
    
    st.info("Obtuviste: " + str(int(pts * 1.7)) + " puntos extra por esta práctica!")
    
    pts = int((pts * 0.7) + (pts * 0.3 * info[2]) + 0.1 + (pts * 1.7))
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
