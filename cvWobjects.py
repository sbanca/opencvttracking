import cvWrapper as cvW
from config import config 

# initialise masks
####################

Masks = {}

Masks['Blue Mask'] = cvW.HSVMask('Blue Mask')
Masks['Blue Mask'].dictToJson(config['filename'],mode='load')

Masks['Red Mask'] = cvW.HSVMask('Red Mask')
Masks['Red Mask'].dictToJson(config['filename'],mode='load')

Masks['Green Mask'] = cvW.HSVMask('Green Mask')
Masks['Green Mask'].dictToJson(config['filename'],mode='load')

Masks['Yellow Mask'] = cvW.HSVMask('Yellow Mask')
Masks['Yellow Mask'].dictToJson(config['filename'],mode='load')

Masks['Hand'] = cvW.HSVMask('Hand')
Masks['Hand'].dictToJson(config['filename'],mode='load')


# initialise trims
####################

Trims = {}

Trims['Trim'] = cvW.trimmer('Trim')
Trims['Trim'].dictToJson(config['filename'],mode='load')
Trims['Trim'].initialise()

Trims['Trim2'] = cvW.trimmer('Trim2')
Trims['Trim2'].dictToJson(config['filename'],mode='load')
Trims['Trim2'].initialise()


# initialise Background Subtraction
###################################

bckSub = {}

bckSub['bckSub'] = cvW.bckSub('bckSub')
bckSub['bckSub'].dictToJson(config['filename'],mode='load')


# initialise thresh
###################################

Thresh = {}
Thresh['one'] = cvW.thresh('one')


#initialise Bins and workAreas and exclusionZones
#################################################

Bins = {}
BinList =  config['BinList']

for binname in BinList:
    Bins[binname] = cvW.binbox(binname)
    Bins[binname].dictToJson(config['filename'],mode='load')

wAreas = {}
wAreaList = config['wAreaList']

for wArea in wAreaList:
    wAreas[wArea] = cvW.binbox(wArea)
    wAreas[wArea].dictToJson(config['filename'],mode='load')

OrgRect = cvW.binbox('orgRect')
OrgRect.dictToJson(config['filename'],mode='load')

exclRect = cvW.binbox('exclRect')
exclRect.dictToJson(config['filename'],mode='load')


#Import Gaze positions
######################
GazePositions = cvW.eyeTrackerData('video1')
GazePositions.config(path=config['path'] +'exports/'+config['exportName']+'/',startstamp=0,key='video1')
GazePositions.initialise()


#Initialise Camera undistortion
###############################
Undistort = cvW.cameraUndistortion('undistort',config['calibration'],config['calibrationInvMap'])


#Initialise Perspective work
############################
perspective = cvW.perspective('perspective')
perspective.dictToJson(config['filename'],mode='load')
perspective.addOrgRect(OrgRect.returnPoints())
perspective.addBins([ Bins[key].returnPoints() for key in Bins])
perspective.addwAreas([ wAreas[key].returnPoints() for key in wAreas])
perspective.addGaze(GazePositions)


#initialiseBlocks
##################
Blocks = cvW.blocks('blocks')
Blocks.dictToJson(config['filename'],mode='load')
Blocks.addROI(Bins)
Blocks.addROI(wAreas)
Blocks.addGaze(perspective)
Blocks.addExclusion(exclRect)