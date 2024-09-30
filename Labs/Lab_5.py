import streamlit as st
from openai import OpenAI
from pathlib import Path
import os
from PyPDF2 import PdfReader
import PyPDF2
import requests
import json



__import__('pysqlite3')
import sys
sys.modules['sqlite3']=sys.modules.pop('pysqlite3')
import chromadb

# get the model
if st.sidebar.checkbox('Use Advance Model'):
    model = 'gpt-4o'
else: model = 'gpt-4o-mini'


def chat_completion_request(messages, tools=None, tool_choice=None, model = model):
    try:
        response = openai_client.chat.completions.create(
        model=model,
        messages = messages,
        tools=tools,
        tool_choice = tool_choice
        #stream = True
    )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

def get_current_weather(location, API_key):
    if "," in location:
        location = location.split(",")[0].strip()

    urlbase = "https://api.openweathermap.org/data/2.5/"
    urlweather = f"weather?q={location}&appid={API_key}"
    url = urlbase + urlweather
    response = requests.get(url)
    data = response.json()

    # Extract temperatures & Convert Kelvin to Celsius
    temp = data['main']['temp'] - 273.15
    feels_like = data['main']['feels_like'] - 273.15
    temp_min = data['main']['temp_min'] - 273.15
    temp_max = data['main']['temp_max'] - 273.15
    humidity = data['main']['humidity']

    return json.dumps({"location": location,
        "temperature": round(temp, 2),
        "feels_like": round(feels_like, 2),
        "temp_min": round(temp_min, 2),
        "temp_max": round(temp_max, 2),
        "humidity": round(humidity, 2)
    })

# Show title and description.
st.title("Page 5: The What to Wear Bot")
st.sidebar.title (":red[Labs]")

# Create an OpenAi client
if 'openai_client' not in st.session_state:
    openai_api_key = st.secrets['Openai_key']
    st.session_state.openai_client = OpenAI(api_key=openai_api_key)

openai_client = st.session_state.openai_client

# define the functions
tools = [
    {
            'type':'function',
            'function': {
                'name': 'get_current_weather',
                'description':'Get the current weather',
                'parameters': {
                    'type':'object',
                    'properties': {
                        'location':{
                            'type':'string',
                            'description':'The city and state, e.g. San Francisco, CA',
                        },
                        'format':{
                            'type':'string',
                            'enum':['celsius','fahrenheit'],
                            'description':'The temperature unit to use. Infer this from the users location.'
                        },
                    },
                    'required': ['location','format']
                },
            }
    },
]

# Create messages
messages = []
messages.append({'role':'system','content':"Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
messages.append({'role':'user','content':'What is the weather like today'})

# Get Responses asking for location
chat_response = chat_completion_request(
    messages,tools=tools
)

response_message = chat_response.choices[0].message
messages.append(response_message)
#st.write(response_message) #test

# give location and invokes function
messages.append({'role':'user','content':'I am in Syracuse, NY. I would like the temperaturee in Celsius.'})
chat_response = chat_completion_request(
    messages,tools=tools
)
response_message = chat_response.choices[0].message
messages.append(response_message)
#st.write(chat_response) #test
#st.write(response_message)#test

# determine if a tool has been called
tool_calls = response_message.tool_calls
if tool_calls:
    # If true the model will return the name of the tool / function to call and the arguments
    tool_call_id = tool_calls[0].id
    tool_function_name = tool_calls[0].function.name
    tool_location = eval(tool_calls[0].function.arguments)['location']

    if tool_function_name == 'get_current_weather':
        results = get_current_weather(tool_location,st.secrets['weather_key'] ) # get the arguments

        messages.append({
            'role':'tool',
            'tool_call_id':tool_call_id,
            'name':tool_function_name,
            'content':results
        })

        # Invoke the chat completions API
        #st.write(messages) #test

        model_response_with_function_call = chat_completion_request(
            messages, model = model
        )
        #st.write(model_response_with_function_call) #test
        st.write(model_response_with_function_call.choices[0].message.content)

        


    else:
        st.write(f'Error: function {tool_function_name} does not exist')
else:
    st.write(response_message.content)

# call the function and retrieve results. append results to the message list.


