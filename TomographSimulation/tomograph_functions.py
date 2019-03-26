# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 11:59:35 2019

@author: Mikołaj Frankowski, Krzysztof Pasiewicz
"""
import numpy as np
from bresenham import bresenham, bresenham_converted

# *************************************
# validate if point is on image or not
# point -> tuple of coordinates (x, y)
# size -> size of square image
# returns: True if ok, else False
# *************************************
def validate_point(point, size):
    if point[0]>=0 and point[0]<size and point[1]>=0 and point[1]<size:
        return True
    else:
        return False

# **************************************************
# make image square for easier computations
# img -> iamge in PIL.Image format
# returns: resized image; size of new, square image
# **************************************************
def make_square(img):
    from PIL import Image
    
    shape = img.size
    if shape[0]>shape[1]:
        expanded = Image.new("L", (shape[0], shape[0]))
        expanded.paste(img, (int((shape[0]-shape[0])/2), int((shape[0]-shape[1])/2)))
        return expanded, shape[0]
    if shape[1]>shape[0]:
        expanded = Image.new("L", (shape[1], shape[1]))
        expanded.paste(img, (int((shape[1]-shape[0])/2), int((shape[1]-shape[1])/2)))
        return expanded, shape[1]
    else:
        return img, shape[0]

# ********************************************************************   
# calculate points for emiter and detectors
# emitter_deg -> position angle of emitter from main axis
# detectors_deg -> angle between furthest detectors in emitter point
# detectors_num -> number of detectors
# size -> square image size
# returns: numpy array of emitter coords, array of detectors positions
# ********************************************************************
def calculate_positions(emitter_deg, detectors_deg, detectors_num, size):
    positions = []
    angleEm = np.deg2rad(emitter_deg)
    angleDet = np.deg2rad(detectors_deg)
    r = (size * np.sqrt(2))/2
    center = size/2
    emitter_position = [int(r*np.cos(angleEm)+ center), int(r*np.sin(angleEm)+ center)]
    if detectors_num > 1:
        for detector in range(0,detectors_num):
            positions.append([int(r*np.cos(angleEm + np.pi - angleDet/2 + detector * angleDet / (detectors_num-1) )+ center),
                             int(r*np.sin(angleEm + np.pi - angleDet/2 + detector * angleDet / (detectors_num-1) )+ center)])
    elif detectors_num == 1:
        positions.append([int(r*np.cos(angleEm + np.pi)+ center),
                          int(r*np.sin(angleEm + np.pi)+ center)])
    else:
        print("ValueError - detectors_num must be higher than 0 \n")
        return [], []
    return emitter_position, positions

# *************************************************************************************************************
# create list of all detections - each detections is list of arrays of points between emiter and aeach detector
# iterations -> number of measurements
# detectors_deg -> angle between furthest detectors in emitter point
# detectors_num -> number of detectors
# size -> square image size
# returns: list of lists of tuples of points to read
# *************************************************************************************************************
def create_detections(iterations, detectors_deg, detectors_num, size):
    emiterAngles = np.linspace(0., 360., iterations, endpoint=False)
    list_of_lines =[]
    for angle in emiterAngles:
        measurement = []
        emiter, detectors = calculate_positions(angle, detectors_deg, detectors_num, size)
        for detector in detectors:
            points = bresenham_converted(emiter, detector)
            measurement.append(points)
        list_of_lines.append(measurement)
    return list_of_lines
            

def sinogram(img,list_of_lines, size):
    sum_color = 0
    lin_length = 0
    line_sums = []
    all_sums = []
    history = []

    for lines in list_of_lines:
        for line in lines:
            for point in line:
                if validate_point(point, size):
                    (x, y) = point
                    color = img.getpixel((x, y))
                    sum_color = sum_color + color
                    lin_length += 1
            line_sums.append((sum_color / lin_length)/255)
            sum_color = 0
            lin_length = 0
        all_sums.append(line_sums)
        line_sums = []
        history.append(all_sums.copy())
    return all_sums, history

def process_img(emitter, detectors, sinogram_col, img, size):
    for i in range(len(detectors)):
        for j in bresenham(emitter, detectors[i]):
            if validate_point(j, size):
                img[j[1]][j[0]] += sinogram_col[i]
    return img

def normalise(img):
    maximum = 0
    for column in img:
        if max(column) > maximum:
            maximum = max(column)

    for i in range(len(img)):
        for j in range(len(img[0])):
            if maximum != 0 and img[i][j] > 0:
                img[i][j] = img[i][j]/maximum
            else:
                img[i][j] = 0

    return img

def convolution(receivers_number,emitters_number):
    image = []

    for i in range(emitters_number):
        row = []
        for j in range(receivers_number):
            row.append(0)
        image.append(row)

    amount = receivers_number
    result = []

    for i in range(0, amount):
        result.append(0)

    mask = []
    for j in range(0, (amount * 2 - 1)):
        mask.append(0)

    rank_sum = 1;

    for i in range(0,(amount * 2 - 1)):
        j = i-amount + 1
        if(j%2 == 0):
            mask[i] = 0
        else:
            mask[i] = (-4/(np.pi*np.pi*j*j))
        rank_sum = rank_sum + mask[i]

    mask[amount - 1] = 1
    start = 0
    p = 0

    while(start < 2*np.pi):
        for i in range(0,amount):
            sum = 0
            for j in range(0,(amount*2 -1)):
                mask_dist = amount -1 -j
                k = i - mask_dist
                if((k>=0) and (k<amount)):
                    sum = sum + image[p][k] * mask[amount-mask_dist-1]
            image[p][i] = sum/rank_sum
        p = p + 1
        if(p==emitters_number):
            break
        start  = start + (2*np.pi/emitters_number)
    return image

def process_cone(detectors_num, detector_deg, iterations, size, img):
    history = []
    
    processed_img = np.zeros((size,size))
    
    history.append(processed_img.copy())
    
    detections = create_detections(iterations, detector_deg, detectors_num, size)

    sinogram_values, sinogram_history = sinogram(img, detections, size)
    #print(sinogram_values)

    angles = np.linspace(0., 360., iterations, endpoint=False)

    for i in range(iterations):
        angle = angles[i]
        emitter, detectors = calculate_positions(angle, detector_deg, detectors_num, size)

        sinogram_col = sinogram_values[i]

        processed_img = process_img(emitter, detectors, sinogram_col, processed_img, size)
        history.append(processed_img.copy())
    normalise(processed_img)

    return processed_img, history, sinogram_values, sinogram_history

# ********************************************
# convert array of values to PIL.Image format
# array -> matrix of colors representng image
# returns: image in PIL.Image format
# ********************************************
def convert_to_image(array):
    from PIL import Image
    
    array = (np.array(array)*256).astype(np.uint8)
    img = Image.fromarray(array)
    return img

# ***************************************************  
# prepares images of steps to animation
# data -> array of images from process_cone function
# returns: same array of normalised PIL.Image images
# ***************************************************
def prepare_images(data):
    for i in range(len(data)):
        data[i] =  convert_to_image(normalise(data[i]))
    return data

def prepare_sinograms(data, iterations, detectors_num):
    for i in range(len(data)):
        empty = np.zeros((iterations,detectors_num))
        empty[0:len(data[i]),:] = data[i] 
        data[i] =  convert_to_image(normalise(empty))
    return data
