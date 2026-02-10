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


class Vision_Pro:
    def __init__(self):  # init constructor hai
        print('Initializing Vision Pro Engine...')
        self.yolo = YOLO('yolov8n.pt')  # self == this
        self.is_running = True

        self.app = FaceAnalysis(
            name='buffalo_s', # l ki jarurat nahi hai s se bhi kaam ho jayega mera
            root='C:/Users/priya/.insightface',
            providers=['CUDAExecutionProvider']
        )
        # buffallo_l model use kar raha hai agar cuda available hai to use karega nahi to CPU

        self.app.prepare(ctx_id=0, det_size=(640, 640))
        # app ka object ban gya ab engine start karna prepare se ctx_id mtlb jo provider
        # diya hai usme se 0th index wala use karega.

        self.conn = sqlite3.connect('vision_pro.db', check_same_thread=False)
        # conn naam ka obj banaya ab ye database se connect karega vision_pro.db file se

        self.cursor = self.conn.cursor()
        # conn bridge hai jaha se hum databse jayenge but cursor is the gaurd jo queries ko execute karega

        self.setup_db()
        # database setup karne ke liye function call kiya

        self.known_names = []  # same as arrayList or vector naaam ke liye
        self.known_embeddings = []  # embeddings mtlb chehre ke features store karega
        self.known_info = []  # uska info store karega jaise role etc
        self.load_memory()  # function call kiya memory load karne ke liye

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
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
        # --- ⏳ HELPER: Bolne ka wait karo, fir user ko time do ---
        def speak_and_wait(text, wait_for_user_seconds=0):
            if tts_engine:
                tts_engine.speak(text)
                time.sleep(0.5)  # Thread start hone ka chhota buffer
                # Jab tak Sarah bol rahi hai, code yahi roka rahega
                while hasattr(tts_engine, '_is_speaking') and tts_engine._is_speaking:
                    time.sleep(0.1)
            else:
                print(f"[TTS MISSING]: {text}")

            # Ab Sarah chup hai, User ko time do move karne ka
            if wait_for_user_seconds > 0:
                print(f"Waiting {wait_for_user_seconds}s for user action...")
                time.sleep(wait_for_user_seconds)

        # ---------------------------------------------------------

        # 1. FRONT FACE (Jo frame pass hua hai use hi use kar lo)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.app.get(rgb_frame)

        if len(faces) == 0:
            print(f'No faces detected')
            speak_and_wait("I can't see your face. Please look at the camera.", 0)
            return False

        speak_and_wait("Hold on, capturing front view.", 0)

        # Capture Front
        face_straight = sorted(faces, key=lambda x: x.bbox[2] * x.bbox[3])[-1]
        embedding_straight = face_straight.embedding

        # 2. LEFT FACE
        speak_and_wait("Now turn your face slightly to the left.", wait_for_user_seconds=3)

        ret, frame_left = self.cap.read()  # Ab photo lo
        if not ret: return False

        rgb_left = cv2.cvtColor(frame_left, cv2.COLOR_BGR2RGB)
        faces_left = self.app.get(rgb_left)

        if len(faces_left) == 0:
            speak_and_wait("Face not found in left view, using front view instead.", 0)
            embedding_left = embedding_straight  # Fallback
        else:
            face_left_obj = sorted(faces_left, key=lambda x: x.bbox[2] * x.bbox[3])[-1]
            embedding_left = face_left_obj.embedding

        # 3. RIGHT FACE
        speak_and_wait("Now turn slightly to the right.", wait_for_user_seconds=3)

        ret, frame_right = self.cap.read()
        if not ret: return False

        rgb_right = cv2.cvtColor(frame_right, cv2.COLOR_BGR2RGB)
        faces_right = self.app.get(rgb_right)

        if len(faces_right) == 0:
            speak_and_wait("Face not found in right view, using front view instead.", 0)
            embedding_right = embedding_straight  # Fallback
        else:
            face_right_obj = sorted(faces_right, key=lambda x: x.bbox[2] * x.bbox[3])[-1]
            embedding_right = face_right_obj.embedding

        # 4. SMILE (Optional but Good)
        speak_and_wait("Okay, now look at the camera and give me a big smile.", wait_for_user_seconds=2)

        ret, frame_smile = self.cap.read()
        embedding_smile = embedding_straight  # Default fallback
        if ret:
            rgb_smile = cv2.cvtColor(frame_smile, cv2.COLOR_BGR2RGB)
            faces_smile = self.app.get(rgb_smile)
            if len(faces_smile) > 0:
                face_smile_obj = sorted(faces_smile, key=lambda x: x.bbox[2] * x.bbox[3])[-1]
                embedding_smile = face_smile_obj.embedding

        # --- DATABASE INSERTION ---
        json_info = json.dumps(info_dict)

        # Binary convert
        binary_enc_straight = pickle.dumps(embedding_straight)
        binary_enc_left = pickle.dumps(embedding_left)
        binary_enc_right = pickle.dumps(embedding_right)
        binary_enc_smile = pickle.dumps(embedding_smile)

        # 4 Rows Insert karo (Front, Left, Right, Smile)
        query = "INSERT INTO humans (name, embedding, info) VALUES (?, ?, ?)"
        self.cursor.execute(query, (name, binary_enc_straight, json_info))
        self.cursor.execute(query, (name, binary_enc_left, json_info))
        self.cursor.execute(query, (name, binary_enc_right, json_info))
        self.cursor.execute(query, (name, binary_enc_smile, json_info))

        self.conn.commit()

        # Update Memory
        self.known_embeddings.extend([embedding_straight, embedding_left, embedding_right, embedding_smile])
        self.known_names.extend([name, name, name, name])
        self.known_info.extend([info_dict, info_dict, info_dict, info_dict])

        speak_and_wait(f"Done! I have successfully registered {name}.", 0)
        print(colorama.Fore.GREEN + f"[Vision] Registered new face: {name} (4 Angles)")
        return True

    # --- 🛠️ HELPER FUNCTIONS (NOW CORRECTLY INDENTED) ---

    def check_person_exists(self, name):
        """Check if person exists and return their current info"""
        try:
            # Case-insensitive search
            self.cursor.execute("SELECT info FROM humans WHERE name LIKE ?", (name,))
            row = self.cursor.fetchone()
            if row:
                return json.loads(row[0])  # Return Info Dict
            return None
        except Exception:
            return None

    def update_person_info(self, name, new_info_dict):
        """Updates only the info, keeps the face data"""
        try:
            json_info = json.dumps(new_info_dict)
            # Update all entries for this name (Front, Left, Right etc.)
            self.cursor.execute("UPDATE humans SET info = ? WHERE name LIKE ?", (json_info, name))
            self.conn.commit()

            # Memory list update
            self.load_memory()  # Reload DB to RAM (Corrected function name)
            return True
        except Exception as e:
            print(f"Update Error: {e}")
            return False

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

                if max_score > 0.4:
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

    def close_camera(self):
        # 1. Pehle loop ko roko (Agar thread chal raha hai)
        self.is_running = False

        # 2. Thoda saans lene do taaki last frame process ho jaye
        time.sleep(0.1)

        # 3. Ab camera resource release karo
        if self.cap.isOpened():
            self.cap.release()

        # 4. Windows udao
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        print("Camera Resource Released.")

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

    def get_info(self, name_query):
        """
        Retrieves info from DB using Smart/Fuzzy Matching.
        Agar user 'Ankit' bole aur DB me 'Ankit Dandotia' ho, to bhi pakad lega.
        """
        try:
            # 1. Pehle EXACT match try karo (Fastest)
            self.cursor.execute("SELECT name, info FROM humans WHERE name LIKE ?", (name_query,))
            row = self.cursor.fetchone()

            if row:
                return row[0], json.loads(row[1])

            # 2. Agar Exact nahi mila, to PARTIAL match try karo
            # Example: name_query="Ankit" -> Dhoondo jiske naam me "Ankit" aata ho
            pattern = f"%{name_query}%"
            self.cursor.execute("SELECT name, info FROM humans WHERE name LIKE ?", (pattern,))
            row = self.cursor.fetchone()

            if row:
                # DB wala full name return karo (e.g., 'Ankit Dandotia')
                print(f"[DB] Partial match found: '{name_query}' -> '{row[0]}'")
                return row[0], json.loads(row[1])

            # 3. DEBUG: Agar kuch nahi mila to batao DB me kya hai
            print(f"[DB] '{name_query}' not found. Dumping all names in DB for check:")
            self.cursor.execute("SELECT DISTINCT name FROM humans")
            all_names = self.cursor.fetchall()
            print([n[0] for n in all_names])

            return None

        except Exception as e:
            print(f"DB Error: {e}")
            return None


if __name__ == "__main__":
    v = Vision_Pro()

    # Note: cap yahan define karne ki zarurat nahi hai agar class ke andar already self.cap hai.
    # Lekin agar aapko loop yahan chalana hai to 'v.cap' use karein ya naya banayein.

    print("Press 'r' to register yourself, 'q' to quit")

    while True:
        # Class wala camera use karte hain taaki conflict na ho
        ret, frame = v.cap.read()
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

            # NOTE: Yahan 'None' pass kiya hai kyunki main loop me 'tts_engine' nahi hai.
            # Agar real usage me TTS chahiye, to tts_engine ka object pass karna padega.
            v.register_face(frame, my_name, info_data, None)
    v.close_camera()