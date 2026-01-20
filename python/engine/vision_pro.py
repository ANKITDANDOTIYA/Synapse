
from multiprocessing.spawn import prepare
import cv2
import numpy as np
import os
import sqlite3
from torch import embedding
from ultralytics import YOLO
from insightface.app import FaceAnalysis
import pickle
import json
import colorama

class Vision_Pro :
    def __intit__ (self):
        print ('Initializing Vision Pro Engine...')
        self.yolo = YOLO('yolov8n.pt')
        self.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.add = prepare(ctx_id = 0, det_size =(640, 640))


        self.conn = sqlite3.connect('vision_pro.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_db()

        self.known_face = []
        self.known_names = []
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
        self.cursor.fetchall()
        self.known_info = []
        self.known_names = []
        self.known_embeddings = []

        for name, enc_blob, info_json in rows:
            embedding = pickle.load(enc_blob)

            try:
                info = json.loads(info_json) if info_json else {}
            except :
                info = {}
            self.known_names.appen(name)
            self.known_embeddings.append(embedding)
            self.knwon_info.append(info)

            print(colorama.Fore.GREEN + f"[Vision] Loaded {len(self.known_names)} identities.")

    def register_face(self, frame, name, info_dict) :
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.app.get(rgb_frame)

        if len(faces) == 0:
            print(f'No faces detected')
            return False
        face = sorted(faces, key=lambda x: x.bbox[2]*x.bbox[3])[-1]

        embedding = face.embedding
        
        binary_enc = pickle.dumps(embedding)
        json_info =  json.dumps(info_dict)

        self.cursor.execute("INSERT INTO humans (name, embedding, info) VALUES (?, ?, ?)", 
                            (name, binary_enc, json_info))
        self.conn.commit()  

        self.known_embeddings.append(embedding)
        self.known_names.append(name)   
        self.known_info.append(info_dict)   

        print(colorama.Fore.GREEN + f"[Vision] Registered new face: {name}")    

        return True