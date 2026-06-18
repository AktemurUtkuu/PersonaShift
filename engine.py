import sys
import os
import torchvision.transforms.functional as functional
sys.modules['torchvision.transforms.functional_tensor'] = functional
import cv2
import numpy as np
import time
import pyvirtualcam
from PyQt6.QtCore import QThread, pyqtSignal, Qt
import insightface
from insightface.app import FaceAnalysis
from gfpgan import GFPGANer

# --- YOL TANIMI ---
if getattr(sys, 'frozen', False):
    # PyInstaller ile derlenmişse:
    application_path = sys._MEIPASS
    # Basicsr kütüphanesinin paket içinde doğru algılanması için:
    sys.path.append(os.path.join(application_path, 'basicsr'))
else:
    # Normal çalıştırma:
    application_path = os.path.dirname(os.path.abspath(__file__))
# ------------------

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray, int)

    def __init__(self):
        super().__init__()
        self._run_flag = False
        self.last_frame = None
        
        self.brightness = 0   
        self.contrast = 1.0   
        
        self.single_face_mode = False
        self.target_width = 1280
        self.target_height = 720
        self.change_res_flag = False
        
        print("Yapay Zeka Modelleri Yükleniyor...")
        
        
        model_dir = os.path.join(application_path, 'models')
        
        self.app = FaceAnalysis(name='buffalo_l', root=model_dir, providers=['CUDAExecutionProvider'], allowed_modules=['detection', 'recognition', 'landmark_2d_106'])
        self.app.prepare(ctx_id=0, det_size=(320, 320))
        
        
        swapper_path = os.path.join(application_path, 'models', 'inswapper_128.onnx')
        if os.path.exists(swapper_path):
            self.swapper = insightface.model_zoo.get_model(swapper_path, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
            print(f"Yüz değiştirme modeli yüklendi: {swapper_path}")
        else:
            self.swapper = None

        gfpgan_path = os.path.join(application_path, 'models', 'GFPGANv1.4.pth')
        if os.path.exists(gfpgan_path):
            self.enhancer = GFPGANer(model_path=gfpgan_path, upscale=1, arch='clean', channel_multiplier=2, bg_upsampler=None, device='cuda')
            print(f"Yüz netleştirici modeli yüklendi: {gfpgan_path}")
        else:
            self.enhancer = None

        self.source_face = None 
        self.ui_ready = True
        self.hd_mode = False
        print("Modeller Hazır.")

    def set_source_face(self, face_path):
        img = cv2.imread(face_path)
        if img is not None:
            faces = self.app.get(img)
            if len(faces) > 0:
                self.source_face = faces[0]
                print(f"Kaynak yüz başarıyla yüklendi: {os.path.basename(face_path)}")
            else:
                self.source_face = None

    def set_resolution(self, width, height):
        self.target_width = width
        self.target_height = height
        self.change_res_flag = True

    def run(self):
        self._run_flag = True
        cap = cv2.VideoCapture(0)
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
        cap.set(cv2.CAP_PROP_FPS, 30) 
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        fps = 0
        frame_counter = 0
        cached_faces = []

        virtual_cam_active = False
        try:
            self.cam = pyvirtualcam.Camera(width=960, height=540, fps=30, fmt=pyvirtualcam.PixelFormat.BGR, backend='unitycapture', device='Unity Video Capture')
            virtual_cam_active = True
        except Exception as e:
            print(f"Sanal Kamera Başlatılamadı: {e}")

        while self._run_flag:
            if self.change_res_flag:
                cap.release()
                time.sleep(0.5)
                cap = cv2.VideoCapture(0)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
                cap.set(cv2.CAP_PROP_FPS, 30)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.change_res_flag = False

            ret, frame = cap.read()
            if ret:
                start_time = time.time()
                frame = cv2.convertScaleAbs(frame, alpha=self.contrast, beta=self.brightness)
                frame = cv2.resize(frame, (960, 540))
                frame_counter += 1
                
                if frame_counter % 2 == 1:
                    cached_faces = self.app.get(frame)
                
                if self.source_face is not None and self.swapper is not None:
                    faces_to_process = cached_faces
                    if self.single_face_mode and len(cached_faces) > 0:
                        largest_face = max(cached_faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[0]))
                        faces_to_process = [largest_face]

                    for face in faces_to_process:
                        frame = self.swapper.get(frame, face, self.source_face, paste_back=True)
                    
                    if self.hd_mode and self.enhancer is not None:
                        _, _, frame = self.enhancer.enhance(frame, paste_back=True)
                            
                else:
                    for face in cached_faces:
                        if hasattr(face, 'landmark_2d_106') and face.landmark_2d_106 is not None:
                            landmarks = face.landmark_2d_106.astype(int)
                            for point in landmarks:
                                cv2.circle(frame, (point[0], point[1]), 2, (0, 0, 255), -1)
                        elif hasattr(face, 'kps') and face.kps is not None:
                            landmarks = face.kps.astype(int)
                            for point in landmarks:
                                cv2.circle(frame, (point[0], point[1]), 3, (0, 0, 255), -1)

                if virtual_cam_active:
                    self.cam.send(frame)

                process_time = time.time() - start_time
                if process_time > 0:
                    current_fps = int(1.0 / process_time)
                    fps = int((fps * 0.9) + (current_fps * 0.1)) if fps > 0 else current_fps

                if self.ui_ready:
                    self.last_frame = frame.copy()
                    self.ui_ready = False
                    self.change_pixmap_signal.emit(frame.copy(), fps)
            
        cap.release()
        if virtual_cam_active:
            self.cam.close()
            
    def stop(self):
        self._run_flag = False
        self.wait()