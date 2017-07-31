
import cv2
import cvWrapper as cvW
import numpy as np



# initialise masks
####################

Masks = {}

Masks['Blue Mask'] = cvW.HSVMask('Blue Mask')
Masks['Blue Mask'].dictToJson('file.json',mode='load')

Masks['Red Mask'] = cvW.HSVMask('Red Mask')
Masks['Red Mask'].dictToJson('file.json',mode='load')

Masks['Green Mask'] = cvW.HSVMask('Green Mask')
Masks['Green Mask'].dictToJson('file.json',mode='load')

Masks['Yellow Mask'] = cvW.HSVMask('Yellow Mask')
Masks['Yellow Mask'].dictToJson('file.json',mode='load')

Masks['Hand'] = cvW.HSVMask('Hand')
Masks['Hand'].dictToJson('file.json',mode='load')

# initialise trims
####################

Trims = {}

Trims['Trim'] = cvW.trimmer('Trim')
Trims['Trim'].dictToJson('file.json',mode='load')
Trims['Trim'].initialise()

Trims['Trim2'] = cvW.trimmer('Trim2')
Trims['Trim2'].dictToJson('file.json',mode='load')
Trims['Trim2'].initialise()

# initialise Background Subtraction
###################################

bckSub = {}

bckSub['bckSub'] = cvW.bckSub('bckSub')
bckSub['bckSub'].dictToJson('file.json',mode='load')

# initialise thresh
###################################

Thresh = {}

Thresh['one'] = cvW.thresh('one')

#initialise Bins and workAreas
##################################

Bins = {}
BinList = ['first','second','third','fourth','fifth','sixth','seventh','eight','nineth','tenth','eleventh','twelveth']

for binname in BinList:
    Bins[binname] = cvW.binbox(binname)
    Bins[binname].dictToJson('file.json',mode='load')

wAreas = {}
wAreaList = ['areaFirst','areaSecond','areaThird','areaFourth']

for wArea in wAreaList:
    wAreas[wArea] = cvW.binbox(wArea)
    wAreas[wArea].dictToJson('file.json',mode='load')

#initialiseBlocks
##################

Blocks = cvW.blocks('blocks')
Blocks.addROI(Bins)
Blocks.addROI(wAreas)

# Pipeline class
####################

