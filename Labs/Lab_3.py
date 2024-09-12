import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("Page 3: Chatbot")

st.sidebar.title (":red[Labs]")

if st.sidebar.checkbox('Use Advance Model'):
    model = 'gpt-4o'
else: model = 'gpt-4o-mini'

# Create an OpenAi client
if 'client' not in st.session_state:
    openai_api_key = st.secrets['Openai_key']
    st.session_state.client = OpenAI(api_key=openai_api_key)

if 'messages' not in st.session_state:
    st.session_state ['messages']=\
        [{'role':'assistant','content':'How can I help you?'}]

for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.write(msg['content'])

if prompt := st.chat_input('What is up?'): 
    st.session_state.messages.append({'role':'user','content':prompt})

    with st.chat_message ('user'):
        st.write(prompt)
    
    client = st.session_state.client
    stream = client.chat.completions.create(
        model=model_to_use,
        messages = st.session_state.messages,
        stream = True
    )

    with st.chat_message('assistant'):
        respones = st.write_stream(stream)

    st.session_state.messages.append({'role':'assistant','content':response})
