import json
import subprocess
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_key = OPENAI_API_KEY


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
    print(response.stdout)
    image_url = json.loads(response.stdout)['data'][0]['url']
    return image_url

result = post_image_request_dalle(
    """Show a photo of a trade show booth with 1 meter standard width modular walls and no luminous body above 

1. **All Walls Illuminated Modular Lightboxes**: feature every single wall as modular LED lightboxes, These lightboxes should be the central focus, creating a bright and attention-grabbing display for exhibitors products. walls are lightboxes, The booth should have a clean, modular design that appears effortlessly assembled, with seamless connections between panels. No luminous body above 

2. **Minimalistic and Modern Aesthetics**: minimalistic design. Incorporate large, vibrant graphics printed on fabric that can be easily swapped out. The booth should look modern with smooth surfaces and minimal clutter. no luminous body above 

3. **Modular Components **: Include features like counters, shelves, or brochure holders that seamlessly attach to the lightbox frames. no light bulbs above 

4. **No luminous body above**: Ensure no light bulbs from top down or from above. only even glowing walls, shadow-free backlighting to make the graphics pop, The lighting should highlight exhibitors products   glowing walls to present in the glowing walls:  

5. Only lights in the walls, no lights above. no measures of any kind, only glowing walls.




Photo of yellow mangoes""")
print(result)