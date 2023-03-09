import numpy as np
import cv2
import argparse
import os

from TSR import table_structure_recognition_all as tsra
from TSR import table_structure_recognition_lines as tsrl
from TSR import table_structure_recognition_lines_wol as tsrlwol
from TSR import table_structure_recognition_wol as tsrwol
import table_ocr as tocr

from table_xml import output_to_xml

if __name__ == "__main__":
    type_dict = {"borderd":tsrl, "unbordered":tsrwol, "partially":tsrlwol, "partially_color_inv":tsra}
    
    folder = 'img/'
    img_output = 'out/'
    xml_output = 'xml/'
    
    files = os.listdir(folder)
    
    for file in files:
        print(file)
        print(folder)
        img = cv2.imread(folder + "/" + file)
        print('img: ', img)
        boxes, img_processed = tsrl.recognize_structure(img)
        print(img_output + "/" + file)
        if img_output:
            cv2.imwrite(img_output + "/" + file, img_processed)
        if xml_output:
            print(xml_output + "/" + file[:-3])
            output_to_xml(boxes, xml_output + "/" + file[:-3])
            tocr.output_to_csv(boxes, img_processed)
