import os
import json
import cv2

config = {}
config['path'] = 'D:/Dropbox/HCI project/videos/'

for root, dirs, files in os.walk(config['path']):  
    for name in files:
        if name.endswith(("config.json")):

            filename = root + "\\config.json"

            #open loading and closing file in reading mode
            data_file = open(filename, 'r+')   
            existingDict = json.load(data_file)
            data_file.close()

            if 'persistentModel' in existingDict: del existingDict['persistentModel'] 
            if 'proceduralTask' in existingDict: del existingDict['proceduralTask'] 

            #open file in writing mode 
            data_file =  open(filename, 'w')  
            json.dump( existingDict , data_file,  indent=5)
            data_file.close()
