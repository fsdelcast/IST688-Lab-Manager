import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("Page 2: My Document Question Answering")

#st.write(
#    "Upload a document below and ask a question about it – GPT will answer! "
#    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
#)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
# openai_api_key = st.text_input("OpenAI API Key", type="password")


st.sidebar.title (":red[Labs]")

if st.sidebar.checkbox('Use Advance Model'):
    model = 'gpt-4o'
else: model = 'gpt-4o-mini'

summary_type = st.sidebar.selectbox('Choose a summary type',
                            ('Summarize the document in 100 words',
                             'Summarize the document in 2 connecting paragraphs',
                             'Summarize the document in 5 bullet points'))


openai_api_key = st.secrets['Openai_key']
st.write ('Do you want to know my secret? ', st.secrets['other_secret'])




if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    try:
        client.models.list()
    except:
        st.error("Invalid API key. Please input a valid API key.", icon="⛔")    
    else:
        # Let the user upload a file via `st.file_uploader`.
        uploaded_file = st.file_uploader(
            "Upload a document (.txt or .md)", type=("txt", "md")
        )


        if uploaded_file:

            # Process the uploaded file and question.
            document = uploaded_file.read().decode()
            messages = [
                {"role": "system",
                 "content": "You are an assistant that talks like a pirate"
                },
                {   
                    "role": "user",
                    "content": f"Here's a document: {document} \n\n---\n\n {summary_type}",
                }
            ]

            # Generate an answer using the OpenAI API.
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                temperature = 0
            )

            # Stream the response to the app using `st.write_stream`.
            st.write_stream(stream)
