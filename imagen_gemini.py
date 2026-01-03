import os
import torch
import requests
import base64
import numpy as np
import json
from io import BytesIO
from PIL import Image

# --- Helper Functions ---

def pil2tensor(pil_image):
    """Convert PIL Image (RGB) back to ComfyUI tensor (B=1, H, W, C)"""
    if pil_image is None:
        return None
    arr = np.array(pil_image).astype(np.float32) / 255.0
    arr = arr[np.newaxis, ...]
    return torch.from_numpy(arr)

class ImagenGemini:
    """
    ComfyUI Node for Google Imagen 4 & 3 (Ultra, Standard, Fast).
    Supports specific resolution (1K/2K) and aspect ratios.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "A futuristic city with flying cars, cinematic lighting", "multiline": True}),
                "model": ([
                    # Imagen 4 (Preview/Latest)
                    "imagen-4.0-ultra-generate-001",
                    "imagen-4.0-generate-001",
                    "imagen-4.0-fast-generate-001",
                    # Imagen 3 (Stable/Current)
                    "imagen-3.0-generate-002",
                    "imagen-3.0-fast-generate-001",
                    "imagen-3.0-generate-001",
                ], {"default": "imagen-4.0-generate-001"}),
                "gemini_api_key": ("STRING", {"default": "", "multiline": False}),
                "aspect_ratio": ([
                    "1:1", "3:4", "4:3", "9:16", "16:9"
                ], {"default": "1:1"}),
                "resolution": (["1K", "2K"], {"default": "1K"}),
                "num_images": ("INT", {"default": 1, "min": 1, "max": 4, "step": 1}),
                "person_generation": (["allow_adult", "dont_allow", "allow_all"], {"default": "allow_adult"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "guidance")
    FUNCTION = "process"
    CATEGORY = "ImagenGemini"
    OUTPUT_NODE = True

    def process(self, prompt, model, gemini_api_key, person_generation="allow_adult", aspect_ratio="1:1", resolution="1K", num_images=1):
        
        # 1. Credential Check
        if not gemini_api_key or gemini_api_key.strip() == "":
            gemini_api_key = os.environ.get("GEMINI_API_KEY")

        if not gemini_api_key or gemini_api_key.strip() == "":
            raise ValueError("Please provide a valid Google Gemini API Key via the UI or the GEMINI_API_KEY environment variable.")

        # 2. Configure API Payload
        parameters = {
            "sampleCount": num_images,
            "aspectRatio": aspect_ratio,
            "sampleImageSize": resolution,
            "personGeneration": person_generation
        }

        payload = {
            "instances": [
                { "prompt": prompt }
            ],
            "parameters": parameters
        }

        # 3. Request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict?key={gemini_api_key}"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            print(f"Imagen API Request Failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                 raise ValueError(f"API Error: {e.response.text}")
            raise ValueError(f"API Request failed: {str(e)}")

        # 4. Parse Response
        predictions = result.get("predictions", [])
        
        if not predictions:
            raise ValueError(f"No images returned. API Response: {json.dumps(result, indent=2)}")

        output_tensors = []
        
        for pred in predictions:
            b64_data = pred.get("bytesBase64Encoded")
            if b64_data:
                try:
                    img_data = base64.b64decode(b64_data)
                    pil_img = Image.open(BytesIO(img_data)).convert("RGB")
                    tensor_out = pil2tensor(pil_img)
                    output_tensors.append(tensor_out)
                except Exception as e:
                    print(f"Error decoding image: {e}")

        if not output_tensors:
             raise ValueError("Failed to decode any images from the response.")

        # 5. Stack Batch
        result_batch = torch.cat(output_tensors, dim=0)

        # 6. Guidance Output
        guidance_text = """# Imagen 4 Prompting Guidance

## Imagen 4 Prompt Writing Basics

A good prompt is descriptive, clear, and uses meaningful keywords. Limit prompts to **480 tokens**.

* **Subject**: Define the core object, person, animal, or scenery.
* **Context and background**: Place the subject in a specific environment (e.g., "a studio with a white background," "outdoors").
* **Style**: Specify the artistic style (e.g., "oil painting," "sketch," "isometric 3D," "photorealistic").

**Iterative prompting** is key: start with a core idea and refine by adding details until the image matches your vision.

## Key Prompt Elements
* **Use descriptive language**: Employ detailed adjectives and adverbs.
* **Provide context**: Include background info to aid understanding.
* **Reference specific artists or styles**: Mention specific aesthetics or movements (e.g., "Impressionism").
* **Enhancing facial details**: Explicitly focus on faces (e.g., use "portrait").

## Generating Text in Images
Imagen 4 can render text within images.
* **Iterate with confidence**: You may need multiple attempts for the best text integration.
* **Keep it short**: Limit text strings to **25 characters or less** for optimal results.
* **Multiple phrases**: Use 2–3 distinct phrases max; do not exceed this for cleaner compositions.
* **Guide Placement**: The model attempts to follow positioning directions, though variations occur.
* **Inspire font style**: Specify general styles (e.g., "bold font," "handwritten") rather than exact typefaces.
* **Font size**: Use general size indicators like "small," "medium," or "large."

