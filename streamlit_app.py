# Import python packages
import streamlit as st
import pandas as pd
import random
import time

from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

#Write directly to the app
st.title("Inicio de Sesión🧍")
st.write(
  """
  **HOLA,** 
  Aquí está el [link al drive](https://drive.google.com/drive/folders/1auNf6oiLNuRekk_Rm9r295vzChcWpWtI?usp=drive_link).
  """
)

# Get the current credentials
cnx = st.connection("snowflake")
session = cnx.session()

mat_login = st.text_input("Ingresa tu matrícula:", placeholder = '000000')

if mat_login:
    try:
        matched = session.table("primeroc.public.students").filter(col('matricula')==mat_login).collect()
    except:
        st.write("Ingresa tu matrícula de 6 digitos")
        matched = 0
    
    if matched:
        # Initialization
        if 'mat' not in st.session_state:
            st.session_state['mat'] = mat_login

        start_seed = random.randint(1,50)
        if 's_seed' not in st.session_state:
            st.session_state['s_seed'] = start_seed
            
        st.write("¡Bienvenido!")
        
        time.sleep(1)
        st.switch_page("pages/inicio.py")
        
    else:
        st.write("No existe esta matrícula. Checa cómo la escribiste.")
