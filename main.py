import os
import random
import subprocess
import time
import requests
import streamlit as st
import json

from leonardo_api import Leonardo

LEONARD_API_KEY = os.getenv("LEONARD_API_KEY")
leonardo = Leonardo(auth_token=LEONARD_API_KEY)

MIDJOURNEY_API_KEY = os.getenv("MID_JOURNEY_AUTH_TOKEN")
LEONARD_API_KEY = os.getenv("LEONARD_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STABLE_DIFFUSION_API_KEY = os.getenv("STABLE_DIFFUSION_API_KEY")


openai_key = OPENAI_API_KEY
stable_key = STABLE_DIFFUSION_API_KEY   

st.title("Welcome to PIXLIP AI!")

dalle_text = st.text_area("Please enter Dall e prompt")
stable_text = st.text_area("Please enter Stable Diffusion prompt")
leonardo_text = st.text_area("Please enter Leonardo prompt")
mid_journey_text = st.text_area("Please enter MidJourney prompt")



def post_image_request_leo(prompt: str):
    response = leonardo.post_generations(prompt=prompt, num_images=1,
                                           model_id='e316348f-7773-490e-adcd-46757c738eb7', width=1024, height=768,
                                           guidance_scale=7)
    generation_id = response['sdGenerationJob']['generationId']
    response = leonardo.get_single_generation(generation_id)
    response = leonardo.wait_for_image_generation(generation_id=generation_id)
    return response['url']

def post_image_request_midjourney(prompt: str):
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
# The below function is not used as the key is not valid
def post_image_request_stable_diffusion(prompt: str):
    url = "https://stablediffusionapi.com/api/v3/text2img"
    payload = json.dumps({
        "key": stable_key,
        "prompt": prompt,
        "negative_prompt": None,
        "width": "512",
        "height": "512",
        "samples": "1",
        "num_inference_steps": "20",
        "seed": None,
        "guidance_scale": 7.5,
        "safety_checker": "yes",
        "multi_lingual": "no",
        "panorama": "no",
        "self_attention": "no",
        "upscale": "no",
        "embeddings_model": None,
        "webhook": None,
        "track_id": None
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response = json.loads(response.text)
    image_id = response['id']
    return image_id

def post_image_request_dalle(prompt: str):
    data = json.dumps({
    "model": "dall-e-3",
    "prompt": prompt,
    "n": 1,
    "size": "1024x1024",
    "quality": "hd",
    "response_format": "url"
    })
    curl_command = [
    "curl", "-X", "POST", "https://api.openai.com/v1/images/generations",
    "-H", "Content-Type: application/json",
    "-H", f"Authorization: Bearer {openai_key}",
    "-d", data
    ]
    response = subprocess.run(curl_command, capture_output=True, text=True, check=True)
    image_url = json.loads(response.stdout)['data'][0]['url']
    return image_url




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

def get_stable_image(image_id:str):
    fetch_url = f"https://stablediffusionapi.com/api/v3/fetch/{image_id}"
    headers = {
        'Content-Type': 'application/json',
    }
    fetch_data = {
        "key": stable_key
    }
    fetch_response = requests.post(url=fetch_url,headers=headers,data=json.dumps(fetch_data))
    data_dict = json.loads(fetch_response.text)
    while data_dict['status'] != "success" and data_dict['status'] != "failed":
        time.sleep(2)
        fetch_response = requests.post(url=fetch_url,headers=headers,data=json.dumps(fetch_data))
        data_dict = json.loads(fetch_response.text)
    return data_dict['output'][0]
def get_random_image():
    random_number = random.randint(2, 5)
    url = f"https://backend.exafy.io/media/tmpimages/Picture{random_number}.jpg"
    return url


if st.button("Submit"):
    idea=1
    random_image = get_random_image()
    with st.spinner("Processing..."):
        if dalle_text:
            for i in range(0,4):
                dalle_image_url = post_image_request_dalle(dalle_text)
                if dalle_image_url:
                    st.title(f"Idea {idea}")
                    st.image(dalle_image_url)
                    idea+=1
        if stable_text:
            for i in range(0,4):
                stable_image_id = post_image_request_stable_diffusion(stable_text)
                if stable_image_id:
                    stable_image = get_stable_image(stable_image_id)
                    if stable_image:
                        st.title(f"Idea {idea}")
                        st.image(stable_image)
                        idea+=1
        if leonardo_text:
            for i in range(0,4):
                leo_image_url = post_image_request_leo(leonardo_text)
                if leo_image_url:
                        st.title(f"Idea {idea}")
                        st.image(leo_image_url)
                        idea+=1
        if mid_journey_text:

            message_id = post_image_request_midjourney(f"{random_image} {mid_journey_text}")
            if message_id:
                image_url = get_image(message_id)
                if image_url:
                    st.title("Idea 12 to 16")
                    st.image(image_url)
    









