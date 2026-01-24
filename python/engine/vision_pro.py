import cv2
import numpy as np
import sqlite3
import time
from ultralytics import YOLO
from insightface.app import FaceAnalysis
import pickle
import json
import colorama
from thefuzz import process
from python.engine.tts_engine import TTS_Engine


class Vision_Pro:
    def __init__(self):  # init constructor hai
        print('Initializing Vision Pro Engine...')
        self.yolo = YOLO('yolov8n.pt')  # self == this

        self.app = FaceAnalysis(
            name='buffalo_l',
            providers=['CPUExecutionProvider']
        )

        # buffallo_l model use kar raha hai agar
        # cuda available hai to use karega nahi to CPU

        self.app.prepare(ctx_id=0, det_size=(640, 640))
        # app ka object ban gya ab engine start karna prepare se ctx_id mtlb jo provider 
        # # diya hai usme se 0th index wala use karega camera se 1080p yaa 4K ko reframe 
        # karega 640x640 me
        # # and usme chehra dhundega, Face detection ke liye fast hai

        self.conn = sqlite3.connect('vision_pro.db', check_same_thread=False)
        # conn naam ka obj banaya ab ye database se connect karega vision_pro.db file se
        #  agar file nahi hai to nayi file bana dega
        # check_same_thread=False ka matlab hai ki multiple threads se access kar sakte hai 
        # sqllite ka rule hai jis thread ne banaya vahi access kar sakta hai good for multithreading

        self.cursor = self.conn.cursor()
        # conn bridge hai jaha se hum databse jayenge but cursor is the gaurd jo queries ko execute karega
        # jese insert select etc

        self.setup_db()
        # database setup karne ke liye function call kiya

        self.known_names = []  # same as arrayList or vector naaam ke liye
        self.known_embeddings = []  # dembeddings mtlb chehre ke features store karega
        self.known_info = []  # uska info store karega jaise role etc
        self.load_memory()  # function call kiya memory load karne ke liye

        self.cap = cv2.VideoCapture(0)
        print('Vision Pro Engine Ready.')

    def setup_db(self):
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS humans
            (
                id
                INTEGER
                PRIMARY
                KEY
                AUTOINCREMENT,
                name
                TEXT,
                info
                TEXT,
                embedding
                BLOB
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

    def register_face(self, frame, name, info_dict, tts_engine):
        # 1. FRONT FACE (Jo frame pass hua hai use hi use kar lo)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.app.get(rgb_frame)

        if len(faces) == 0:
            print(f'No faces detected')
            return False

        tts_engine.speak("Hold on, capturing front view.")
        # front face capture
        face_straight = sorted(faces, key=lambda x: x.bbox[2] * x.bbox[3])[-1]
        embedding_straight = face_straight.embedding

        # 2. left face
        tts_engine.speak("Now turn your face slightly to the left.")
        time.sleep(2)  # User ko time do

        ret, frame_left = self.cap.read()  # NEW PHOTO
        if not ret: return False

        rgb_left = cv2.cvtColor(frame_left, cv2.COLOR_BGR2RGB)
        faces_left = self.app.get(rgb_left)

        if len(faces_left) == 0:
            tts_engine.speak("Face not found in left view, using front view instead.")
            embedding_left = embedding_straight  # Fallback
        else:
            face_left_obj = sorted(faces_left, key=lambda x: x.bbox[2] * x.bbox[3])[-1]
            embedding_left = face_left_obj.embedding

        # right face lelo
        tts_engine.speak("Now turn slightly to the right.")
        time.sleep(2)

        ret, frame_right = self.cap.read()  # <--- NEW PHOTO
        if not ret: return False

        rgb_right = cv2.cvtColor(frame_right, cv2.COLOR_BGR2RGB)
        faces_right = self.app.get(rgb_right)

        if len(faces_right) == 0:
            tts_engine.speak("Face not found in right view, using front view instead.")
            embedding_right = embedding_straight  # Fallback
        else:
            face_right_obj = sorted(faces_right, key=lambda x: x.bbox[2] * x.bbox[3])[-1]
            embedding_right = face_right_obj.embedding  # <--- CORRECTED

        # info sunte hi json me dump karo
        json_info = json.dumps(info_dict)

        # Binary convert
        binary_enc_straight = pickle.dumps(embedding_straight)
        binary_enc_left = pickle.dumps(embedding_left)
        binary_enc_right = pickle.dumps(embedding_right)

        # 3 Rows Insert karo
        self.cursor.execute("INSERT INTO humans (name, embedding, info) VALUES (?, ?, ?)",
                            (name, binary_enc_straight, json_info))
        self.cursor.execute("INSERT INTO humans (name, embedding, info) VALUES (?, ?, ?)",
                            (name, binary_enc_left, json_info))
        self.cursor.execute("INSERT INTO humans (name, embedding, info) VALUES (?, ?, ?)",
                            (name, binary_enc_right, json_info))
        self.conn.commit()

        # List length barabar honi chahiye
        self.known_embeddings.append(embedding_straight)
        self.known_embeddings.append(embedding_left)
        self.known_embeddings.append(embedding_right)

        # Name aur Info ko bhi 3 baar add karna padega taaki index match ho
        self.known_names.extend([name, name, name])
        self.known_info.extend([info_dict, info_dict, info_dict])
        tts_engine.speak(f"Now I will remember you {name}.")
        print(colorama.Fore.GREEN + f"[Vision] Registered new face: {name} (3 Angles)")
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

    def scan_scene(self):
        ret, frame = self.cap.read()
        if not ret:
            return ["Camera Error"]

        results = self.recognize(frame)


        if not results:
            return []  # Khali list return karo

        found_names = []
        for face in results:
            name = face['name']
            found_names.append(name)
        return found_names

    def get_info(self, name):
        # Safety check: If name is None or not in our database
        if name is None:
            return None
        if name not in self.known_names:
            return None
        best_match, score = process.extractOne(name, self.known_names)
        print(f"Debug : input {name} with {best_match} and {score}")
        if score > 75:
            idx = self.known_names.index(best_match)
            return best_match,self.known_info[idx]
        else:
            print(f"Can't recognize {name}")
            return None



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

            label = f"{name} ({int(score * 100)}%)"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if name != "Unknown" and info:
                info_str = str(info.get('role', ''))
                cv2.putText(frame, info_str, (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

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
