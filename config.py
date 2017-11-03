
import os.path
import json
import csv

config={}

########## Files Config

config['path'] = 'videos/2017_10_25/006/'

############

config['filename'] = config['path'] + 'config.json'
config['video0'] = config['path'] + 'top.avi'
config['video1'] = config['path'] + 'world.mp4'
config['timestamps0'] = config['path'] + 'top_timestamps.csv'
config['timestamps1'] = config['path'] + 'world_timestamps.npy'
config['startStamp0'] = 0
config['startStamp1'] = 0
config['calibration'] = 'calibration.npz'
config['calibrationInvMap'] = 'calibrationInvMap.npy'
config['persistentModel'] = 'persistentModel'
config['proceduralTask'] = 'proceduralTask'

######## Load from JSON

def loadExternal(fileName,key):

    if not os.path.isfile(fileName):
        print('file not existent notthing loaded')
    else: 
        data_file = open(fileName, 'r+')   
        json_content= json.load(data_file)
        return json_content[key] 

loadlist = ['startStamp0','startStamp1','persistentModel','proceduralTask'] 

for key in loadlist:
    config[key] = loadExternal(config['filename'],key)