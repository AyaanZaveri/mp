import asyncio
import websockets
import json
import pyautogui as pag
import numpy as np
import time

pag.PAUSE = 0

width, height = pag.size()

# Variable to store the last click time
last_click_time = 0

def identify_right_hand(handedness):
    for hand in handedness:
        for item in hand:
            if item['categoryName'] == "Right":
                return handedness.index(hand)
    return None

def identify_left_hand(handedness):
    for hand in handedness:
        for item in hand:
            if item['categoryName'] == "Left":
                return handedness.index(hand)
    return None

def move(x, y):
    pag.moveTo((1 - x) * width, y * height, tween=pag.easeOutQuad)

async def echo(websocket, path):
    global last_click_time # Make last_click_time accessible inside this function
    async for message in websocket:
        results = json.loads(message)
        index_finger = results["indexFinger"]
        middle_finger = results["middleFinger"]
        thumb = results["thumb"]
        handedness = results["handedness"]
        wrist = results["wrist"]

        right_hand_index = identify_right_hand(handedness)
        left_hand_index = identify_left_hand(handedness)
        
        if right_hand_index is not None:
            move(index_finger[right_hand_index]["x"], index_finger[right_hand_index]["y"])
        
        if left_hand_index is not None:
            if 0 <= left_hand_index < len(index_finger) and 0 <= left_hand_index < len(thumb):
                distance = ((index_finger[left_hand_index]["x"] - thumb[left_hand_index]["x"]) ** 2 + (index_finger[left_hand_index]["y"] - thumb[left_hand_index]["y"]) ** 2 + (index_finger[left_hand_index]["z"] - thumb[left_hand_index]["z"]) ** 2) ** 0.5
                print(distance)
                if distance < 0.05:
                    # Check if enough time has passed since the last click
                    current_time = time.time()
                    if current_time - last_click_time > 0.5: # Adjust the time threshold as needed
                        pag.click()
                        last_click_time = current_time # Update the last click time
            
                distance = np.sqrt((middle_finger[left_hand_index]["x"] - index_finger[left_hand_index]["x"])**2 +
                                (middle_finger[left_hand_index]["y"] - index_finger[left_hand_index]["y"])**2)

                if distance < 0.04:
                    if middle_finger[left_hand_index]["y"] > wrist[left_hand_index]["y"]:
                        pag.scroll(-1)
                    elif middle_finger[left_hand_index]["y"] < wrist[left_hand_index]["y"]:
                        pag.scroll(1)

start_server = websockets.serve(echo, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
