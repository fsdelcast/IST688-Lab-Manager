import streamlit as st
from openai import OpenAI

# define the message to get the number of messages to pass to the LLM
def get_messages(list_messages,k):
    beggining = (k*2)+1
    output = list_messages[-beggining:]
    return output 

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
    st.session_state['messages']=\
        [{'role':'assistant','content':'I want to answer a question'}]

for msg in st.session_state.messages:
    st.chat_message(msg['role']).write(msg['content'])

if prompt := st.chat_input('Ask a question'):
    
    #end_text = ' At the end, ask me "DO YOU WANT MORE INFO?"'
    #full_prompt = prompt + end_text 
    
    st.chat_message ('user').write(prompt)

    st.session_state.messages.append({'role':'user','content':prompt})
    client = st.session_state.client

    if prompt in ['No','no','NO']:
        full_responses = 'I want to answer a question'
        st.write(full_responses)
        #st.chat_message('assistant').write('I want to answer a question')
    else:
        messages_to_pass = get_messages(st.session_state.messages,2)

        stream = client.chat.completions.create(
            model=model,
            messages = messages_to_pass,
            stream = True
        )

        with st.chat_message('assistant'):
            responses = st.write_stream(stream)
            full_responses = responses + ' DO YOU WANT MORE INFO?'
            st.write ('DO YOU WANT MORE INFO?')
    
    st.session_state.messages.append({'role':'assistant','content':full_responses})

    #st.write(messages_to_pass)
