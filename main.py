#!/usr/bin/env python


import freenect
import cv2
import frame_convert2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from PIL import ImageDraw
import keras

#setup pwm

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(12, GPIO.OUT)
servo = GPIO.PWM(12,50)

servo.start(0)

GPIO.setup(11, GPIO.OUT)
esc = GPIO.PWM(11,50)

esc.start(0)

global speed_esc
global speed_servo

def get_video(ind):
    return frame_convert2.video_cv(freenect.sync_get_video(ind)[0])
    
def get_depth(ind):
    return frame_convert2.pretty_depth_cv(freenect.sync_get_depth(ind)[0])


def main(img, depth):
    #get image

    print(img)
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    #cv2.imshow('img' , img)
    #cv2.waitKey()
    
    img = Image.fromarray(img, 'RGB')
    
    #img  = cv2.imdecode(img)
    
    #plt.imshow(img)
    #plt.show()
    
    print(img)
    
    #plt.imshow(img)
    #plt.show()
    
    #get model
    model = keras.models.load_model("./modle.h5")
    
    #scann image
    sizes = [200]
    step_size = 75
    
    humans = [] 
    print(img.size)
    for size in sizes:
        for x in range(0, img.size[0] - size, step_size):
            for y in range(0, img.size[1] - size, step_size):
                part = img.crop((x, y, x + size, y + size))
                data = np.asarray(part.resize((32, 32), resample=Image.BICUBIC))
                data = data.astype(np.float32) / 255.
                
                pred = model.predict(data.reshape(-1, 32, 32, 3))
                print(pred)
                if pred[0][0] > 0.07:
                    # print(pred[0][0])
                    humans.append((x, y, size))
                    
                    
    out = img.copy()
    draw = ImageDraw.Draw(out)
    
    humans_drawn = []
    
    for human in humans:
        exists = False
        for human_drawn in humans_drawn:
            if human[0] >= human_drawn[0] and human[0] <= human_drawn[0] + human_drawn[2]:
                if human[1] >= human_drawn[1] and human[1] <= human_drawn[1] + human_drawn[2]:
                    exists = True
                    
        if exists == False:
            points = [
                (human[0], human[1]),
                (human[0], human[1] + human[2]),
                (human[0] + human[2], human[1] + human[2]),
                (human[0] + human[2], human[1]),
                (human[0], human[1])
            ]
            draw.line(points, "yellow", 5)
            humans_drawn.append(human)
            print(human)
            
    #show klassified image
    #plt.imshow(out)
    #plt.show()
    
  
    #get stering from image
    try:
        #get and set stering PWM from image
        wantabile_human = humans_drawn[0]
        direction = 8 - (wantabile_human[0] * 0.00425)
        print(direction)
        if direction < 4 or direction > 8:
            direction = 7
            servo.ChangeDutyCycle(direction)
        servo.ChangeDutyCycle(direction)
        speed = 7
        #get and set throttle pwm
        wantabile_human = humans_drawn[0]
        x, y = [wantabile_human[0] + (wantabile_human[2] / 2), wantabile_human[1] + (wantabile_human[2] / 2)]
        ditance = depth[int(x), int(y)]
        if ditance > 10:
            if speed < 2 or speed > 7:
                speed = 7
                esc.ChangeDutyCycle(speed)
            speed = speed - 0.5
            print(speed)
            esc.ChangeDutyCycle(speed)
        else:
            if speed < 2 or speed > 7:
                speed = 7
                esc.ChangeDutyCycle(speed)
            speed =  speed + 0.2
            print('else', speed)
            esc.ChangeDutyCycle(speed)
            
        
    #if shit goes wrong
    except:
        print('shit went wrong')
        direction = 6.
        print(direction)
        servo.ChangeDutyCycle(direction)
        
        speed = 7
        print(speed)
        esc.ChangeDutyCycle(speed)
        
    time.sleep(0.25)
    esc.ChangeDutyCycle(0)
inde = 1
while True:
    try:
        depth = get_depth(inde)
        img = get_video(inde)
        main(img, depth)
    #time.sleep(2)
    except TypeError:
        inde = 0
        continue
    inde = inde + 1
    print(str(inde))