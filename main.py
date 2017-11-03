####external
import cv2

####internal
import cvWrapper as cvW
from cvWrapper import Timestamp
import interfaceWrapper as intWr
from config import config
from cvWobjects import Masks,Trims, bckSub, Thresh, Bins, wAreas, Blocks, GazePositions, perspective, OrgRect

def main():
    
    cap0 = cv2.VideoCapture(config['video0'])
    cap1 = cv2.VideoCapture(config['video1'])
    
    Blocks.config(AreaTopBound = {'interface':False},
                  AreaBottomBound={'interface':False},
                  B2x1 = {'interface':False},
                  B2x2 = {'interface':False},
                  B2x4 = {'interface':False},
                  time = {'interface':True},
                  blocchi = {'interface':True},
                  task = {'interface':True},
                  testGraph = {'interface':True})

    newWindow = intWr.interface()

    newWindow.config(obj=Blocks,
                     pipelines=['TopCamera','eyetrack'],
                     media=[cap0,cap1],
                     timestamps=[config['timestamps0'],config['timestamps1']],
                     startStamps=[config['startStamp0'],config['startStamp1']])

    newWindow.initialise()

    newWindow.create()

main()

def live():
    
    cap0 = cv2.VideoCapture(config['video0'])
    
    Main = cvW.base('Main')
    Main.config(name='Main', saveButton = {'interface':True,'widget':'button','command':'saveobject'})

    newWindow = intWr.interface()

    newWindow.config(obj=Blocks,
                     pipelines=['TopCamera'],
                     media=[cap0])

    newWindow.initialise()

    newWindow.create()

#live()

def eyetracker():
    
    cap1 = cv2.VideoCapture(config['video1'])

    Main = cvW.base('Main')
    Main.config(name='Main', saveButton = {'interface':True,'widget':'button','command':'saveobject'})

    newWindow = intWr.interface()

    newWindow.config(obj=Main,
                     pipelines=['Eyetrack2'],
                     media=[cap1],
                     timestamps=[config['timestamps1']],
                     timeStampKey=['video1'],
                     startStamps=[config['startStamp1']])

    newWindow.initialise()

    newWindow.create()

#eyetracker()

def configurationeyetracker():

    cap = cv2.VideoCapture(config['video1'])

    ##### 1 CONFIG TRIM
    #################

    # newWindow = intWr.interface()
    # newWindow.config(obj=Trims['Trim2'],
    #                  timestamps=[config['timestamps1']],
    #                  timeStampKey=['video1'],
    #                  startStamps=[config['startStamp1']],
    #                  pipelines=['eyetrackConfig'],
    #                  media=[cap])

    # newWindow.initialise()
    # newWindow.create()

    ##### 1 CONFIG TARGETS DETECTION
    #################

    newWindow = intWr.interface()
    newWindow.config(obj=perspective,
                     timestamps=[config['timestamps1']],
                     timeStampKey=['video1'],
                     startStamps=[config['startStamp1']],
                     pipelines=['eyetrackConfig'],
                     media=[cap])

    newWindow.initialise()
    newWindow.create()

configurationeyetracker()

def configurationTopCamera():

    cap = cv2.VideoCapture(config['video0'])
    
    ##### 1 CONFIG TRIM
    #################

    # newWindow = intWr.interface()
    # newWindow.config(obj=Trims['Trim'],pipelines=['TrimWarp'],media=[cap]) 
    # newWindow.initialise()
    # newWindow.create()
        
    ##### 2 ORIGRECT used for the eyetracker perspective transformations
    #################

    newWindow = intWr.interface()  
    newWindow.config(obj=OrgRect,pipelines=['OrgRect'],media=[cap]) 
    newWindow.initialise()
    newWindow.create()

    ##### 3 BINS CONFIG
    #################

    # windows={}

    # for binname in Bins:
    #     windows[binname] = intWr.interface()
    #     windows[binname].config(obj=Bins[binname],pipelines=['Bins'],media=[cap])
    #     windows[binname].initialise()
    #     windows[binname].create()
    
    ##### 4 AREAS CONFIG
    #################

    # windows={}
    
    # for wArea in wAreas:
    #     windows[wArea] = intWr.interface()
    #     windows[wArea].config(obj=wAreas[wArea],pipelines=['wAreas'],media=[cap])
    #     windows[wArea].initialise()
    #     windows[wArea].create()
    
    ##### 5 MASKS CONFIG
    #################

    windows={}

    pipelineMasks = ['pipelineBlue','pipelineRed','pipelineGreen','pipelineYellow','pipelineHand']

    for idx,maskKey in enumerate(Masks):
        windows[maskKey] = intWr.interface()
        windows[maskKey].config(obj=Masks[maskKey],pipelines=[pipelineMasks[idx]],media=[cap])
        windows[maskKey].initialise()
        windows[maskKey].create()

    ##### 6 BLOCK SIZES CONFIG
    #################

    # newWindow = intWr.interface()

    # Blocks.config(AreaTopBound = {'interface':True},
    #               AreaBottomBound={'interface':True},
    #               B2x1 = {'interface':True},
    #               B2x2 = {'interface':True},
    #               B2x4 = {'interface':True},
    #               time = {'interface':True},
    #               blocchi = {'interface':False},
    #               task = {'interface':False})
    
    # newWindow.config(obj=Blocks,pipelines=['TopCamera'],media=[cap]) 
    # newWindow.initialise()
    # newWindow.create()
    
    #### 7 CONFIGURE EXPECTED BLOCKS AND TASKS
    ########################## 
    ###### configure 'ExpectedBlocks' in the config.json file 
    ###### configure 'Tasks' in the config.json file 
    ############################
    
    # Blocks.config(AreaTopBound = {'interface':False},AreaBottomBound={'interface':False},
    #               B2x1 = {'interface':False},B2x2 = {'interface':False},B2x4 = {'interface':False},
    #               time = {'interface':True},blocchi = {'interface':True},task = {'interface':True})

    # newWindow = intWr.interface()

    # newWindow.config(obj=Blocks,pipelines=['TopCamera'],media=[cap],timestamps=[config['timestamps0']],startStamps=[config['startStamp0']])

    # newWindow.initialise()
    # newWindow.create()

    ####OTHERS
    # newWindow.config(obj=bckSub['bckSub'],pipelines=['bckSub','BGR2RGB'],media=[cap,cap])
    # newWindow.config(obj=Thresh['one'],pipelines=['thresh'],media=[cap])

#configurationTopCamera()

def synchcronize():
    
    cap0 = cv2.VideoCapture(config['video0'])
    cap1 = cv2.VideoCapture(config['video1'])
    
    Main = cvW.base('Main')
    Main.config(name='Main', saveButton = {'interface':True,'widget':'button','command':'saveobject'})

    newWindow = intWr.interface()

    newWindow.config(obj=Main,
                     pipelines=['syncTopCamera','syncEyetrack'],
                     media=[cap0,cap1],
                     timestamps=[config['timestamps0'],config['timestamps1']],
                     startStamps=[config['startStamp0'],config['startStamp1']])

    newWindow.initialise()

    newWindow.create()

#synchcronize()



