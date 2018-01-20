import os.path
import json
import cv2

config = {}
config['path'] = 'D:/Dropbox/HCI project/videos/2017_12_01/003/'
config['filename'] = config['path'] + 'config.json'
config['video0'] = config['path'] + 'top.avi'
config['video1'] = config['path'] + 'world.mp4'

#load the exported trial folders list
list_of_exported_trials = os.listdir(config['path']+'/exports/')
#print( 'export list: ' + str(list_of_exported_trials) )

#load video 1 and apporx count frames
video0 = cv2.VideoCapture(config['video0'] )
video0Frames = int(video0.get(cv2.CAP_PROP_FRAME_COUNT))
#print( 'video0 frames: ' + str(video0Frames) )

#load video 1 and apporx count frames
video1 = cv2.VideoCapture(config['video1'] )
video1Frames = int(video1.get(cv2.CAP_PROP_FRAME_COUNT))
#print( 'video1 frames: ' + str(video1Frames) )

#calculate approx ratio
ratio = video0Frames/video1Frames

#create object variable to collect trials
trials = {}

#Trial list creation
for idx,folder in enumerate(list_of_exported_trials):
    key = 'trial'+str(idx+1)
    startStop = str.split(folder, '-' )
    trial = {}
    trial['startStamp0'] = int(int(startStop[0]) * ratio)
    trial['startStamp1'] = int(startStop[0])
    trial['stopStamp1'] = int(startStop[1])
    trial['numberOfBlocks'] = 'set int please'
    trial['instructions'] = 'set bool please'
    trials[key] = trial

#print(trials)

#open loading and closing file in reading mode
data_file = open(config['filename'], 'r+')   
existingDict = json.load(data_file)
data_file.close()

for key in trials: existingDict[key] = trials[key] 

#open file in writing mode 
data_file =  open(config['filename'], 'w')  
json.dump( existingDict , data_file,  indent=5)
data_file.close()
