import streamlit as st
from openai import OpenAI
from pathlib import Path

__import__('pysqlite3')

import sys
sys.modules['sqlite3']=sys.modules.pop('pysqlite3')

import chromadb


# define the message to get the number of messages to pass to the LLM
def get_messages(list_messages,k):
    beggining = (k*2)+1
    output = list_messages[-beggining:]
    return output 

def add_to_collection(collection,text,filename):
    #create an embedding
    openai_client = st.session_state.openai_client
    response = openai_client.embeddings.create(
        input = text,
        model = 'text-embedding-3-small'
    )
    #get the embedding
    embedding = response.data[0].embedding
    #add embedding and document to chromaDB
    collection.add(
        documents = [text],
        ids = [filename],
        embeddings = [embedding]
    )


# Lab 4
folder_path = Path("../lab4_files/")

# Loop through all files in the folder
for file_path in folder_path.iterdir():
    text = file_path.read().decode()
    add_to_collection('Lab4Collection',text,file_path)
    

# Show title and description.
st.title("Page 4: Chatbot")

st.sidebar.title (":red[Labs]")

if st.sidebar.checkbox('Use Advance Model'):
    model = 'gpt-4o'
else: model = 'gpt-4o-mini'


# new lab 4
topic = st.sidebar.selectbox('Topic',('Text Mining','GenAI'))

# Create an OpenAi client
if 'client' not in st.session_state:
    openai_api_key = st.secrets['Openai_key']
    st.session_state.openai_client = OpenAI(api_key=openai_api_key)



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
    openai_client = st.session_state.openai_client

    
    # new lab 4
    response = openai_client.embeddings.create(
        input = topic,
        model = 'text-embedding-3-small'
    )

    query_embedding = response.data[0].embedding
    results = collection.query(
        query_embedding = [query_embedding],
        n_results = 3 
    )

    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        doc_id = results['id'][0][i]
        st.write (f'the following file/syllabus might be helpful: {doc_id}')


    messages_to_pass = get_messages(st.session_state.messages,2)

    stream = openai_client.chat.completions.create(
        model=model,
        messages = messages_to_pass,
        stream = True
    )

    with st.chat_message('assistant'):
        responses = st.write_stream(stream)

    st.session_state.messages.append({'role':'assistant','content':responses})

    #st.write(messages_to_pass)
