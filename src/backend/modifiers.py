"""
You can pass these modification functions as parameters to methods in processor.py to execute a 
specific modification on the file(s) also passed as parameters in those methods as explained below.
"""

#IMPORTS
import cv2
import numpy as np

#CONVENTIONAL IMAGE PROCESSING MODIFICATIONS:

#sharpen parameter:
sharpeningKernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])  

#bcontrast (these were parameters I very unrigorously found I liked best during testing)
selectedAlpha = 1.15
selectedBeta = -10 

#turn the frame grayscale
def grayscale(frame):
    """[grayscale]"""
    return cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2RGB)

#sharpen the frame with the above kernel
def sharpen(frame) :
    """[sharpen]"""
    return cv2.filter2D(frame, -1, sharpeningKernel)

#boost the frame's contrast
def bcontrast(frame) :
    """[bcontrast]"""
    return cv2.convertScaleAbs(frame, alpha=selectedAlpha, beta=selectedBeta) 

#sharpen, then boost contrast
def sharpen_bcontrast(frame):
    """[sharpen,bcontrast]"""
    return cv2.filter2D(cv2.convertScaleAbs(frame, alpha=selectedAlpha, beta=selectedBeta), -1, sharpeningKernel)

#boost contrast, then sharpen
def bcontrast_sharpen(frame):
    """[bcontrast,sharpen]"""
    return cv2.convertScaleAbs(cv2.filter2D(frame, -1, sharpeningKernel), alpha=selectedAlpha, beta=selectedBeta)

#apply a gaussina blur with a 5x5 kernel, this is used to make sample test videos to upscale bacl
def blur(frame) :
    """[blur]"""
    return cv2.GaussianBlur(frame, (5,5), 0)

#denoise the image (don't use this unless absolutely nescessary mods_test shows this takes almost 1/4 of a second
#per one frame on the AOT episodes, which is very slow)
def denoise(frame) :
    """[denoise]"""
    return cv2.fastNlMeansDenoisingColored(frame, None, 11, 6, 7, 21)

#Do nothing, testing purposes only
def none(frame) :
    """[none]"""
    return frame