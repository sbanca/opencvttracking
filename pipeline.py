
###external
import cv2
import numpy as np

###internal
import cvWrapper as cvW
from config import config
from cvWobjects import Masks,Trims,bckSub,Thresh,Bins,wAreas,Blocks,GazePositions,Undistort,perspective,OrgRect

# Pipeline class
####################

class pipeline(cvW.base,object):
    
    def __init__(self):
        super(pipeline, self).__init__( 'pipeline' )
        self.posAttrList = ['perspective','renderROIs','renderWAreas','kind','name','Trim','Trim2','blur','blueMask','redMask','greenMask','yellowMask','hand','BGR2RGB','bckSub','thresh','gray','hsv','renderBins','blocksRepres','filterHand','drawEyeGaze','undistortCamera','prepearEyeGaze','renderOrgRect','perspeRender','flip','renderTrsfGaze']
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
                       'renderROIs':self.renderROIs,
                       'filterHand':self.filterHand,
                       'drawEyeGaze':self.drawEyeGaze,
                       'undistortCamera':self.undistortCamera,
                       'prepearEyeGaze':self.prepearEyeGaze,
                       'perspective':self.perspective,
                       'renderOrgRect':self.renderOrgRect,
                       'perspeRender':self.perspeRender,
                       'flip':self.flip,
                       'renderTrsfGaze':self.renderTrsfGaze}

        self.blankImage = np.zeros((480,640), np.uint8)
        self.stageTimers = {}
        self.timerInitialization = False
        
    def Trim(self): 
        self.frame = Trims['Trim'].process(self.frame)

    def Trim2(self): 
        self.frame = Trims['Trim2'].process(self.frame)
        GazePositions.changeInScale(Trims['Trim2'].dict['resizeValue']['value'])
    
    def blur(self): 
        self.blur = cv2.GaussianBlur(self.frame,(5,5),0)
    
    def hsv(self): 
        self.hsv = cv2.cvtColor(self.blur,cv2.COLOR_BGR2HSV)

    def flip(self):
        self.frame = cv2.flip( self.frame, -1 )

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
        self.handImage,self.frame,self.handCoordinates = Masks['Hand'].mostSomenthing(self.handImage,self.frame) 
        Blocks.handDetection(self.handImage,self.handCoordinates)

    def bckSub(self): 
        self.bckSub = bckSub['bckSub'].process(self.frame)
        #self.frame = self.bckSub
        Blocks.movementDetection(self.bckSub)

    def BGR2RGB(self): 
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)     
    
    def gray(self): 
        self.gray = cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
    
    def thresh(self): 
        self.thresh = Thresh['one'].process(self.gray)

    def filterHand(self): 
        Blocks.handFiltering(self.handImage2)

    def blocksRepres(self):
        Blocks.process()

    def renderROIs(self):
        #Blocks.detectPosition()
        self.frame = Blocks.renderROIs(self.frame)

    def renderBins(self): 
        for key in Bins: 
            self.frame = Bins[key].render(self.frame) 
    
    def renderOrgRect(self): 
        self.frame = OrgRect.render(self.frame) 

    def prepearEyeGaze(self):
        GazePositions.prepearPos(self.frame)
    
    def drawEyeGaze(self):
        self.frame = GazePositions.renderGaze(self.frame)
        
    def renderWAreas(self): 
        for key in wAreas: 
            self.frame = wAreas[key].render(self.frame)        
    
    def undistortCamera(self):
        self.frame = Undistort.process(self.frame)
        GazePositions.changeInPixelMapping(Undistort.invMap)
        GazePositions.roiTrimming(Undistort.roi)
    
    def perspective(self):
        self.frame = perspective.process(self.frame)
        Blocks.gazeDetection()

    def perspeRender(self):
        self.frame = perspective.renderAll(self.frame)

    def renderTrsfGaze(self):
        self.frame = perspective.renderTrsfmGaze(self.frame)

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





