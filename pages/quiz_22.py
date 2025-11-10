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
    ("a^m * a^n = a^(m+n)", "Multiplicando bases iguales"),
    ("(a^m)^n = a^(m*n)", "Una potencia elevada a una potencia"),
    ("(ab)^n = a^n * b^n", "El producto de una potencia"),
    ("(a/b)^n = a^n / b^n", "El cociente de una potencia"),
    ("a^m / a^n = a^(m-n)", "Dividiendo bases iguales"),
    ("a^-n = 1/a^n", "Definición de un exponente negativo"),
    ("a^0 = 1", "Definición de un exponente cero"),
]

# Obtener cantidad de preguntas (5 por defecto, 3 si es examen)
cantidad_preguntas = obtener_cantidad_preguntas()

# Seleccionamos leyes al azar según la cantidad de preguntas
seleccionadas = random.sample(leyes, cantidad_preguntas)

ejercicios = []
for ley, nombre in seleccionadas:
    base = random.choice(bases)
    m = random.randint(1, 5)
    n = random.randint(1, 5)

    if "m+n" in ley:
        expr = f"{base}^{{{m}}} \\cdot {base}^{{{n}}}"
        res = f"{base}^{{{m+n}}}"
    elif "m*n" in ley:
        expr = f"({base}^{{{m}}})^{{{n}}}"
        res = f"{base}^{{{m*n}}}"
    elif "(ab)" in ley:
        expr = f"({bases[0]}{bases[1]})^{{{n}}}"
        res = f"{bases[0]}^{{{n}}} \\cdot {bases[1]}^{{{n}}}"
    elif "(a/b)" in ley:
        expr = f"\\left(\\frac{{{bases[0]}}}{{{bases[1]}}}\\right)^{{{n}}}"
        res = f"\\frac{{{bases[0]}^{{{n}}}}}{{{bases[1]}^{{{n}}}}}"
    elif "m-n" in ley:
        expr = f"\\frac{{{base}^{{{m}}}}}{{{base}^{{{n}}}}}"
        res = f"{base}^{{{m-n}}}"
    elif "1/a^n" in ley:
        expr = f"{base}^{{{-n}}}"
        res = f"\\frac{{1}}{{{base}^{{{n}}}}}"
    elif "a^0" in ley:
        expr = f"{base}^{{0}}"
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
st.write("Une la expresión con su resultado y la descripción correspondiente")

#Reutilizable
with st.form("my_form"):
    respuestas = []
    for i, e in enumerate(ejercicios):
        st.subheader(f"Pregunta {i+1}")
        st.write("**Resuelve la siguiente expresión:**")
        st.latex(e['expresion'])
        st.write("")
        
        # Mostrar opciones de resultados en columnas
        st.write("**a) Selecciona el resultado correcto:**")
        cols_res = st.columns(5)
        for j, col in enumerate(cols_res):
            with col:
                st.write(f"**{chr(65+j)}:**")
                st.latex(resultados_mezclados[j])
        
        resultado_opciones = [f"{chr(65+j)}" for j in range(5)]
        res_letra = st.radio("Selecciona tu respuesta:", resultado_opciones, 
                             key=f"res_{i}", horizontal=True, label_visibility="collapsed")
        st.write("")
        
        # Mostrar opciones de leyes
        st.write("**b) Selecciona la descripción correspondiente:**")
        l_sel = st.selectbox(f"Ley {i+1}", leyes_mezcladas, key=f"ley_{i}")
        
        # Store the index of the selected result (0-4)
        res_idx = ord(res_letra) - 65
        respuestas.append((res_idx, l_sel))
        st.write("---")

    logrado = st.form_submit_button('Confirmar respuestas', on_click=disable_button, disabled=st.session_state.button_disabled)

#Reutilizable
if logrado:
    pts = 0
    for i, e in enumerate(ejercicios):
        # Find the index of the correct result in the mixed results list
        resultado_correcto_idx = resultados_mezclados.index(e["resultado"])
        # Check if student selected the correct result index and the correct law
        correcto = (respuestas[i][0] == resultado_correcto_idx) and (respuestas[i][1] == e["ley"])
        
        if correcto:
            st.success(f"✅ Ejercicio {i+1}: Correcto ({e['ley']})")
            pts += 1
        else:
            # Find the correct letter for the result
            letra_correcta_result = chr(65 + resultado_correcto_idx)
            st.warning(f"❌ Ejercicio {i+1}: Era {letra_correcta_result} ({e['ley']})")
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
