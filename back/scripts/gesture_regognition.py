import cv2
import mediapipe as mp
from cloud_api import text_to_speech, \
text_detect, object_detect, speech_to_prompt, \
VISION_FILE, SPEECH_FILE

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode
global options
options = GestureRecognizerOptions(
    base_options=BaseOptions(
        model_asset_path='/Resources/gesture_recognizer.task'),
    running_mode=VisionRunningMode.IMAGE,
    min_hand_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    num_hands=1)

def action(gesture, frame):
    if gesture == 'ILoveYou':
        print(gesture)
        return speech_to_prompt(SPEECH_FILE)
    elif gesture == 'Pointing_Up':
        print(gesture)
        cv2.imwrite(VISION_FILE, frame)
        return text_to_speech(object_detect())
    elif gesture == 'Closed_Fist':
        print(gesture)
        cv2.imwrite(VISION_FILE, frame)
        return text_to_speech(text_detect())

# Main Loop
def main():
    cap = cv2.VideoCapture(1)
    with GestureRecognizer.create_from_options(
            options) as recognizer:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue
            #mark the image as not writeable to pass by reference.
            frame.flags.writeable = False
            rgb_frame = frame
            results = recognizer.recognize(
                mp.Image(image_format=mp.ImageFormat.SRGB, 
                data=rgb_frame))
            if results.gestures:
                gesture_name = results.gestures[0][0].category_name
                if gesture_name != 'None':
                    action(gesture_name, frame)
                else:
                    print(gesture_name)
            cv2.imshow('Gesture Recognition', rgb_frame)            
                # Exit when 'esc' is pressed
            if  cv2.waitKey(10) & 0xff == 27: 
                break
    # Release the video capture object and close the OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
