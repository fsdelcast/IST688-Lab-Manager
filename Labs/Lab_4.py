import streamlit as st
from openai import OpenAI
from pathlib import Path
import os
from PyPDF2 import PdfReader
import PyPDF2

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

    metadata = meta[filename]

    #add embedding and document to chromaDB
    collection.add(
        documents = [text],
        ids = [filename],
        embeddings = [embedding],
        metadatas = [metadata]
    )

# Show title and description.
st.title("Page 4: Chatbot")
st.sidebar.title (":red[Labs]")

if st.sidebar.checkbox('Use Advance Model'):
    model = 'gpt-4o'
else: model = 'gpt-4o-mini'

# Create an OpenAi client
if 'client' not in st.session_state:
    openai_api_key = st.secrets['Openai_key']
    st.session_state.openai_client = OpenAI(api_key=openai_api_key)

# Create messages
if 'messages' not in st.session_state:
    st.session_state['messages']=\
        [{'role':'assistant','content':'I want to answer a question'}]

# Create Databases
if 'Lab4_vectorDB' not in st.session_state:
    # Chroma client
    chroma_client = chromadb.PersistentClient(path = 'chroma' )
    #chroma_client.delete_collection("Lab4Collection") #delete collection
    collection = chroma_client.get_or_create_collection(name = 'Lab4Collection')
    st.session_state['Lab4_vectorDB'] = collection

    folder_path = Path("lab4_files/")
    meta = {'IST 644 Syllabus.pdf':{'Course Title':'MANAGING DATA SCIENCE PROJECTS'},
                 'IST 652 Syllabus.pdf':{'Course Title':'SCRIPTING FOR DATA ANALYSIS'},
                 'IST 782 Syllabus.pdf':{'Course Title':'APPLIED DATA SCIENCE PORTFOLIO'},
                 'IST614 Info tech Mgmt & Policy Syllabus.pdf':{'Course Title':'Information Technology Management and Policy'},
                 'IST688-BuildingHC-AIAppsV2.pdf':{'Course Title':'Building Human-Centered AI Applications'},
                 'IST691 Deep Learning in Practice Syllabus.pdf':{'Course Title':'Deep Learning in Practice'},
                 'IST736-Text-Mining-Syllabus.pdf':{'Course Title':'Text Mining'}}
    
    # Loop through all files in the folder
    for file_path in folder_path.iterdir():
        if file_path.suffix == '.pdf':
            try:
                reader = PyPDF2.PdfReader(file_path)
                document = ''
                # loop through pages and extract the text data
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    document += page.extract_text()
                
                # Get the filename
                filename = file_path.name

                add_to_collection(collection,document,str(filename))

            except Exception as e:
                print(f"Error reading {file_path.name}: {e}")

if 'Lab4_vectorDB' in st.session_state:
    collection = st.session_state['Lab4_vectorDB']
    
    # Retrieve the documents, embeddings, and metadata from the collection
    results = collection.get()
    
    # Display the database contents in the Streamlit app
    #st.write(f"Documents: {results['documents'][0]}") # here are the documents
    #st.write(f"IDs: {results['ids']}")
    #st.write(f"Metadata: {results['metadatas']}")
    #st.write(f"Embeddings: {results['embeddings'][0]}")
    #st.write(f"Embeddings: {results['data'][0]}")




for msg in st.session_state.messages:
    st.chat_message(msg['role']).write(msg['content'])

if prompt := st.chat_input('Ask a question'): 

    st.chat_message ('user').write(prompt) # write user prompt
    st.session_state.messages.append({'role':'user','content':prompt})

    openai_client = st.session_state.openai_client

    # new lab 4 - Send querry embeding
    response = openai_client.embeddings.create(
        input = prompt,
        model = 'text-embedding-3-small'
    )
    
    # GEt the querry results
    collection = st.session_state.Lab4_vectorDB
    query_embedding = response.data[0].embedding

    results = collection.query(
        query_embeddings = [query_embedding],
        n_results = 3 
    )

    # Print query results
    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        doc_id = results['ids'][0][i]
        metadata = results['metadatas'][0][i]
        #st.write (f'the following file/syllabus might be helpful: {doc_id}')
        #st.write (f"This is the metadata: {metadata}")
        
    # Memory of 2 User messages.
    messages_to_pass = get_messages(st.session_state.messages,2)

    # Get Responses
    stream = openai_client.chat.completions.create(
        model=model,
        messages = messages_to_pass,
        stream = True
    )

    # Write Stream
    with st.chat_message('assistant'):
        responses = st.write_stream(stream)

    # Append Messages.
    st.session_state.messages.append({'role':'assistant','content':responses})

    #st.write(messages_to_pass)