## Advanced Techniques: Photography Modifiers

To generate photorealistic images, start your prompt with **"A photo of..."** and use specific terminology from the categories below to control the look and feel.

### 1. Shot Types & Framing
Control how much of the subject is visible.
* **Extreme Close-Up**: Focuses on a specific detail (e.g., "an eye," "texture of a leaf").
* **Close-Up**: Frames the head and shoulders; captures facial expressions.
* **Medium Shot**: Waist-up; good for interactions or dialogue scenes.
* **Cowboy Shot (American Shot)**: Framed from mid-thigh up; classic for confident stances.
* **Full Shot**: Captures the subject's entire body from head to toe.
* **Wide Shot / Long Shot**: Shows the subject within their environment.
* **Establishing Shot**: Very wide view designed to show the setting or location.

### 2. Camera Angles
Control the viewer's perspective relative to the subject.
* **Eye-Level**: Neutral, natural perspective; connects directly with the subject.
* **Low Angle**: Camera looks up at the subject; makes them look powerful, dominant, or large.
* **High Angle**: Camera looks down; makes the subject look vulnerable or small.
* **Bird’s-Eye View / Overhead**: Directly from above (90 degrees); creates a geometric or map-like layout.
* **Worm’s-Eye View**: From the ground looking straight up; emphasizes height and scale.
* **Dutch Angle / Canted Angle**: Tilted camera horizon; creates tension, disorientation, or dynamism.
* **Over-the-Shoulder**: View from behind a subject, looking at what they are seeing or facing.

### 3. Lighting Styles & Atmosphere
Lighting defines the mood and depth of the image.
* **Golden Hour**: Warm, soft, orange glow just after sunrise or before sunset.
* **Blue Hour**: Cool, deep blue tones just before sunrise or after sunset.
* **Rembrandt Lighting**: Dramatic portrait lighting characterized by a triangular highlight on the shadowed cheek.
* **Butterfly Lighting**: Glamour lighting with a butterfly-shaped shadow under the nose; high placement.
* **Rim Lighting / Backlighting**: Light source behind the subject; creates a glowing outline or silhouette.
* **Chiaroscuro**: Strong contrast between light and dark; moody and dramatic.
* **High-Key**: Bright, evenly lit, minimal shadows; optimistic and clean.
* **Low-Key**: Dark, predominant shadows, selective lighting; mysterious and intense.
* **Volumetric Lighting / God Rays**: Visible beams of light cutting through atmosphere (fog, dust, smoke).

### 4. Photographic Styles & Genres
Define the "intent" of the photograph.
* **Candid Shot**: Unposed, natural, capturing a genuine moment unaware of the camera.
* **Street Photography**: Gritty, urban, capturing everyday life and society.
* **Editorial / Fashion**: Stylish, high-end, posed, focused on clothing or beauty (often "studio lighting").
* **Macro Photography**: Extreme magnification of small subjects (insects, droplets).
* **Tilt-Shift**: Miniature effect; blurs top and bottom to make real scenes look like toys.
* **Double Exposure**: Superimposing two images (e.g., "silhouette of a person combined with a forest").
* **Long Exposure**: Blurs moving elements (e.g., "silky water," "light trails" from cars).

### 5. Camera Settings & Optics
Simulate specific lens and camera behaviors.
* **Bokeh / Shallow Depth of Field**: Sharp subject, blurry background; isolates the subject.
* **Deep Depth of Field**: Everything in focus from foreground to background (common in landscapes).
* **Motion Blur**: Background or subject streaking to convey speed.
* **Fisheye Lens**: Ultra-wide, distorted spherical view (180 degrees).
* **Telephoto Lens**: Compresses distance; makes background elements look closer and larger.
* **Wide Angle**: Expands the view; exaggerates perspective (objects near lens look huge).

### 6. Film Stocks & Vintage Aesthetics
Mimic specific analog looks.
* **Kodachrome**: Vivid, rich colors, high contrast (classic mid-century look).
* **Polaroid / Instant Film**: Soft focus, specific color casts, white borders.
* **Sepia**: Brownish tone; implies history or "Old West."
* **Monochrome / Black and White**: Focuses on texture and contrast; timeless.
* **Cyanotype**: Blueprint-like, deep monochromatic blue.
* **Daguerreotype**: Metallic, antique, high-detail, eerie vintage portraiture.

## Art & Material Modifiers
* **Shapes and materials**: Define unique compositions (e.g., "an armchair made of paper," "neon tubes in the shape of a bird").
* **Historical art references**: Use **"in the style of [Movement]"** (e.g., "Renaissance," "Pop Art," "Surrealism").
* **Image quality modifiers**: Use keywords like **"high-quality," "4K," "HDR," "studio photo,"** or **"by a professional"** to boost aesthetic quality.

## Prompt Parameterization
For dynamic applications, use placeholders in your prompt structure (e.g., `A {logo_style} logo for a {company_name}`)."""

        return (result_batch, guidance_text)