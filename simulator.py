#!/usr/bin/env python3

"""

Module offering a method to aproach the value of PI

"""

import sys
from random import uniform

#Point = namedtuple('Point', 'x y')

def is_in_circle(p_x, p_y, c_x, c_y, radius):
    """
    Return True if the value of a point (p_x, p_y)
    is in the circle which has as center (c_x, c_y) and of radius 'radius',
    False otherwise
    """
    return (p_x - c_x)**2 + (p_y - c_y)**2 < radius**2

def simulate(n_points, yields=1):
    """
    Approaches the value of pi using a Monte Carlo simulation
    of 'n_points' points and return a Generator with 'yields' intermediate results
    """
    yield_cpt = 1
    cpt = 0
    pts = []
    for i in range(n_points):
        p_x = uniform(-1, 1)
        p_y = uniform(-1, 1)
        pts.append((p_x, p_y))
        if is_in_circle(p_x, p_y, 0, 0, 1):
            cpt += 1
        if not yield_cpt%(n_points//yields): # To yield
            yield (cpt*4)/i, pts
            pts = []
        yield_cpt += 1


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
        raise Exception(
            f"Utilisation:{sys.argv[0]} <taille_image> <nombre_de_points> <chiffres_après_virgule>"
        )
    if not sys.argv[1].isdigit():
        raise TypeError("Le nombre de points générés doit être un entier.")

    for pi, _ in simulate(int(sys.argv[1])): # One value
        print(pi)
