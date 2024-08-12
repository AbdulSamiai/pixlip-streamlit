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

input_text = st.text_area("Enter a prompt here...")



def post_image_request_leo(prompt: str):
    response = leonardo.post_generations(prompt=prompt, num_images=1,
                                           model_id='b24e16ff-06e3-43eb-8d33-4416c2d75876', width=1024, height=768,
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
        if input_text:
            for i in range(0,4):
                dalle_image_url = post_image_request_dalle(f"""Make a photo of an exhibition island booth with 1 meter standard width modular walls and no luminous bodies or lights on top of the walls. 
1. All Walls Illuminated Modular Lightboxes: feature every single wall as modular LED lightboxes, These lightboxes should be the central focus, creating a bright and attention-grabbing display. walls are lightboxes, The booth should have a clean, modular design that appears effortlessly assembled, with seamless connections between panels. No luminous body above
2. Minimalistic and Modern Aesthetics: minimalistic design. Incorporate large, vibrant graphics displayed on the shining walls. The booth should look modern with smooth surfaces and minimal clutter. No lights or luminous bodies on the walls and no ceiling on top of the stand 
3. Modular Components : Include features like counters, shelves, or brochure holders that seamlessly attach to the lightbox frames. No light bulbs above 
4. No luminous bodies above the stand: Ensure no light bulbs and no ceiling, no lights on top of the walls. only even glowing walls are lightboxes to make the graphics pop 
The glowing walls display this:{input_text}""")
                if dalle_image_url:
                    st.title(f"Idea {idea}")
                    st.image(dalle_image_url)
                    idea+=1
        if input_text:
            for i in range(0,4):
                stable_image_id = post_image_request_stable_diffusion(f"""Show trade show booth in busy Exhibition Hall built with glowing LED 1 meter width wall panels.
The glowing wall panels display full size images of:{input_text}""")
                if stable_image_id:
                    stable_image = get_stable_image(stable_image_id)
                    if stable_image:
                        st.title(f"Idea {idea}")
                        st.image(stable_image)
                        idea+=1
        if input_text:
            for i in range(0,4):
                leo_image_url = post_image_request_leo(f"""Show trade show booth in busy Exhibition Hall built with glowing LED 1 meter width wall panels. Modular glowing booth walls with integration LED backlighting makes the wall graphics appear to glow, walls with sharp edges. No other light above. The glowing wall panels display full size images of:{input_text}""")
                if leo_image_url:
                        st.title(f"Idea {idea}")
                        st.image(leo_image_url)
                        idea+=1
        if input_text:
            message_id = post_image_request_midjourney(f"{random_image} Modular glowing booth walls with integration LED backlighting makes the wall graphics appear to glow, walls with sharp edges. No other light above. Create a PIXLIP booth for:{input_text}")
            if message_id:
                image_url = get_image(message_id)
                if image_url:
                    st.title("Idea 12 to 16")
                    st.image(image_url)
    









