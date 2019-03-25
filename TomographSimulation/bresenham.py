# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 11:59:35 2019

@author: Krzysztof Pasiewicz
"""

import numpy as np


"""
    bresenham algorithm implementation
    input: start, end-> tuple of coordinates
    returns: numpy array of points lying on the line between start and end
"""
def bresenham(start, end):
    (x0, y0) = start
    (x1, y1) = end
    # step 1 get end-points of line 
    dx = x1 - x0
    dy = y1 - y0

    xsign = 1 if dx > 0 else -1
    ysign = 1 if dy > 0 else -1

    dx = abs(dx)
    dy = abs(dy)

    if dx > dy:
        xx, xy, yx, yy = xsign, 0, 0, ysign
    else:
        dx, dy = dy, dx
        xx, xy, yx, yy = 0, ysign, xsign, 0

    D = 2*dy - dx
    y = 0

    for x in range(dx + 1):
        yield x0 + x*xx + y*yx, y0 + x*xy + y*yy
        if D >= 0:
            y += 1
            D -= 2*dx
        D += 2*dy
        
def bresenham_converted(start, end):
    out = []
    for i in bresenham(start,end):
        out.append(i)
    
    return out
