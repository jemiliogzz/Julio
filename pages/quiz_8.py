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

def resuelve_par(expresion):
  expresion.replace("  ", " ")
  x = expresion.rfind('(')
  res = expresion

  if x > -1:
    res = expresion[x + 1:]
    y = res.find(')')
    res = res[:y]

  aux = ''
  while res != aux:
    aux = res
    res = resuelve_exp(res)
    res = res.replace("  ", " ")

  aux = ''
  while res != aux:
    aux = res
    res = resuelve_mul_div(res)
    res = res.replace("  ", " ")

  aux = ''
  while res != aux:
    aux = res
    res = resuelve_sum_res(res)
    res = res.replace("  ", " ")

  if x == -1:
    expresion = res
  else:
    expresion = expresion[:x] + res + expresion[y + x + 2:]

  return expresion.replace("  ", " ")

def resuelve_exp(expresion):
  x = expresion.find('^')
  if x > -1:
    espacio_previo = expresion.rfind(' ', 0, x - 1)
    espacio_posterior = expresion.find(' ', x + 2)

    expresion = expresion[:espacio_previo] + ' ' + str(round(float(expresion[espacio_previo:x-1]) ** float(expresion[x+2:espacio_posterior]), 2)) + expresion[espacio_posterior:]

  return expresion

def resuelve_mul_div(expresion):
  x = expresion.find('*')
  y = expresion.find('/')

  if (x < y or y < 0) and x > -1:
    espacio_previo = expresion.rfind(' ', 0, x - 1)
    espacio_posterior = expresion.find(' ', x + 2)
    expresion = expresion[:espacio_previo + 1] + str(round(float(expresion[espacio_previo:x-1]) * float(expresion[x+2:espacio_posterior]), 2)) + expresion[espacio_posterior:]
  elif y > -1:
    espacio_previo = expresion.rfind(' ', 0, y - 1)
    espacio_posterior = expresion.find(' ', y + 2)
    expresion = expresion[:espacio_previo + 1] + str(round(float(expresion[espacio_previo:y-1]) / float(expresion[y+2:espacio_posterior]), 2)) + expresion[espacio_posterior:]

  return expresion

def resuelve_sum_res(expresion):
  x = expresion.find('+')
  y = expresion.find('-', 2)

  if (x < y or y <= 1) and x > -1:
    espacio_previo = expresion.rfind(' ', 0, x - 1)
    espacio_posterior = expresion.find(' ', x + 2)
    expresion = expresion[:espacio_previo + 1] + str(round(float(expresion[espacio_previo:x-1]) + float(expresion[x+2:espacio_posterior]), 2)) + expresion[espacio_posterior:]
  elif y > -1:
    try:
      espacio_previo = expresion.rfind(' ', 0, y - 1)
      espacio_posterior = expresion.find(' ', y + 2)
      expresion = expresion[:espacio_previo + 1] + str(round(float(expresion[espacio_previo:y-1]) - float(expresion[y+2:espacio_posterior]), 2)) + expresion[espacio_posterior:]
    except:
      return expresion

  return expresion

for i in range (5):
    #Fin

    num = random.randint(1, 5 + i)

    latex_str = str(num)
    expresion = ' ' + str(num)

    tot_op = 2
    opened = 0
    its = 3
    j = 0
    while j < its:
        operador = random.choice(['+', '+', '-', '/', '*', '^', '(', '(', ')', ')', 'skip'])
        
        if operador == 'skip':
            continue
            
        elif operador == '/':
            num = random.randint(-3 - i, 3 + i + j)
            if num == 0:
                num = 1
            latex_str += '\div' + str(num)
            expresion += ' ' + operador + ' ' + str(num)

        elif operador == '^':
            num = random.randint(1, 3)
            latex_str += operador + str(num) + '+' + str(num)
            expresion += ' ' + operador + ' ' + str(num) + ' + ' + str(num)
            j += 1
        
        elif operador == '(':
            if tot_op > 0:
                tot_op -= 1
                its += 1
                opened += 1
                prev_op = random.choice(['+', '+', '-', '-', '/', '*'])
                num = random.randint(-3 - i, 3 + i + j)
                if prev_op == '/':
                    latex_str += '\div'
        
                else:
                    latex_str += prev_op
                latex_str += '(' + str(num)    
                expresion += ' ' + prev_op + ' ' + operador + ' ' + str(num)
                
        elif operador == ')':
            its += 1
            if opened > 0:
                opened -= 1
                latex_str += ')'
                expresion += ' ' + operador
        else:
            num = random.randint(1, 5 + i + j)
            latex_str += operador + str(num)
            expresion += ' ' + operador + ' ' + str(num)

        j += 1

    for j in range (opened):
        opened -= 1
        latex_str += ')'
        expresion += ' )'

    expresion += ' '
    aux = ''

    while expresion != aux:
        aux = expresion
        expresion = resuelve_par(expresion)

    preguntas.append(latex_str)
    respuestas.append(float(expresion.replace(" ", "")))
    
#Reutilizable
with st.form("my_form"):
    st.write("**Instrucciones:** Para cada operación, resuelve y encuentra el resultado.")
    st.write("---")
    
    respuestas_estudiante = []
    
    for i in range(5):
        st.write(f"**Pregunta {i+1}:**")
        st.latex(preguntas[i])
        res_est = st.text_input(f"{i+1}. Ingresa tu respuesta:", key=f"resp_{i}")
        
        if res_est:
            try:
                res_est = float(res_est)
            except:
                st.warning('Ingresa un numero válido')
        
        respuestas_estudiante.append(res_est)
        st.write("---")
    
    logrado = st.form_submit_button('Confirmar respuestas', on_click=disable_button, disabled=st.session_state.button_disabled)

#Reutilizable
if logrado:
    pts = 0
    
    for i in range(5):
        if respuestas[i] == respuestas_estudiante[i]:
            st.success(f"{i+1}. Bravooo")
            pts += 1
        else:
            mensaje_error = f"{i+1}. La respuesta era: " + str(respuestas[i])
            st.warning(mensaje_error)
        
        time.sleep(0.8)

    pts_extra = 0
    if pts == 5:
        st.write(f"Felicidades por contestar todo bien. Obtienes", info[2], "punto(s) adicional.")
        pts_extra += info[2]
    
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
    
