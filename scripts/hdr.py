import modules.scripts as scripts
import numpy as np

from helper_funcs import *

class DynamicHDR(scripts.Script):
    def __init__(self):
        self.grid = None

    def title(self):
        return "Dynamic HDR"

    def show(self, is_img2img):
        if not is_img2img:
            return None

        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        if not is_img2img:
            return None

        return setup_ui()

    def process(self, p, enable:bool, iterations:int, offset:int, bound:int, saturation:float, debug:bool, sigma:float, strength:int):
        self.grid = None
        if not enable:
            return p

        input_image = p.init_images[0]
        input_array = np.array(input_image)

        luma_array = calculate_luma(input_array, strength)

        luma_map_array = lerp_array(luma_array, -bound + offset, bound + offset)

        output_array = np.array(modify_saturation(input_image, saturation))

        for i in range(iterations):
            noise_array = generate_noise(luma_map_array, sigma)
            output_array = output_array + noise_array

        p.init_images[0] = to_image(np.clip(output_array, 0, 255))

        if debug == True:
            self.grid = generate_debug_grid(
                    input_image,
                    to_image(luma_array),
                    p.init_images[0]
            )

        return p

    def postprocess(self, p, processed, *args):
        if not self.grid == None:
            processed.images.append(self.grid)