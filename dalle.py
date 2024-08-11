import json
import time
import requests
import os

STABLE_DIFFUSION_API_KEY = os.getenv("STABLE_DIFFUSION_API_KEY")

stable_key = STABLE_DIFFUSION_API_KEY

def post_image_request_stable_diffusion(image_url:str, prompt: str):
    url = "https://stablediffusionapi.com/api/v3/img2img"
    payload = json.dumps({
        "key": stable_key,
        "prompt": prompt,
        "negative_prompt": "((roof of a booth)),((lights above))",
        "init_image": image_url,
        "width": "512",
        "height": "512",
        "samples": "1",
        "num_inference_steps": "50",
        "safety_checker": "no",
        "enhance_prompt": "yes",
        "guidance_scale": 12,
        "strength": 0.2,
        "seed": None,
        "base64": "no",
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


image_url = "https://backend.exafy.io/media/tmpimages/Picture2.jpg"

result = post_image_request_stable_diffusion(
    image_url=image_url,
    prompt="""Photo of yellow bananas"""
)

print(result)


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

img = get_stable_image(result)
print(img)