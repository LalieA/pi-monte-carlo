#!/usr/bin/env python3

"""

Module offering methods of converting static images to animated images like GIFs

"""

import sys
from PIL import Image

def generate_gif_file(images, gif_label):
    """
    Creates an animated GIF image names gif_label from the images in parameters
    Equivalent of: convert -delay 100 -loop 0 <images> <gif_label>.gif
    """
    frames = []
    for img in images:
        frames.append(Image.open(img))
    frames[0].save(
        gif_label,
        format='GIF',
        append_images=frames[1:],
        optimize=False,
        save_all=True,
        duration=1000,
        loop=0
    )

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
        raise Exception(
            f"Utilisation : {sys.argv[0]} <image_1 [image_2 image_3 ...]> <nom_du_fichier>"
        )

    generate_gif_file(sys.argv[1:-1], sys.argv[-1])
