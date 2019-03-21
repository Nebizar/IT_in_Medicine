# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 11:59:35 2019

@author: Mikołaj Frankowski
"""

def pixel_sum(img,list_of_lines):
    sum = 0
    line_sums = []
    all_sums = []

    for lines in list_of_lines:
        for line in lines:
            for point in line:
                x, y = point
                RGB = img.getpixel((x, y))
                sum = sum + RGB
            line_sums.append((sum / len(line)) / 255)
            sum = 0
        all_sums.append(tab)
        line_sums = []
    return all_sums
