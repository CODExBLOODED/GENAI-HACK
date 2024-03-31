from flask import Flask, jsonify
from flask_cors import CORS
import cv2
import mediapipe as mp
import math

app = Flask(__name__)
CORS(app)

NUM_LANDMARKS = 21
# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands

# Initialize MediaPipe Drawing module for drawing landmarks
mp_drawing = mp.solutions.drawing_utils

# Open a video capture object (0 for the default camera)
cap = cv2.VideoCapture(0)
distances = ()
fingers = ('thumb_index', 'thumb_middle')
frame_count = 0
action_delay = 3

@app.route('/api/data', methods=['GET'])
def get_data():
    with mp_hands.Hands(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7) as hands:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue
            if frame_count % 2 == 0:
                #mark the image as not writeable to pass by reference.
                frame.flags.writeable = False
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                rgb_frame = frame
                results = hands.process(rgb_frame) ####CHANGE TO RGB FRAME

                # Check if hands are detected
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        landmarks = hand_landmarks.landmark
                        hand = landmarks[5]
                        palm = landmarks[0]
                        f_thumb = landmarks[4]
                        f_index = landmarks[8]
                        f_middle = landmarks[12]

                        hand_size_metric = math.sqrt((hand.x-palm.x)**2 + (hand.y-palm.y)**2 + (hand.z-palm.z)**2)
                        thumb_index = math.sqrt((f_thumb.x-f_index.x)**2 + (f_thumb.y-f_index.y)**2 + (f_thumb.z-f_index.z)**2)/hand_size_metric
                        thumb_middle = math.sqrt((f_thumb.x-f_middle.x)**2 + (f_thumb.y-f_middle.y)**2 + (f_thumb.z-f_middle.z)**2)/hand_size_metric
                        action_delay-=1

                cv2.imshow('Hand Recognition', rgb_frame)
            frame_count += 1

            # Exit when 'esc' is pressed
            if cv2.waitKey(10) & 0xff == 27: 
                break

    # Release the video capture object and close the OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

    data = {"key": "value"}  # Replace with your actual data
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
    print("Connected to the server and connected with the React application")
