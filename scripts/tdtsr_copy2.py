import numpy as np
import cv2
import argparse
import os
import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

from detectron2.data import DatasetCatalog, MetadataCatalog

import pandas as pd

import json
import itertools

from TSR import table_structure_recognition_all as tsra
from TSR import table_structure_recognition_lines as tsrl
from TSR import table_structure_recognition_lines_wol as tsrlwol
from TSR import table_structure_recognition_wol as tsrwol
import table_detection
import table_ocr as tocr

from table_xml import output_to_xml

def deskewImage(img):
    """
    adapted from: https://www.pyimagesearch.com/2017/02/20/text-skew-correction-opencv-python/
    """
    
    # use medianBluer to remove black artefacts from the image
    image = cv2.medianBlur(img, 5)
    
    # convert the image to grayscale and flip the foreground
    # and background to ensure foreground is now "white" and
    # the background is "black"
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    # threshold the image, setting all foreground pixels to
    # 255 and all background pixels to 0
    thresh = cv2.threshold(gray, 0, 255,
    	cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # grab the (x, y) coordinates of all pixel values that
    # are greater than zero, then use these coordinates to
    # compute a rotated bounding box that contains all
    # coordinates
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    print('angle: ', angle)
    # the `cv2.minAreaRect` function returns values in the
    # range [-90, 0); as the rectangle rotates clockwise the
    # returned angle trends to 0 -- in this special case we
    # need to add 90 degrees to the angle
    if angle < -45:
    	angle = -(90 + angle)
    # otherwise, just take the inverse of the angle to make
    # it positive
    else:
    	angle = -angle
        
    # rotate the image to deskew it
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    rotated_img = cv2.warpAffine(img, M, (w, h),
    	flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated_img

if __name__ == "__main__":
    type_dict = {"borderd":tsrl, "unbordered":tsrwol, "partially":tsrlwol, "partially_color_inv":tsra}
    
    folder='img/'
    tsr_img_output = "out/ts"
    td_img_output= "out/td"
    td_xml_output="xml"
    yaml="/root/autodl-tmp/Multi-Type-TD-TSR/All_X152.yaml"
    weights="/root/autodl-tmp/Multi-Type-TD-TSR/model_final.pth"

    #create detectron config
    # cfg = get_cfg(config)
    cfg = get_cfg()

    #set yaml
    cfg.merge_from_file(yaml)

    #set model weights
    cfg.MODEL.WEIGHTS = weights # Set path model .pth

    predictor = DefaultPredictor(cfg) 

    files = os.listdir(folder)

    for file in files:
        img = cv2.imread(folder + "/" + file)
        # deskewed_image = deskewImage(img)
        deskewed_image = img
        table_list, table_coords = table_detection.make_prediction(deskewed_image, predictor)
        list_table_boxes = []

        for table in table_list:
            boxes, table_processed = type_dict["borderd"].recognize_structure(table)
            list_table_boxes.append(boxes)
            
            if tsr_img_output:
                cv2.imwrite(tsr_img_output + "/" + file, table_processed)
            if td_img_output:
                cv2.imwrite(td_img_output + "/" + file, table)
            if td_xml_output:
                print(td_xml_output + "/" + file[:-3])
                output_to_xml(boxes, td_xml_output + "/" + file[:-3])
                tocr.output_to_csv(boxes, table_processed)