# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 12:40:56 2021

@author: amkulk@udel.edu (Abhijeet Kulkarni)
"""

import cv2
filepath = 'wolf.mp4'

# helping functions
def DrawBoundingBox(frame,bbox,color= (255,0,0),thickness=2):
    (x, y, w, h) = [int(d) for d in bbox]
    cv2.rectangle(frame, (x,y), (x+w,y+h),color,thickness)

def GetBoxCenter(bbox):
    if bbox == None:
        return None
    (x, y, w, h) = [int(d) for d in bbox]
    return (x+w//2,y+w//2)

def CropFrame(frame,composition=None,currentObjCenter=None):
    global objCenter
    if composition is not None:
        (x, y, w, h) = [int(d) for d in composition]
        framepadded = cv2.copyMakeBorder(frame,h,h,w,w,cv2.BORDER_CONSTANT,None,0) # without padding overflows
        dx,dy=currentObjCenter[0]-objCenter[0],currentObjCenter[1]-objCenter[1]
        framecropped=framepadded[h+y+dy:h+y+h+dy,w+x+dx:w+x+dx+w]
    return framecropped
    

def DisplayImage(frame):
    global videoFPS
    cv2.imshow('video',frame)
    key = cv2.waitKey(int(1000/videoFPS)) & 0xFF
    return key

def WriteVideo(frame,out):
    global videoFPS
    dim = frame.shape[:2] #[height,width]
    if out is None:
        out = cv2.VideoWriter("TrackedVideo.mp4",cv2.VideoWriter_fourcc(*'XVID'), videoFPS, (dim[1],dim[0]))
    out.write(frame)
    return out

video=cv2.VideoCapture(filepath)
videoFPS= video.get(cv2.CAP_PROP_FPS)
OPENCV_OBJECT_TRACKERS = {
          "csrt": cv2.TrackerCSRT_create(),
          "kcf": cv2.TrackerKCF_create(),
          "mil": cv2.TrackerMIL_create(),
    }

tracker = OPENCV_OBJECT_TRACKERS['csrt'] 
tracking = None
composition = None
success = True
objCenter = None
videowriter = None

while True:
    video_incoming, frame = video.read()
    if video_incoming:
        if tracking is not None:
            (success,tracking) = tracker.update(frame)
            if success:
                DrawBoundingBox(frame, tracking) #comment this for suppressing blue box
                frameCropped = CropFrame(frame,composition,GetBoxCenter(tracking))
                key = DisplayImage(frameCropped)
                
                videowriter=WriteVideo(frameCropped,videowriter)
            else:
                key = DisplayImage(frame)
        else:

            key = DisplayImage(frame)
            
        if key == ord("s") or success == False: #select ROI
            tracking = cv2.selectROI("Select ROI",frame,fromCenter=False,showCrosshair=True)
            tracker.init(frame,tracking)
            cv2.destroyAllWindows()
            if composition == None:
                DrawBoundingBox(frame, tracking)
                objCenter=GetBoxCenter(tracking)
                composition = cv2.selectROI("Select Composition",frame,fromCenter=False,showCrosshair=True)
                cv2.destroyAllWindows()
        
        elif key == ord("q"): #stop video
            break
        
        elif key == ord("f"): #skipping 1 sec
            _=[video.read() for i in range (1000/videoFPS)]
        
        
            
        
    else:
        
        break
print("Done")
video.release()
videowriter.release()
cv2.destroyAllWindows()