import gradio as gr
import numpy as np

from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

def to_image(input_array):
    return Image.fromarray(input_array.astype(np.uint8))

def setup_ui():
    with gr.Accordion("Dynamic HDR", open=False):

        with gr.Row() as Fx:
            enable = gr.Checkbox(label="Enable")
            iterations = gr.Slider(label="Steps", minimum=1, maximum=32, step=1, value=6)

        with gr.Row() as BnC:
            offset = gr.Slider(label="Brightness", minimum=-64, maximum=64, step=1, value=4)
            bound = gr.Slider(label="Contrast", minimum=0, maximum=32, step=1, value=2)
            saturation = gr.Slider(label="Saturation", minimum=0.0, maximum=2.0, step=0.1, value=1.2)

        with gr.Accordion("Advanced Settings", open=False):
            debug = gr.Checkbox(label="Debug")

            with gr.Row() as Adv:
                sigma = gr.Slider(label="Sigma",minimum=0,maximum=4,step=0.01,value=1.0)
                strength = gr.Slider(label="Blur",minimum=1,maximum=64,step=1,value=16)

    return [enable, iterations, offset, bound, saturation, debug, sigma, strength]

def calculate_luma(input_array, strength):
    luma_array = np.dot(input_array, [0.2126, 0.7152, 0.0722])
    return gaussian_filter(luma_array, sigma=strength)

def lerp_array(input_array, new_min, new_max):
    old_min = np.min(input_array)
    old_max = np.max(input_array)

    return np.interp(input_array, (old_min, old_max), (new_min, new_max))

def generate_noise(luma_map, sigma):
    r = np.random.normal(loc=luma_map, scale=sigma)
    g = np.random.normal(loc=luma_map, scale=sigma)
    b = np.random.normal(loc=luma_map, scale=sigma)

    return np.stack((r, g, b), axis=2)

def modify_saturation(input_image, saturation_factor):
    hsv_image = input_image.convert("HSV")
    h, s, v = hsv_image.split()
    
    s_array = np.array(s)
    s_array = np.clip(s_array * saturation_factor, 0, 255)
    modified_s = to_image(s_array)
    
    modified_hsv_image = Image.merge("HSV", (h, modified_s, v))
    return modified_hsv_image.convert("RGB")

def generate_debug_grid(og_image, luma_image, noise_image):
    caption1 = "Original Image"
    caption2 = "Luma Map"
    caption3 = "Input Image"

    caption_bar = 64

    image_width, image_height = og_image.size

    grid_width = 3 * image_width
    grid_height = image_height + caption_bar

    grid_image = Image.new("RGB", (grid_width, grid_height), (255, 255, 255))

    grid_image.paste(og_image, (0, caption_bar))
    grid_image.paste(luma_image, (image_width, caption_bar))
    grid_image.paste(noise_image, (image_width * 2, caption_bar))

    draw = ImageDraw.Draw(grid_image)
    font = ImageFont.truetype("arial.ttf", 48)

    draw.text((image_width * 0.25, 8), caption1, font=font, fill=(0, 0, 0))
    draw.text((image_width * 1.25, 8), caption2, font=font, fill=(0, 0, 0))
    draw.text((image_width * 2.25, 8), caption3, font=font, fill=(0, 0, 0))

    return grid_image