import sys
import json
import cv2 as cv
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, 
                             QFileDialog, QCheckBox, QLabel, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QBrush, QPainterPath

from model import Model

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.model = Model()
        
        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 800, 600)

        self.frame_width = 900
        self.frame_height = 500

        self.video_widget = QWidget(self)
        self.setCentralWidget(self.video_widget)
        
        layout = QVBoxLayout(self.video_widget)
        
        self.video_label = QLabel(self)
        layout.addWidget(self.video_label)
        
        self.process_button = QPushButton("Process Video", self)
        self.process_button.clicked.connect(self.process_video)
        layout.addWidget(self.process_button)

        self.save_button = QPushButton("Save JSON results", self)
        self.save_button.clicked.connect(self.save_json)
        layout.addWidget(self.save_button)
        self.save_button.setEnabled(False)

        self.load_button = QPushButton("Load JSON results", self)
        self.load_button.clicked.connect(self.load_json)
        layout.addWidget(self.load_button)

        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.play_video)
        layout.addWidget(self.play_button)
        self.play_button.setEnabled(False)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_video)
        layout.addWidget(self.stop_button)
        self.stop_button.setEnabled(False)

        self.select_video_button = QPushButton("Select Video", self)
        self.select_video_button.clicked.connect(self.choose_video_file)
        layout.addWidget(self.select_video_button)
        
        self.cap = None
        self.video_file = None
        self.frame_annotations = {}
        self.current_time = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        
        self.checkbox_widget = QWidget(self)
        self.checkbox_layout = QVBoxLayout(self.checkbox_widget)
        layout.addWidget(self.checkbox_widget)
        
        self.checkboxes = []

        self.labels_used = self.model.get_possible_labels()
        self.use_model = True

        self.create_checkboxes()

    def get_objects_using_model(self, frame, current_time):
        annotations = self.model.predict(frame, current_time)
        for annotation in annotations:
            x1, y1, x2, y2 = annotation["bbox"]
            x1 *= frame.shape[1]  # Adjusting to frame width
            x2 *= frame.shape[1]
            y1 *= frame.shape[0]  # Adjusting to frame height
            y2 *= frame.shape[0]
            x, y, w, h = list(map(int, (x1, y1, (x2 - x1), (y2 - y1))))
            annotation["bbox"] = [x, y, w, h]
        print(f"Time {current_time} predictions: {annotations}")  # Debug print
        return annotations

    def process_video(self):
        if not self.video_file:
            self.show_error("Please select a video file first.")
            return

        self.cap = cv.VideoCapture(self.video_file)
        annotations = {}
        
        fps = self.cap.get(cv.CAP_PROP_FPS)
        frame_count = 0

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            current_time = frame_count / fps
            current_time = round(current_time, 1)  # rounding to 1 decimal place for better accuracy
            time_key = f"{current_time:.1f}"  # Convert to string format with one decimal place
            if time_key not in annotations:
                annotations[time_key] = []
            annotations[time_key] = self.get_objects_using_model(frame, current_time)
            frame_count += 1

        self.cap.release()

        self.frame_annotations = annotations
        self.save_button.setEnabled(True)
        self.play_button.setEnabled(True)
        self.show_message("Processing complete. JSON file is ready to be saved.")

        self.create_checkboxes()

    def save_json(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save JSON results", "", "JSON Files (*.json)", options=options)
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(self.frame_annotations, f, indent=4)
            self.show_message(f"JSON file saved successfully at {file_path}")

    def load_json(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load JSON results", "", "JSON Files (*.json)", options=options)
        if file_path:
            with open(file_path, 'r') as f:
                self.frame_annotations = json.load(f)
            self.show_message(f"JSON file loaded successfully from {file_path}")
            self.play_button.setEnabled(True)

    def create_checkboxes(self):
        for i in reversed(range(self.checkbox_layout.count())): 
            self.checkbox_layout.itemAt(i).widget().setParent(None)

        for label in self.model.label_names.values():
            checkbox = QCheckBox(label, self)
            checkbox.setChecked(True)
            self.checkboxes.append(checkbox)
            self.checkbox_layout.addWidget(checkbox)
        
    def choose_video_file(self):
        if self.video_file and self.cap and self.cap.isOpened():
            self.cap.release()
            self.play_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.current_time = 0
        self.video_file, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi)")
        if self.video_file:
            self.cap = cv.VideoCapture(self.video_file)
            self.update_frame()
            self.process_button.setEnabled(True)

    def play_video(self):
        if not self.cap.isOpened():
            self.cap.open(self.video_file)
        self.timer.start(30)
        self.play_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_video(self):
        self.timer.stop()
        if self.cap.isOpened():
            self.play_button.setEnabled(True)
            self.stop_button.setEnabled(False)
        
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_time = self.cap.get(cv.CAP_PROP_POS_MSEC) / 1000.0
            self.current_time = round(self.current_time, 1)  # rounding to 1 decimal place for better accuracy
            time_key = f"{self.current_time:.1f}"  # Convert to string format with one decimal place
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            pixmap = pixmap.scaled(self.frame_width, self.frame_height)
            painter = QPainter(pixmap)
            self.draw_annotations(painter, frame, time_key)
            painter.end()
            self.video_label.setPixmap(pixmap)
            self.video_label.setAlignment(Qt.AlignCenter)
        else:
            self.cap.release()
            self.timer.stop()
            self.play_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.current_time = 0
            
    def draw_annotations(self, painter: QPainter, frame: np.array, time_key: str):
        if time_key in self.frame_annotations:
            print(f'Time Key: {time_key}')
            print(f'Annotation: {self.frame_annotations[time_key]}')
            annotations = self.frame_annotations[time_key]
            if annotations:
                active_checkboxes = self.get_active_checkboxes()
                print(f'Active checkboxes: {active_checkboxes}')
                for annotation in annotations:
                    label = annotation['label']
                    print(f'Processing label: {label}')
                    if label not in active_checkboxes:
                        print(f'Skipping label: {label}')
                        continue
                    x, y, w, h = annotation['bbox']
                    
                    # Convert relative coordinates to absolute coordinates
                    x = int(x / frame.shape[1] * self.frame_width)
                    y = int(y / frame.shape[0] * self.frame_height)
                    w = int(w / frame.shape[1] * self.frame_width)
                    h = int(h / frame.shape[0] * self.frame_height)
                    
                    print(f'Drawing bbox for label {label}: x={x}, y={y}, w={w}, h={h}')  # Debug print
                    pen = QPen(QColor('red'))
                    pen.setWidth(4)
                    painter.setPen(pen)
                    painter.drawRect(x, y, w, h)

                    font = painter.font()
                    font.setPixelSize(35)
                    painter.setFont(font)
                    painter.setPen(QPen(QColor('black')))
                    painter.drawText(x, y - 10, label)
            else:
                print(f"Annotations list is empty for {time_key} time key.")
        else:
            print("No data for this time key.")

    def get_active_checkboxes(self):
        active_checkboxes = []
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                active_checkboxes.append(checkbox.text())
        print(f"Active checkboxes: {active_checkboxes}")  # Debug print
        return active_checkboxes

    def show_message(self, message):
        msg_box = QMessageBox(self)
        msg_box.setText(message)
        msg_box.setStyleSheet("background-color: green;")
        msg_box.exec_()

    def show_error(self, message):
        msg_box = QMessageBox(self)
        msg_box.setText(message)
        msg_box.setStyleSheet("background-color: red;")
        msg_box.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
