# ComfyUI-Imagen-Gemini
<img width="1057" height="584" alt="gemini-imagen" src="https://github.com/user-attachments/assets/881fcf7f-a631-4f6a-aab4-a0582bf2d75d" />

A custom node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that integrates Google's latest **Imagen 4** and **Imagen 3** generative models via the Gemini API. 

Generate high-quality images directly within your ComfyUI workflows using Google's state-of-the-art diffusion models.
**Note that: The "allow_all" parameter value is not allowed in EU, UK, CH, MENA locations.**

## ✨ Features

* **Model Support:** Access to the latest models including:
    * **Imagen 4:** Ultra, Standard, and Fast variants.
    * **Imagen 3:** Standard and Fast variants.
* **Resolution Control:** Select between `1K` and `2K` native generation.
* **Aspect Ratios:** Native support for `1:1`, `3:4`, `4:3`, `9:16`, and `16:9`.
* **Safety Settings:** Configurable person generation filters (`allow_adult`, `allow_all`, `dont_allow`).
* **Guidance Output:** Includes a secondary text output containing official prompting guidance for Imagen 4.
* **Secure Auth:** Supports API keys via node widget or environment variables (`GEMINI_API_KEY`).

## 🛠️ Installation

### Option 1: Git Clone (Manual)
1.  Navigate to your ComfyUI `custom_nodes` directory.
2.  Clone this repository:
    ```bash
    git clone [https://github.com/yourusername/ComfyUI-Imagen-Gemini.git](https://github.com/yourusername/ComfyUI-Imagen-Gemini.git)
    ```
3.  Install dependencies (if necessary):
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: This node primarily uses standard libraries like `requests`, `torch`, and `Pillow` which are likely already installed in your ComfyUI environment.)*

4.  Restart ComfyUI.

## 🔑 API Key Configuration

You need a Google Gemini API key to use this node. You can get one here: [Google AI Studio](https://aistudio.google.com/).

You can provide the key in two ways:

1.  **Environment Variable (Recommended):**
    Set a `GEMINI_API_KEY` environment variable on your system. The node will automatically detect this, allowing you to leave the API key field in the UI blank.
    
2.  **Node Widget:**
    Paste your API key directly into the `gemini_api_key` field on the node.

## 🎛️ Usage

1.  **Add Node:** Right-click > `ImagenGemini` > `Imagen Gemini`.
2.  **Connect Prompt:** Connect a string primitive or write your prompt in the widget.
3.  **Outputs:**
    * **IMAGE:** The generated image tensor (connect to `PreviewImage` or `SaveImage`).
    * **GUIDANCE:** A string output containing prompting tips specific to Imagen models (connect to `ShowText` or similar).

### Parameters

| Parameter | Description |
| :--- | :--- |
| **prompt** | The positive text description for image generation. |
| **model** | Select the model version (e.g., `imagen-4.0-generate-001`, `imagen-3.0-fast-generate-001`). |
| **gemini_api_key** | Your Google API Key. Leave empty if using env var. |
| **aspect_ratio** | The shape of the image (`1:1`, `16:9`, etc.). |
| **resolution** | `1K` or `2K` generation. |
| **num_images** | Batch size (1 to 4 images per request). |
| **person_generation** | Controls generation of people: `allow_adult` (default), `allow_all`, or `dont_allow`. |

## 📋 Requirements

* ComfyUI
* Python 3.x
* `requests`
* `torch`
* `Pillow`
* `numpy`

## ⚠️ Notes

* **Negative Prompts:** Google's Imagen API implementation for these models does not currently support negative prompts or system instructions; therefore, the node only accepts a positive prompt.
* **API Limits:** Usage is subject to Google Gemini API quotas and pricing. Please check your Google AI Studio dashboard for details.

## License

[MIT](LICENSE)
