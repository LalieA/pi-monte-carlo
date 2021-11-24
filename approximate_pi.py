#!/usr/bin/env python3

"""

Module offering methods to create visual representations
of a Monte Carlo simulation that approaches PI value

"""

import sys
import subprocess
from re import match
from os import listdir, remove
from simulator import is_in_circle, simulate


NUMBER_OF_IMAGES = 10
IN_COLOR = bytes.fromhex("eb8310")
OUT_COLOR = bytes.fromhex("d33488")
BLANK_COLOR = bytes.fromhex("ffffff")
PRINT_COLOR = bytes.fromhex("000000")


def delete_old_files():
    """
    Deletes all .ppm and .gif files from the current directory
    """
    for file in listdir():
        if match("^.*.ppm$", file) or match("^.*.gif$", file):
            remove(file)

def change_pixel(content, point, color, line_len):
    """
    Assuming that content is a bytearray representing the content of a ppm image,
    it changes the value of the pixel at index 'point' (tuple of shape (x, y)) by 'color'.
    The number of bytes in 'content' that makes a whole line in the PPM image at the end
    is stored on 'line_len'.

    """
    line_index = point[1] * line_len
    col_index = point[0] * 3
    index = line_index + col_index

    content[index:index+3] = color


def print_char(content, car, anchor, seg_size, measures):
    """
    Replaces the good values in 'content' to represent a 7 segments character 'car'
    of width seg_size[0] and height seg_size[1] starting from an anchor point 'anchor' tuple
    at bottom left with a thickness of measures[1].
    The number of bytes in 'content' that makes a whole line in the PPM image at the end
    is stored on measures[0].

    Segments are named this way :
                A
           -----------
           |         |
        F  |    G    | B
           -----------
        E  |         | C
           |    D    |
           O----------
           ^
           |
        Anchor
    """
    line_len, thickness = measures
    seg_width, seg_height = seg_size

    horiz_seg = [(x, anchor[1]) for x in range(anchor[0], anchor[0] + seg_width + 1)]
    verti_seg = [(anchor[0], y) for y in range(anchor[1], anchor[1] - seg_height, -1)]

    if car == '.':
        for i in range(thickness * 2):
            for j in range(thickness * 2):
                change_pixel(content, (anchor[0] + i, anchor[1] - j), PRINT_COLOR, line_len)
        return

    if car not in ['1', '4']:
        # A
        for i in range(thickness):
            for point in ((x, y - 2 * seg_height + i) for (x, y) in horiz_seg):
                change_pixel(content, point, PRINT_COLOR, line_len)
    if car not in ['5', '6']:
        # B
        for i in range(thickness):
            for point in ((x + seg_width - i, y - seg_height) for (x, y) in verti_seg):
                change_pixel(content, point, PRINT_COLOR, line_len)
    if car != '2':
        # C
        for i in range(thickness):
            for point in ((x + seg_width - i, y) for (x, y) in verti_seg):
                change_pixel(content, point, PRINT_COLOR, line_len)
    if car not in ['1', '4', '7']:
        # D
        for i in range(thickness):
            for point in ((x, y - i) for (x, y) in horiz_seg):
                change_pixel(content, point, PRINT_COLOR, line_len)
    if car in ['0', '2', '6', '8']:
        # E
        for i in range(thickness):
            for point in ((x + i, y) for (x, y) in verti_seg):
                change_pixel(content, point, PRINT_COLOR, line_len)
    if car not in ['1', '2', '3', '7']:
        # F
        for i in range(thickness):
            for point in ((x + i, y - seg_height) for (x, y) in verti_seg):
                change_pixel(content, point, PRINT_COLOR, line_len)
    if car not in ['0', '1', '7']:
        # G
        for i in range(- int(thickness/2), int(thickness/2) + 1):
            for point in ((x, y - seg_height + i) for (x, y) in horiz_seg):
                change_pixel(content, point, PRINT_COLOR, line_len)

