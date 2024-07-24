import os
import time
import requests

import streamlit as st
# from dotenv import load_dotenv

# load_dotenv()
# MIDJOURNEY_API_KEY = os.getenv("MID_JOURNEY_AUTH_TOKEN")

MIDJOURNEY_API_KEY = st.secrets["MID_JOURNEY_AUTH_TOKEN"]

st.title("Welcome to Midjourney!")
input_text = st.text_area("Please enter your message")

def post_image_request(prompt: str):
        
    # Configuration for the POST request
    url = "https://api.imaginepro.ai/api/v1/midjourney/imagine"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MIDJOURNEY_API_KEY}"
    }
    data = {
        "prompt": f"""{prompt}""" 
    }
    # Making the POST request
    response = requests.post(url, json=data, headers=headers)
    message_id = None
    # Handling the response
    if response.status_code == 200:
        print(response.json())
        message_id = response.json()['messageId']
    else:
        print("Failed to fetch data:", response.status_code)
    return message_id

def get_processing_button(message_id: str):
    url = "https://api.imaginepro.ai/api/v1/midjourney/button"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MIDJOURNEY_API_KEY}"
    }
    data = {
        "messageId": message_id,
        "button": "U1"
    }

    # Making the POST request
    response = requests.post(url, json=data, headers=headers)

    # Handling the response
    if response.status_code == 200:
        print(response.json())
    else:
        print("Failed to fetch data:", response.status_code)
        print(response.text)


def get_image(message_id: str):
    headers= {
        "Authorization": f"Bearer {MIDJOURNEY_API_KEY}",
    }
    url =f"https://api.imaginepro.ai/api/v1/midjourney/message/{message_id}"
    status = None
    is_processing = True
    while status != "DONE":
        time.sleep(5)
        get_task_bar = requests.get(url, headers=headers)

        if get_task_bar.status_code == 200:
            print(get_task_bar.json())
            status = get_task_bar.json()['status']
            if status == "PROCESSING":
                print("Processing...")
                if is_processing:
                    get_processing_button(message_id)
                    is_processing = False

            elif status == "FAIL":
                print("Failed to fetch data")
                return None
            elif status == "DONE":
                print("Done")
                return get_task_bar.json()['uri']
    
             


if st.button("Submit"):
    if input_text:
        with st.spinner("Processing..."):
            message_id = post_image_request(input_text)
            if message_id:
                image_url = get_image(message_id)
                if image_url:
                    st.image(image_url)
    else:
        st.write("Please enter some text to proceed.")