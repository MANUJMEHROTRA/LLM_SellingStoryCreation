#Running command:  streamlit run Chatbot.py
import openai
import streamlit as st
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def load_custom_css():
    custom_css = Path("styles.css")
    st.markdown(f"<style>{custom_css.read_text()}</style>", unsafe_allow_html=True)

# Call the function to load the custom CSS
load_custom_css()



def get_customer_information(Customer_ID):
    """Get the customer information using the customer_ID argument"""
    URL = "http://127.0.0.1:8000/customer/{}".format(Customer_ID)
    r = requests.get(url = URL)
    data = r.json()
    print(URL)
    return json.dumps(data[0])
openai_api_key = OPENAI_API_KEY
# with st.sidebar:
#     openai_api_key = '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'
#     "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
#     "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
#     "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"
delimiter = "####"
system_message = f"""Instruction: Create a customized and CONSIZED pointers for each pointer for selling story and do not create any facts.
Context: You are an assistant to Tele Sales agent for a AbInbev, a Beer company. Write a data backed reasons for selling more beer for my next customer whose details are as follows:
The details around the customer should be pulled using Customer ID.
If the user dosent provide the Customer ID then ask him to provide the Customer ID.
The customer service query will be delimited with \ 
{delimiter} characters """
    
# user_message = f"""Can you tell me about customer with customer_ID 0010Y00001aLGsYQAW"""

functions = [
        {
            "name": "get_customer_information",
            "description": "Get the customer information using the customer_ID argument",
            "parameters": {
                "type": "object",
                "properties": {
                    "Customer_ID": {
                        "type": "string",
                        "description": "The customer Identifier, which is unique for each customer",
                    },
                    "Customer_Name": {
                        "type": "string",
                        "description": " This is the Customer Name",
                    },
                },
                "required": ["Customer_ID"],
            },
        }
    ]
st.title("💬 GenScribe: BDR Assistant")
if "messages" not in st.session_state:

    st.session_state["messages"] = [{"role": "assistant", "content": "Hey I am your Assistant !! Ready to help you with Selling Stories!!"}, {'role':'system','content': system_message}]

for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.chat_message(msg["role"]).write(msg["content"])
    # st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    openai.api_key = openai_api_key
    st.session_state.messages.append({"role": "user", "content":f"{delimiter}{prompt}{delimiter}" })
    st.chat_message("user").write(prompt)
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", functions=functions,function_call="auto",messages=st.session_state.messages)
    response_message = response.choices[0].message
    # st.session_state.messages.append(response_message)
    # st.chat_message("assistant").write(response_message.content)

    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_customer_information": get_customer_information,
        }  # only one function in this example, but you can have multiple
        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        print("function_args : ", function_args)
        function_response = fuction_to_call(
            Customer_ID=function_args.get("Customer_ID"),
        )
        print(function_response)

        # Step 4: send the info on the function call and function response to GPT
        st.session_state.messages.append(response_message)  # extend conversation with assistant's reply
        st.session_state.messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=st.session_state.messages,
        )  # get a new response from GPT where it can see the function response
        # return second_response
        print(second_response.choices[0].message)
        st.chat_message("assistant").write(second_response.choices[0].message.content)