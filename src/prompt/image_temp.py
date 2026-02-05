IMAGE_ENHANCEMENT_TEMPLATE = """high quality, detailed, professional, {prompt}, 4k resolution, photorealistic"""

STYLE_TEMPLATES = {
    "photorealistic": "{prompt}, photorealistic, high detail, professional photography",
    "artistic": "{prompt}, artistic interpretation, creative, unique style",
    "minimalist": "{prompt}, minimalist design, clean, simple, elegant",
    "vibrant": "{prompt}, vibrant colors, bold, eye-catching, energetic"
}

def enhance_image_prompt(prompt: str, style: str = None) -> str:
    if style and style in STYLE_TEMPLATES:
        return STYLE_TEMPLATES[style].format(prompt=prompt)
    return IMAGE_ENHANCEMENT_TEMPLATE.format(prompt=prompt)