def print_pi(content, pi_value, precision, width, height=None):
    """
    Replaces the good values in 'content' to represent pi_value on multiple 7 segments characters.
    'width' and 'height' are respectively the width and height of the PPM image we want to generate
    """
    if height is None:
        height = width

    hauteur_ecriture = int(height / 12)
    largeur_ecriture = int(width / 6)

    seg_height = int(hauteur_ecriture / 2)
    seg_width = int((largeur_ecriture - 3 * (precision + 1)) / (precision + 2))

    thickness = 1 + int(min(hauteur_ecriture, largeur_ecriture) / 30)

    x_anchor = int(width / 2 - largeur_ecriture / 2)
    y_anchor = int(height / 2 + seg_height)

    line_len = width * 3
    for car in str(pi_value)[:precision + 2]:
        print_char(content,
                   car,
                   (x_anchor, y_anchor),
                   (seg_width, seg_height),
                   (line_len, thickness))
        x_anchor += seg_width + 3

def generate_ppm_file(width, n_points, precision):
    """
    Generates NUMBER_OF_IMAGES PPM images representing the n_points points of a Monte Carlo
    simulation with a precision of 'precision' numbers after the point, on the current directory
    """
    delete_old_files()

    radius = width / 2
    img = 0
    images = []

    # Build blank image
    content = bytearray((BLANK_COLOR * width) * width)

    for pi_value, pts in simulate(n_points, yields=NUMBER_OF_IMAGES):
        # Fill points from simulation with good color
        for point in [(int(x * radius + radius), int(y * radius + radius)) for x, y in pts]:
            change_pixel(
                content,
                point,
                IN_COLOR if is_in_circle(point[0], point[1], radius, radius, radius) else OUT_COLOR,
                3 * width
            )

        # Writing pi value
        printable_content = bytearray(content)
        print_pi(printable_content, pi_value, precision, width)

        # Image creation
        pi_int, pi_dec = str(pi_value).split('.')
        images.append(f"img{img}_{pi_int}-{pi_dec[:precision]}.ppm")
        with open(images[-1], 'wb') as file:
            file.write(bytes(f"P6 {width} {width} 255\n", 'UTF-8') + printable_content)
        img += 1

    # Gif creation

    # Calling the convert.py module (working on windows)
    #subprocess.run([sys.executable, "convert.py", *images, f"{images[-1][5:-4]}.gif"])

    # Calling the convert program (working on Debian-like distros, tested on Ubuntu)
    try:
        subprocess.check_call(" ".join(['convert',
                                        '-delay',
                                        '100',
                                        '-loop',
                                        '0',
                                        *images,
                                        f"{images[-1][5:-4]}.gif"]),
                              shell=True)
    except subprocess.CalledProcessError as err:
        print(err.cmd)
        print(err.output)

if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
        raise Exception(
            f"Utilisation : {sys.argv[0]} <taille_image> <nombre_de_points> <chiffres_après_virgule>"
        )

    if sys.argv[1].isdigit() and int(sys.argv[1]) <= 0 :
        raise ValueError("La taille de l'image doit être un entier supérieur à zéro.")
    if not sys.argv[1].isdigit():
        raise TypeError("La taille de l'image doit être un entier supérieur à zéro.")

    if sys.argv[2].isdigit() and int(sys.argv[2]) <= 0 :
        raise ValueError("Le nombre de points générés doit être un entier supérieur à zéro.")
    if not sys.argv[2].isdigit():
        raise TypeError("Le nombre de points générés doit être un entier supérieur à zéro.")

    if sys.argv[3].isdigit() and int(sys.argv[3]) <= 0:
        raise ValueError("Le nombre de chiffres après la virgule de pi doit être un entier supérieur à zéro.")
    if not sys.argv[3].isdigit():
        raise TypeError("Le nombre de chiffres après la virgule de pi doit être un entier supérieur à zéro.")

    generate_ppm_file(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))

    # 87 mégaoctets de mémoire RAM utilisés au maximum d'après memory_profiler
