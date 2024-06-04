import cv2 as cv

class Model:
    def __init__(self):
        prototxt = "/home/sheva/PycharmProjects/Src/Src/models/MobileNetSSD_deploy.prototxt"
        caffe_model = "/home/sheva/PycharmProjects/Src/Src/models/MobileNetSSD_deploy.caffemodel"
        
        self.model = cv.dnn.readNetFromCaffe(prototxt, caffe_model)
        self.label_names = { 0: 'background', 1: 'aeroplane', 2: 'bicycle', 
                      3: 'bird', 4: 'boat', 5: 'bottle', 6: 'bus', 7: 'car', 
                      8: 'cat', 9: 'chair', 10: 'cow', 11: 'diningtable', 
                      12: 'dog', 13: 'horse', 14: 'motorbike', 15: 'person', 
                      16: 'pottedplant', 17: 'sheep', 18: 'sofa', 19: 'train', 
                      20: 'tvmonitor'}
        self.labels_used = list(self.label_names.values())
        print(f"Labels used by the model: {self.labels_used}")  # Debug print

    def get_possible_labels(self):
        return self.labels_used.copy()

    def predict(self, image, current_time):
        blob = cv.dnn.blobFromImage(image, scalefactor = 1/127.5, 
                                    size = (300, 300), 
                                    mean = (127.5, 127.5, 127.5), 
                                    swapRB=True, crop=False)
        self.model.setInput(blob)
        detections = self.model.forward()

        annotations = []
        for i in range(detections.shape[2]):
            label = self.label_names[int(detections[0, 0, i, 1])]
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5 and label in self.labels_used:
                x1, y1, x2, y2 = (
                    detections[0, 0, i, 3],
                    detections[0, 0, i, 4], 
                    detections[0, 0, i, 5],
                    detections[0, 0, i, 6]
                )
                annotations.append({
                   "bbox": (x1, y1, x2, y2),
                   "label": label,
                   "frame": current_time
                })
        print(f"Time {current_time} predictions: {annotations}")  # Debug print
        return annotations
