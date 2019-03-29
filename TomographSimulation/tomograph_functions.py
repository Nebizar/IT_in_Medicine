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
    num_pix = np.zeros((size,size))
    for lines in list_of_lines:
        for line in lines:
            for point in line:
                if validate_point(point, size):
                    (x, y) = point
                    num_pix[x][y] += 1
                    color = img.getpixel((x, y))
                    sum_color = sum_color + color
                    lin_length += 1
            line_sums.append((sum_color / lin_length)/255)
            sum_color = 0
            lin_length = 0
        all_sums.append(line_sums)
        line_sums = []
        history.append(all_sums.copy())
    return all_sums, history, num_pix

def process_img(emitter, detectors, sinogram_col, img, size):
    for i in range(len(detectors)):
        for j in bresenham(emitter, detectors[i]):
            if validate_point(j, size):
                img[j[1]][j[0]] += sinogram_col[i]
    return img

def normalise(img, num_pix):
    maximum = 0
    for i in range(len(num_pix[0])):
        for j in range(len(num_pix[0])):
            if num_pix[i][j] != 0:
                img[i][j] = img[i][j]/num_pix[i][j]
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

def normalise_image(img):
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

def get_mask(mask_size):
    assert isinstance(mask_size, int)
    assert mask_size > 1

    mask = np.zeros(shape=(mask_size, ), dtype=np.float64)

    mask[0] = 1.0
    for i in range(1, mask_size):
        if i % 2 == 0:
            mask[i] == 0.0
        else:
            mask[i] = (-4 / (np.pi ** 2)) / (i ** 2)
    return mask


def filter_sinogram(sinogram_in, mask):
    #TODO make initialisation work
    n=len(sinogram_in)
    m=len(sinogram_in[0])
    sinogram_val=np.zeros((n,m))
    for i in range(len(sinogram_in)):
        for j in range(len(sinogram_in[i])):
            sinogram_val[i][j]=sinogram_in[i][j]
    n_angles, n_detectors = sinogram_val.shape
    assert n_detectors > 2
    mask_size = mask.shape[0]
    filtered = np.empty_like(sinogram_val)
    for i_angle in range(n_angles):
        for i_detector in range(n_detectors):
            value = sinogram_val[i_angle, i_detector] * mask[0]
            for dx in range(1, mask_size):
                if i_detector + dx < n_detectors:
                    value += sinogram_val[i_angle, i_detector + dx] * mask[dx]
                if i_detector - dx >= 0:
                    value += sinogram_val[i_angle, i_detector - dx] * mask[dx]
            filtered[i_angle, i_detector] = value
    filtered_sinogram = []
    for i in range(n_angles):
        filtered_sinogram_col = []
        for j in range(n_detectors):
            filtered_sinogram_col.append(filtered[i,j])
        filtered_sinogram.append(filtered_sinogram_col)
    return filtered_sinogram

def process_cone(detectors_num, detector_deg, iterations, size, img):
    history = []
    
    processed_img = np.zeros((size,size))
    
    history.append(processed_img.copy())
    
    detections = create_detections(iterations, detector_deg, detectors_num, size)

    sinogram_values, sinogram_history, pix_num = sinogram(img, detections, size)
    #print(sinogram_values)

    angles = np.linspace(0., 360., iterations, endpoint=False)

    for i in range(iterations):
        angle = angles[i]
        emitter, detectors = calculate_positions(angle, detector_deg, detectors_num, size)

        sinogram_col = sinogram_values[i]

        processed_img = process_img(emitter, detectors, sinogram_col, processed_img, size)
        history.append(processed_img.copy())
    normalise(processed_img, pix_num)

    return processed_img, history, sinogram_values, sinogram_history


def process_cone_filtered(detectors_num, detector_deg, iterations, size, img, mask_size):
    history = []

    processed_img = np.zeros((size, size))

    history.append(processed_img.copy())

    detections = create_detections(iterations, detector_deg, detectors_num, size)

    mask = get_mask(mask_size)

    sinogram_val, sinogram_history, num_pix = sinogram(img, detections, size)
    # print(sinogram_values)

    sinogram_values = filter_sinogram(sinogram_val,mask)

    angles = np.linspace(0., 360., iterations, endpoint=False)

    for i in range(iterations):
        angle = angles[i]
        emitter, detectors = calculate_positions(angle, detector_deg, detectors_num, size)

        sinogram_col = sinogram_values[i]

        processed_img = process_img(emitter, detectors, sinogram_col, processed_img, size)
        history.append(processed_img.copy())
    normalise(processed_img, num_pix)

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
        data[i] =  convert_to_image(normalise_image(data[i]))
    return data

def prepare_sinograms(data, iterations, detectors_num):
    for i in range(len(data)):
        empty = np.zeros((iterations,detectors_num))
        empty[0:len(data[i]),:] = data[i] 
        data[i] =  convert_to_image(normalise_image(empty))
    return data

def error(img1,img2,size):
    sum = 0
    for i in range(0,size):
        for j in range(0,size):
           sum = sum + pow((img1.getpixel((i,j)) - img2[i][j]),2)
    difference = (sum/pow(size,2))
    return difference