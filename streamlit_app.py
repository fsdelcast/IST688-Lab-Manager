import streamlit as st
from openai import OpenAI

lab1_page = st.Page("Lab_1.py", title = 'Lab 1', icon="📄")
lab2_page = st.Page("Lab_2.py", title = 'Lab 2', icon="📄")

pg = st.navigation ([lab1_page,lab2_page])
st.set_page_config(page_title = 'This is not showing',page_icon = '💯')
pg.run()
