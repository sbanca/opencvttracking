
import os.path
import json

config={}

########## Files Config

config['generalPath'] = 'D:/Dropbox/HCI project/videos/'
config['path'] = config['generalPath'] + '2017_11_24/001/'
config['trialNumber'] = 3

############

config['filename'] = config['path'] + 'config.json'
config['trialname'] = 'trial' + str(config['trialNumber'])
config['video0'] = config['path'] + 'top.avi'
config['video1'] = config['path'] + 'world.mp4'
config['startStamp0'] = 0
config['startStamp1'] = 0
config['timestamps0'] = config['path'] + 'top_timestamps.csv'
config['timestamps1'] = config['path'] + 'world_timestamps.npy'
config['calibration'] = 'calibration.npz'
config['calibrationInvMap'] = 'calibrationInvMap.npy'
config['persistentModel'] = {}
config['proceduralTask'] = {}
config['modelAndTaskJsonFile'] = config['generalPath'] + 'blocksAndTask.json'

######## Load from JSON

def loadExternal(fileName,key):

    if not os.path.isfile(fileName):
        print('file not existent notthing loaded')
    else: 
        data_file = open(fileName, 'r+')   
        json_content= json.load(data_file)
        return json_content[key] 

config[config['trialname']] = loadExternal(config['filename'],config['trialname'])

loadlist = ['persistentModel4','proceduralTask4','persistentModel8','proceduralTask8'] 
for key in loadlist: config[key] = loadExternal(config['modelAndTaskJsonFile'],key)

##################

config['startStamp0'] = config[config['trialname']]['startStamp0']
config['startStamp1'] = config[config['trialname']]['startStamp1']
config['stopStamp1'] = config[config['trialname']]['stopStamp1']
config['exportName'] = str(config['startStamp1']) + '-' + str(config['stopStamp1'])

#Load persistent model based on trail numberOfBlocks
####################################################

if config[config['trialname']]['numberOfBlocks'] == 8: 
    config['persistentModel'] = config['persistentModel8']
    config['proceduralTask'] = config['proceduralTask8']
    config['BinList'] =  ['first','second','third','fourth','fifth','sixth','seventh','eight']
    config['wAreaList'] = ['areaFirst','areaSecond','areaThird','Model'] 

elif config[config['trialname']]['numberOfBlocks'] == 4: 
    config['persistentModel'] = config['persistentModel4']
    config['proceduralTask'] = config['proceduralTask4']
    config['BinList'] =['first','second','fifth','sixth']
    config['wAreaList'] = ['areaFirst','areaSecond','Model'] 

