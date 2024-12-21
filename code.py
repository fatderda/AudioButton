import time
import digitalio
import board
import rotaryio
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# init Keyboard
kbd = Keyboard(usb_hid.devices)

# Rotary encoder
enc = rotaryio.IncrementalEncoder(board.GP26, board.GP27)
encSw = digitalio.DigitalInOut(board.GP28)
encSw.direction = digitalio.Direction.INPUT
encSw.pull = digitalio.Pull.UP
lastPosition = 0
 
# USB device
consumer = ConsumerControl(usb_hid.devices)

# button delay
dl = 0.2

# long press
longPressDelay = 0.5
encSwReleased = True

# next previous controls and delay
pressInterval = 0.3
pressedCount = 0
firstPressTime = None

# loop
while True:
    # poll encoder position
    position = enc.position
    if position != lastPosition: 
        if lastPosition < position:
            consumer.send(ConsumerControlCode.VOLUME_INCREMENT)
        else:
            consumer.send(ConsumerControlCode.VOLUME_DECREMENT)
        lastPosition = position 
    
    # poll encoder button
    currentTime = time.monotonic()
    if encSw.value == 0:
        #avoid multiple executions from one press
        if encSwReleased:
            encSwReleased = False
            pressedCount += 1
            
            if pressedCount == 1:
                firstPressTime = currentTime
            
            longPressHandled = False

            # check long press
            if not longPressHandled and pressedCount == 1 and currentTime - firstPressTime >= longPressDelay:
                # send WIN and 7 to open Spotify (or whatever app is at this position in taskbar)
                kbd.press(Keycode.WINDOWS) 
                kbd.press(Keycode.SEVEN) 
                kbd.release(Keycode.WINDOWS)
                kbd.release(Keycode.SEVEN)
                print("long press");
                longPressHandled = True   
                pressedCount = 0
    else:
        encSwReleased = True
        
    # handle multipress 
    if pressedCount > 0 and firstPressTime is not None:
        elapsedTime = currentTime - firstPressTime
        if elapsedTime > pressInterval:
            if pressedCount == 1: 
                consumer.send(ConsumerControlCode.PLAY_PAUSE)
                print("single press - play/pause")
            elif pressedCount == 2: 
                consumer.send(ConsumerControlCode.SCAN_NEXT_TRACK)
                print("double press - next")
            elif pressedCount == 3: 
                consumer.send(ConsumerControlCode.SCAN_PREVIOUS_TRACK)
                print("triple press - previous")
            pressedCount = 0  
            firstPressTime = None
    time.sleep(0.1)