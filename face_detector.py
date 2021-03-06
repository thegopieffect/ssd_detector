#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103
# pylint: disable=E1101

import sys
import time
import numpy as np
import tensorflow as tf
import cv2
import glob

sys.path.append("..")

from utils import label_map_util
from utils import visualization_utils_color as vis_util

def detector(_img_, _confidence_):

    # Path to frozen detection graph. This is the actual model that is used for the object detection.
    PATH_TO_CKPT = '../model/frozen_inference_graph_face.pb'
    # List of the strings that is used to add correct label for each box.
    PATH_TO_LABELS = '../protos/face_label_map.pbtxt'
    NUM_CLASSES = 2
    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)
    img_height, img_width, img_channel = cv2.imread(_img_).shape

    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
    with detection_graph.as_default():
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        with tf.Session(graph=detection_graph, config=config) as sess:
            img = cv2.imread(_img_)
            image_np = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # the array based representation of the image will be used later in order to prepare the
            # result image with boxes and labels on it.
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            # Each box represents a part of the image where a particular object was detected.
            boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            scores = detection_graph.get_tensor_by_name('detection_scores:0')
            classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')
            # Actual detection.
            (boxes, scores, classes, num_detections) = sess.run([boxes, scores, classes, num_detections], feed_dict={image_tensor: image_np_expanded})
            #elapsed_time = time.time() - start_time
            #print(boxes.shape, boxes)
            #print(scores.shape,scores)
            #print(classes.shape,classes)
            #print(num_detections)
            no_of_det = len([score for score in scores[0] if score >= _confidence_])
            #print(len(valid_detections))
            # Visualization of the results of a detection.
            #vis_util.visualize_boxes_and_labels_on_image_array(img, np.squeeze(boxes), np.squeeze(classes).astype(np.int32), np.squeeze(scores), category_index, use_normalized_coordinates=True, line_thickness=4)
            #out.write(image)
            #cv2.imshow('Frame', img)
            #bbox and confidence score for detections above the threshold limit
            bbox = boxes[0][:no_of_det]
            conf_score = scores[0][:no_of_det]
            coord_dict = dict(zip(conf_score, bbox))
            #denorm the bbox coordinates 
            for key, value in coord_dict.items():
                coord_dict[key] = [value[1] * img_width, value[0] * img_height, value[3] * img_width, value[2] * img_height]
            return coord_dict