class pipeline(cvW.base,object):
    
    def __init__(self):
        super(pipeline, self).__init__( 'pipeline' )
        self.posAttrList = ['renderROIs','renderWAreas','kind','name','Trim','Trim2','blur','blueMask','redMask','greenMask','yellowMask','hand','BGR2RGB','bckSub','thresh','gray','hsv','renderBins','blocksRepres']
        self.notSave = ['kind','name']
        self.dict['kind'] = 'pipeline'
        self.stages = {'Trim':self.Trim,
                       'Trim2':self.Trim2,
                       'blur':self.blur,
                       'blueMask':self.blueMask,
                       'redMask':self.redMask,
                       'greenMask':self.greenMask,
                       'yellowMask':self.yellowMask,
                       'hand':self.hand,
                       'BGR2RGB':self.BGR2RGB,
                       'bckSub':self.bckSub,
                       'thresh':self.thresh,
                       'gray':self.gray,
                       'hsv':self.hsv,
                       'renderBins':self.renderBins,
                       'renderWAreas':self.renderWAreas,
                       'blocksRepres':self.blocksRepres,
                       'renderROIs':self.renderROIs}

        self.blankImage = np.zeros((480,640), np.uint8)
        self.stageTimers = {}
        self.timerInitialization = False
        
    def Trim(self): self.frame = Trims['Trim'].process(self.frame)

    def Trim2(self): self.frame = Trims['Trim2'].process(self.frame)
    
    def blur(self): self.blur = cv2.GaussianBlur(self.frame,(5,5),0)
    
    def hsv(self): self.hsv = cv2.cvtColor(self.blur,cv2.COLOR_BGR2HSV)

    def blueMask(self): 
        self.frame,contours = Masks['Blue Mask'].process(self.hsv,self.frame)
        Blocks.addContours(contours,[255,0,0])

    def redMask(self): 
        self.frame,contours = Masks['Red Mask'].process(self.hsv,self.frame)
        Blocks.addContours(contours,[0,0,255])
  
    def greenMask(self): 
        self.frame,contours = Masks['Green Mask'].process(self.hsv,self.frame)
        Blocks.addContours(contours,[0,255,0])

    def yellowMask(self): 
        self.frame,contours = Masks['Yellow Mask'].process(self.hsv,self.frame)
        Blocks.addContours(contours,[0,255,255])

    def hand(self): 
        self.frame,contours = Masks['Hand'].process(self.hsv,self.frame)
        self.handImage = np.copy(self.blankImage)
        for cnt in contours:
            bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])
            cv2.circle(self.handImage,bottommost,5,[255,255,255],-1)
            cv2.circle(self.frame,bottommost,5,[0,255,0],-1)
        Blocks.handDetection(self.handImage)

    def bckSub(self): 
        self.bckSub = bckSub['bckSub'].process(self.frame)
        Blocks.movementDetection(self.bckSub)

    def BGR2RGB(self): self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)     
    
    def gray(self): self.gray = cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
    
    def thresh(self): self.thresh = Thresh['one'].process(self.gray)

    def blocksRepres(self):Blocks.process()

    def renderROIs(self):
        #Blocks.detectPosition()
        Blocks.sizeFiltering()
        Blocks.detectMinBoundingBoxes()
        Blocks.detectType()
        self.frame = Blocks.renderROIs(self.frame)

    def renderBins(self): 
        for key in Bins: 
            self.frame = Bins[key].render(self.frame) 

    def renderWAreas(self): 
        for key in wAreas: 
            self.frame = wAreas[key].render(self.frame)        
    
    def initialiseTimers(self):
        
        for stage in self.dict['config']:
            if stage in self.stages.keys():
                if self.dict[stage]:
                    self.stageTimers[stage] = cvW.timingPerformance(stage)
        
        self.timerInitialization = True

    def process(self,image_frame):
        
        if self.timerInitialization == False:
            self.initialiseTimers()

        self.frame = image_frame
        self.originalFrame = image_frame 
        
        for stage in self.dict['config']:
                if stage in self.stages.keys():
                    if self.dict[stage]:                    
                        self.stageTimers[stage].performanceStart()
                        self.stages[stage]()
                        self.stageTimers[stage].performanceEnd()
       
        return self.frame


# Initialise pipelines
#####################

pipelinesList = {}

pipelinesList['pipelineTest'] = pipeline()
pipelinesList['pipelineBlue'] = pipeline()
pipelinesList['pipelineYellow'] = pipeline()
pipelinesList['pipelineRed'] = pipeline()
pipelinesList['pipelineGreen'] = pipeline()
pipelinesList['pipelineHand'] = pipeline()
pipelinesList['Trim'] = pipeline()
pipelinesList['thresh'] = pipeline()
pipelinesList['pipelineTest'].config(BGR2RGB=True)
pipelinesList['pipelineYellow'].config(blur=True,hsv=True,yellowMask=True,BGR2RGB=True)
pipelinesList['pipelineBlue'].config(blur=True,hsv=True,blueMask=True,BGR2RGB=True,gray=True,thresh=True)
pipelinesList['pipelineRed'].config(blur=True,hsv=True,redMask=True,BGR2RGB=True)
pipelinesList['pipelineGreen'].config(Trim=True,blur=True,hsv=True,greenMask=True,BGR2RGB=True)
pipelinesList['pipelineHand'].config(Trim=True,blur=True,hsv=True,hand=True,BGR2RGB=True)
pipelinesList['Trim'].config(Trim=True,blur=True,hsv=True,bckSub=False,hand=True,blueMask=True,redMask=True,greenMask=True,yellowMask=True,renderROIs=True,BGR2RGB=True)
pipelinesList['thresh'].config(Trim2=True,gray=True,thresh=True)
pipelinesList['bckSub'] = pipeline()
pipelinesList['bckSub'].config(Trim=True,bckSub=True)
pipelinesList['Bins'] = pipeline()
pipelinesList['Bins'].config(Trim=True,renderBins=True,BGR2RGB=True)
pipelinesList['wAreas'] = pipeline()
pipelinesList['wAreas'].config(Trim=True,renderWAreas=True,BGR2RGB=True)
pipelinesList['BGR2RGB'] = pipeline()
pipelinesList['BGR2RGB'].config(Trim=True,BGR2RGB=True)




