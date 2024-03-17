import time
import cv2
import numpy as np
import mediapipe as mp
import pyautogui as pag

mp_hands = mp.solutions.hands.Hands()
hand_landmarks = mp.solutions.hands.HandLandmark

mpDraw = mp.solutions.drawing_utils
# draw circle on articulation point (關節點)
handLmsStyle = mpDraw.DrawingSpec(color=(0, 0, 255), thickness=5)
# draw line between articulation point
handConStyle = mpDraw.DrawingSpec(color=(0, 255, 0), thickness=10)

def move(landmarks, handedness):
    if (handedness == "Left"):
        index = landmarks[hand_landmarks.INDEX_FINGER_TIP]
        width, height = pag.size()
        x = index.x * width
        y = index.y * height
        
        pag.moveTo(x, y)
    
def click(landmarks, handedness):
    if (handedness == "Right"):
        index = landmarks[hand_landmarks.INDEX_FINGER_TIP]
        thumb = landmarks[hand_landmarks.THUMB_TIP]
    
        distance = np.sqrt((index.x - thumb.x)**2 +
                            (index.y - thumb.y)**2)
        
        if distance < 0.05:
            pag.click()

def scroll(landmarks, handedness):
    if handedness == "Right":
        middle_finger_tip = landmarks[hand_landmarks.MIDDLE_FINGER_TIP]
        index_tip = landmarks[hand_landmarks.INDEX_FINGER_TIP]
        wrist = landmarks[hand_landmarks.WRIST]

        distance = np.sqrt((middle_finger_tip.x - index_tip.x)**2 +
                           (middle_finger_tip.y - index_tip.y)**2)

        if distance < 0.06:
            if middle_finger_tip.y > wrist.y:
                pag.scroll(-2)
            elif middle_finger_tip.y < wrist.y:
                pag.scroll(2)

def main():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        results = mp_hands.process(frame)
        
        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                mpDraw.draw_landmarks(frame, landmarks, mp.solutions.hands.HAND_CONNECTIONS, handLmsStyle, handConStyle)
                handedness = results.multi_handedness[results.multi_hand_landmarks.index(landmarks)].classification[0].label
                
                move(landmarks.landmark, handedness)
                scroll(landmarks.landmark, handedness)
                click(landmarks.landmark, handedness)
                    

        if cv2.waitKey(1) == ord('q'):
            break

        cv2.imshow("frame", frame)
    
    hand_landmarker.close()
    cap.release()
    cv2.destroyAllWindows()
    


if __name__ == "__main__":
    main()
