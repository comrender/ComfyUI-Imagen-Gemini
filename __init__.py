from .imagen_gemini import ImagenGemini

NODE_CLASS_MAPPINGS = {
    "ImagenGemini": ImagenGemini
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImagenGemini": "Imagen Gemini"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']