# Masks['Hand Mask'].config(name='Hand Mask',
 #                            minBBoxes={'value':True,'interface':True,'widget':'button','command':'toggleBoolean'},
#                             drawMinBBoxes={'value':True,'interface':True,'widget':'button','command':'toggleBoolean'},
#                             boundingBoxIncrement ={'value':12,'interface':True,'widget':'slider','max':30,'min':1},
#                             trim={'value':True,'interface':True,'widget':'button','command':'toggleBoolean'},
#                             detect={'value':True,'interface':True,'widget':'button','command':'toggleBoolean'},
#                             filterC={'value':True,'interface':True,'widget':'button','command':'toggleBoolean'},
#                             Contours={'value':True,'interface':True,'widget':'button','command':'toggleBoolean'},
#                             drawLabel={'value':True,'interface':True,'widget':'button','command':'toggleBoolean'},
#                             saveButton = {'interface':True,'widget':'button','command':'saveobject'},
#                             bottomBoundary={'value':[9,56,103],'interface':True,'widget':'sliderList','max':[179,255,255],'min':[1,1,1],'nameList':['H','S','V']},
#                             topBoundary={'value':[71,255,255],'interface':True,'widget':'sliderList','max':[179,255,255],'min':[1,1,1],'nameList':['H','S','V']},
#                             erosion={'value':0,'interface':True,'widget':'slider','max':255,'min':0},
#                             dilation={'value':0,'interface':True,'widget':'slider','max':255,'min':0},
#                             blur={'value':11,'interface':True,'widget':'slider','max':255,'min':0},
#                             AreaTopBound={'value':80000,'interface':True,'widget':'slider','max':1000000,'min':0},
#                             AreaBottomBound={'value':0,'interface':True,'widget':'slider','max':10000,'min':0},
#                             StrokeThikness={'value':2,'interface':False},
#                             strokeRgb={'value':[0,255,255],'interface':False})

#BackSub['BckSub'].config(saveButton = {'interface':True,'widget':'button','command':'saveobject'},
                                   #bckSub = {'value':True,'interface':True,'widget':'button','command':'toggleBoolean'})

# Trims['Bins Area Trim'].config(name='Bins Area Trim',
#                             saveButton = {'interface':True,'widget':'button','command':'saveobject'},
#                             warpToggle = {'value':True,'interface':True,'widget':'button','command':'toggleBoolean'},
#                             topLeft={'value':[150,81],'interface':True,'widget':'sliderList','max':[640,480],'min':[0,0],'nameList':['X','Y']},
#                             topRight={'value':[588,114],'interface':True,'widget':'sliderList','max':[640,480],'min':[0,0],'nameList':['X','Y']},
#                             bottomLeft={'value':[128,403],'interface':True,'widget':'sliderList','max':[640,480],'min':[0,0],'nameList':['X','Y']},
#                             bottomRight={'value':[572,428],'interface':True,'widget':'sliderList','max':[640,480],'min':[0,0],'nameList':['X','Y']},
#                             resizeValue = {'value':[420,297],'interface':True,'widget':'sliderList','max':[640,480],'min':[0,0],'nameList':['X','Y']},
#                             resizeToggle = {'value':True,'interface':True,'widget':'button','command':'toggleBoolean'})