import streamlit as st
from openai import OpenAI

lab1_page = st.Page("./Labs/Lab_1.py", title = 'Lab 1', icon="🥇")
lab2_page = st.Page("./Labs/Lab_2.py", title = 'Lab 2', icon="2️⃣")
lab3_page = st.Page("./Labs/Lab_3.py", title = 'Lab 3', icon="3️⃣")



pg = st.navigation ([lab3_page, lab2_page,lab1_page])
st.set_page_config(page_title = "Francisco's",page_icon = '💯')
pg.run()
