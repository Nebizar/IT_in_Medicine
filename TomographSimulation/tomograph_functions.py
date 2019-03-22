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
        all_sums.append(line_sums)
        line_sums = []
    return all_sums

def convolution(receivers_number,emitters_number):
    image = []

    for i in range(emitters_number):
        row = []
        for j in range(receivers_number):
            row.append(0)
        image.append(row)

    amout = receivers_number
    result = []

    for i in range(0, amout):
        result.append(0)

    mask = []
    for j in range(0, (amout * 2 - 1)):
        mask.append(0)

    rank_sum = 1;

    for i in range(0,(amout * 2 - 1)):
        j = i-amout + 1
        if(j%2 == 0):
            mask[i] = 0
        else:
            mask[i] = (-4/(np.pi*np.pi*j*j))
        rank_sum = rank_sum + mask[i]

    mask[amout - 1] = 1
    start = 0
    p = 0

    while(start < 2*np.pi):
        for i in range(0,amout):
            sum = 0
            for j in range(0,(amout*2 -1)):
                mask_dist = amout -1 -j
                k = i - mask_dist
                if((k>=0) and (k<amout)):
                    sum = sum + image[p][k] * mask[amout-mask_dist-1]
            image[p][i] = sum/rank_sum
        p = p + 1
        if(p==emitters_number):
            break
        start  = start + (2*np.pi/emitters_number)
    return image
