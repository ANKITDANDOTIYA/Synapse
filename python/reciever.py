import cv2 as cv
import numpy as np
import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt_string(zmq.SUBSCRIBE, '')

print("Receiver started, waiting for frames...")

while True:
    try :
        print("Waiting for data...", end='\r')
        packet = socket.recv() # Packet pakdo
        print(f"Recieved packet of size :{len(packet)}")
        np_arr = np.frombuffer(packet, dtype=np.uint8) # Bytes -> Array
         # 'imdecode' use karna hai
        frame = cv.imdecode(np_arr, cv.IMREAD_COLOR)
         # Frame dikhana hai
        if frame is  None:
            print("Frame is null ")
        else:
            print("Frame is not null ")
            cv.imshow("RECEIVER (Python)", frame)
            cv.waitKey(1)
            
        if cv.waitKey(1) == ord('q'): break
    except Exception as e:
           print("Error receiving frame:", e)
