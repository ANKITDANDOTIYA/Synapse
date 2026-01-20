import cv2
import numpy as np
import os
import sqlite3
from ultralytics import YOLO
from insightface.app import FaceAnalysis
import pickle
import json
import colorama

class Vision_Pro:
    def __init__(self):
        print('Initializing Vision Pro Engine...')
        self.yolo = YOLO('yolov8n.pt')
        self.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

        self.conn = sqlite3.connect('vision_pro.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_db()

        self.known_names = []
        self.known_embeddings = []
        self.known_info = []
        self.load_memory()
        print('Vision Pro Engine Ready.')

    def setup_db(self):
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS humans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                info TEXT,
                embedding BLOB
            )
        ''')
        self.conn.commit()

    def load_memory(self):
        print(colorama.Fore.CYAN + 'Loading Vision Pro Memory...')
        self.cursor.execute("SELECT name, embedding, info FROM humans")
        rows = self.cursor.fetchall()
        
        self.known_info = []
        self.known_names = []
        self.known_embeddings = []

        for name, enc_blob, info_json in rows:
            embedding = pickle.loads(enc_blob)

            try:
                info = json.loads(info_json) if info_json else {}
            except:
                info = {}
            
            self.known_names.append(name)
            self.known_embeddings.append(embedding)
            self.known_info.append(info)

        print(colorama.Fore.GREEN + f"[Vision] Loaded {len(self.known_names)} identities.")

    def register_face(self, frame, name, info_dict):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.app.get(rgb_frame)

        if len(faces) == 0:
            print(f'No faces detected')
            return False
        
        face = sorted(faces, key=lambda x: x.bbox[2]*x.bbox[3])[-1]
        embedding = face.embedding
        
        binary_enc = pickle.dumps(embedding)
        json_info = json.dumps(info_dict)

        self.cursor.execute("INSERT INTO humans (name, embedding, info) VALUES (?, ?, ?)", 
                            (name, binary_enc, json_info))
        self.conn.commit()  

        self.known_embeddings.append(embedding)
        self.known_names.append(name)   
        self.known_info.append(info_dict)   

        print(colorama.Fore.GREEN + f"[Vision] Registered new face: {name}")    
        return True
    
    def recognize(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.app.get(rgb_frame)

        recognized = []
        for face in faces:
            embedding = face.embedding
            name = "Unknown"
            info = {}
            max_score = 0.0

            if len(self.known_embeddings) > 0:
                known_matrix = np.array(self.known_embeddings)

                sims = np.dot(known_matrix, embedding) / (
                    np.linalg.norm(known_matrix, axis=1) * np.linalg.norm(embedding)
                )

                best_idx = np.argmax(sims)
                max_score = sims[best_idx]

                if max_score > 0.5:
                    name = self.known_names[best_idx]
                    info = self.known_info[best_idx]
             
            bbox = face.bbox.astype(int)
            recognized.append({
                 'name': name,
                 'info': info,
                 'bbox': bbox,
                 'score': float(max_score)
            })
        
        return recognized

if __name__ == "__main__":
    v = Vision_Pro()
   
    cap = cv2.VideoCapture(0)
    print("Press 'r' to register yourself, 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        detections = v.recognize(frame)
        
        for d in detections:
            x1, y1, x2, y2 = d['bbox']
            name = d['name']
            score = d['score']
            info = d['info']
            
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            label = f"{name} ({int(score*100)}%)"
            cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            if name != "Unknown" and info:
                info_str = str(info.get('role', ''))
                cv2.putText(frame, info_str, (x1, y2+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        cv2.imshow("Trinetra InsightFace", frame)
        
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('r'):
            my_name = input("Enter Name: ")
            my_role = input("Enter Role (e.g. Admin/User): ")
            
            info_data = {
                "role": my_role,
                "access": "Level 1",
                "last_seen": "Today"
            }
            
            v.register_face(frame, my_name, info_data)

    cap.release()
    cv2.destroyAllWindows()