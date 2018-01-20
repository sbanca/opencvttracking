import os.path
import json
import csv
import cv2
import time
import datetime
import numpy as np
import os.path
import json
import copy
import matplotlib.pyplot as plt
from scipy.signal import lfilter
from config import config
import matplotlib.path as pth


class timeStamp():

    def __init__(self):
        self.timestamp = 0 
        self.mode = 'unset'
        self.dict={}
        time.clock()

    def setMode(self,mode):
        self.mode = mode

    def getMode(self): return self.mode

    def setTime(self,value): self.timestamp = value

    def getTime(self): 
        
        if self.mode =='live': 
            self.timestamp = time.clock()

        return self.timestamp

    def addFrameNumber(self,key,val): 
        self.dict[key] = val
    
    def getFrameNumber(self,key):
        return self.dict[key]

class timingPerformance():

    def __init__(self, name):
        self.label = name
        self.timer = 0
        self.list = []
        self.average = 0

    def performanceStart(self):
        self.e1 = cv2.getTickCount()

    def performanceEnd(self):
        self.e2 = cv2.getTickCount()
        self.timer = (self.e2 - self.e1)/ cv2.getTickFrequency()
        self.list.append(self.timer)
        self.average = sum(self.list)/len(self.list)

    def printPerformance(self):
        print('Name: ' +str(self.label)+' Performance: '+str(self.average))

class base():

    def __init__(self,name):
        self.dict = {}
        self.dict['name'] = name
        self.dict['kind'] = 'base'
        self.posAttrList = ['name','kind','saveButton','config','piu1','meno1','piu10','meno10','piu100','meno100','saveAndReload','adjustment']
        self.notSave = ['name','kind']
        self.dict['saveButton'] = {'interface':True,'widget':'button','command':'saveobject'}

    def config(self, cnf=None, **kw):

        #save each parameter separatly
        for idx,attr in enumerate(self.posAttrList):
            if attr in kw.keys():
                if isinstance(kw[attr], dict) and attr in self.dict.keys() and isinstance(self.dict[attr], dict): self.subconfig(attr,kw[attr]) #incase the value is a dict and there is some nested stuff
                else: self.dict[attr] = kw[attr]
            if not (cnf == None): 
                if attr in cnf.keys(): 
                    self.dict[attr] = cnf[attr]   

        #save a record of the all config string
        if not (kw == None): 
            self.dict['config'] = list(kw.keys())
        if not (cnf == None): 
            self.dict['config'] = list(cnf.keys())
    
    def subconfig(self,attr,attrDict):

        for key in attrDict: 
            self.dict[attr][key] = attrDict[key]
           
    def printAttributes(self):

        print('start------------------------')
        for idx,value in enumerate(self.dict):
            print(str(value)+' : '+str(self.dict[value]))
        print('end--------------------------')

    def printInheritedAttributes(self):

        print('start------------------------')
        for idx,value in enumerate(self.referencedObject.dict):
            print(str(value)+' : '+str(self.referencedObject.dict[value]))
        print('end--------------------------')
    
    def dictToJson(self, fileName, **kw):
        
        self.fileName = fileName

        if 'mode' in kw.keys(): 
            if 'save' in kw['mode']: self.__saveDict()
            if 'load' in kw['mode']: self.__loadDict()

    def __loadDict(self):
        
        if not os.path.isfile(self.fileName):
            print('file not existent notthing loaded')
        else: 
            data_file = open(self.fileName, 'r+')   
            existingDict = json.load(data_file)
            if self.dict['kind'] in existingDict:
                if self.dict['name'] in existingDict[self.dict['kind']]: self.config(existingDict[ self.dict['kind'] ][ self.dict['name'] ])

        data_file.close()

    def __saveDict(self):
        
        if not os.path.isfile(self.fileName):
            data_file =  open(self.fileName, 'w') 
            existingDict = {}
        else: 
            data_file = open(self.fileName, 'r+')   
            existingDict = json.load(data_file)
            data_file.close()
            data_file =  open(self.fileName, 'w')  

        json.dump( self.__prepearDict(existingDict) , data_file,  indent=5)
        data_file.close()

    def __prepearDict(self,existingDict):

        newObject = { }

        for idx,value in enumerate(self.dict):
            if value not in self.notSave and not type(self.dict[value]).__module__ == np.__name__:
                newObject[value] = self.dict[value]
        
        if not self.dict['kind'] in existingDict: existingDict[self.dict['kind']] = { }
        if not self.dict['name'] in existingDict[self.dict['kind']]: existingDict[ self.dict['kind'] ][ self.dict['name'] ] = { }
        existingDict[ self.dict['kind'] ][ self.dict['name'] ] =  newObject  


        return existingDict

class HSVMask(base,object):
    
    def __init__(self,name,object=None):
        super(HSVMask, self).__init__( name )
        if not (object == None): self.referencedObject = object
        self.posAttrList = ['kind','name','bottomBoundary','topBoundary','erosion','dilation','blur','minBBoxes','drawMinBBoxes','AreaTopBound','AreaBottomBound','StrokeThikness','strokeRgb','saveButton', 'detect', 'filterC' ,'Contours' ,'drawLabel','trim','boundingBoxIncrement','maxMinPoint']
        self.notSave = ['kind','name']
        self.dict['kind'] = 'HSVMask'
        self.count=0
        self.mask = np.zeros((480,640), np.uint8)
        self.dict['maxMinPoint'] = {'value':0,'interface':True,'widget':'multibutton','buttonsValues':[0,1,2,3],'buttonsNames':['leftmost','rightmost','bottommost','topmost']}

    def process(self,hsvFrame,frame):
        
        self.hsvFrame = hsvFrame
        self.frame = frame
        self.originalFrame = copy.copy(frame)

        if self.dict['detect']['value']: self.detectHSVcontours()
        if self.dict['filterC']['value']: self.filterContours()
        if self.dict['Contours']['value']: self.drawContours()
        if self.dict['drawLabel']['value']: self.drawLabel()
        if self.dict['trim']['value']: self.trimSamples()
        if self.dict['minBBoxes']['value']: 
            self.detectMinBoundingBoxes()
            if self.dict['drawMinBBoxes']['value']: 
                self.drawMinBoundingBoxes()

        return (self.frame,self.contours)

    def trimSamples(self):

        self.boundingBoxes=[]

        for idx,c in enumerate(self.contours):
            self.boundingBoxes.append(cv2.boundingRect(self.contours[idx]))
            x = self.boundingBoxes[idx][0]
            y = self.boundingBoxes[idx][1]
            w = self.boundingBoxes[idx][2]
            h = self.boundingBoxes[idx][3]
            cX,cY = (np.average([x,x+w]),np.average([y,y+h]))
            if w>h: 
                h=int(w+w/2+self.dict['boundingBoxIncrement']['value'])
                w=h
            if h>w: 
                w=int(h+w/2+self.dict['boundingBoxIncrement']['value'])
                h=w
            x = int(cX - w/2)
            y = int(cY - h/2)
            # try:
            #     trim = self.originalFrame[y:y+h,x:x+w] 
            #     resized = cv2.resize(trim, (100,100), interpolation = cv2.INTER_AREA)
            #     cv2.imwrite("test/"+str(self.count)+".jpg",resized) 
            #     self.count+=1
            # except Exception:
            #     pass      
            cv2.rectangle(self.frame,(x,y),(x+w,y+h),self.dict['strokeRgb']['value'],2)

    def detectMinBoundingBoxes(self):

        self.minBoundingBoxes=[]

        for idx,c in enumerate(self.contours):
            self.minBoundingBoxes.append(cv2.minAreaRect(self.contours[idx]))

    def drawMinBoundingBoxes(self):

        for idx,c in enumerate(self.minBoundingBoxes):
            box = cv2.boxPoints(self.minBoundingBoxes[idx])
            box = np.int0(box)
            cv2.drawContours(self.frame,[box],0,self.dict['strokeRgb']['value'],1)

    def detectHSVcontours(self):

        #masking algorithm
        bottomBoundary = np.array(self.dict['bottomBoundary']['value'])
        topBoundary = np.array(self.dict['topBoundary']['value'])
        self.mask = cv2.inRange(self.hsvFrame ,bottomBoundary ,topBoundary )
    
        #refine mask
        self.mask = cv2.dilate(self.mask, None, iterations= self.dict['dilation']['value']) 
        self.mask = cv2.erode(self.mask, None, iterations= self.dict['erosion']['value'])
        
        #result bitwise
        self.detectResult = cv2.bitwise_and( self.frame, self.frame, mask = self.mask)

        #contourn
        gray = cv2.cvtColor( self.detectResult, cv2.COLOR_BGR2GRAY)
        
        #this is making it perform bad fix later 
        if self.dict['blur']['value']<1: self.dict['blur']['value'] =1 
        if self.dict['blur']['value']%2 !=1: self.dict['blur']['value'] =1 
        blur = cv2.GaussianBlur( gray, (  self.dict['blur']['value'] , self.dict['blur']['value'] ), 0)

        ret,thresh = cv2.threshold( blur, 0, 255, cv2.THRESH_BINARY)

        img2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)   
        self.contours =  contours

    def filterContours(self):

        self.areas = []
        for idx,c in enumerate(self.contours):
            self.areas.append(cv2.contourArea(c))
            if (self.areas[idx] > self.dict['AreaTopBound']['value']) |  (self.areas[idx] < self.dict['AreaBottomBound']['value']): 
                self.contours[idx]='remove'
                self.areas[idx]='remove'
        
        self.contours[:] = [item for item in self.contours if item != 'remove']
        self.areas[:] = [item for item in self.areas if item != 'remove']

        #if len(self.contours) > 3 :  self.dict['speed'] = 1001              
    
    def drawContours(self): cv2.drawContours(self.frame, self.contours, -1, self.dict['strokeRgb']['value'],self.dict['StrokeThikness']['value'])    

    def drawLabel(self):

        self.centers = []

        for idx,c in enumerate(self.contours):
            try:
                M = cv2.moments(c)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv2.putText(self.frame, self.dict['name'] , (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                self.centers.append[()]
            except Exception: 
                pass
    
    def mostSomenthing(self,frameProcess,frameReppres):
        most = 0 
        value = self.dict['maxMinPoint']['value']

        for cnt in self.contours:
            if ( value == 0 ): 
                most = tuple(cnt[cnt[:,:,0].argmin()][0])
            elif ( value == 1 ):
                most = tuple(cnt[cnt[:,:,0].argmax()][0])
            elif ( value == 2 ): 
                most = tuple(cnt[cnt[:,:,1].argmin()][0])
            elif ( value == 3 ): 
                most = tuple(cnt[cnt[:,:,1].argmax()][0])
            cv2.circle(frameProcess,most,5,[255,255,255],-1)
            cv2.circle(frameReppres,most,5,[0,255,0],-1)
        
        return (frameProcess,frameReppres,most)

class Main(base,object):

    def __init__(self,name,object=None):
        super(Main, self).__init__( name )
        if not (object == None): self.referencedObject = object
        self.posAttrList = ['kind','name']
        self.notSave = self.notSave = ['kind','name']
        self.dict['kind'] = 'Main'

class trimmer(base,object):

    def __init__(self,name,object=None):
        super(trimmer, self).__init__( name )
        if not (object == None): self.referencedObject = object
        self.posAttrList = ['kind','name','saveButton','warpToggle','warpValue','resizeValue','resizeToggle','resize','topLeft','topRight','bottomLeft','bottomRight']
        self.notSave = self.notSave = ['kind','name','pts2','pts1','M']
        self.dict['kind'] = 'trimmer'
        self.pts2 = np.float32([[0,0],[640,0],[0,480],[640,480]])

    def initialise(self):
        
        self.dict['pts2'] = np.float32([[0,0],[640,0],[0,480],[640,480]])

        self.dict['pts1'] = np.float32([[self.dict['topLeft']['value'][0],self.dict['topLeft']['value'][1]],
                                        [self.dict['topRight']['value'][0],self.dict['topRight']['value'][1]],
                                        [self.dict['bottomLeft']['value'][0],self.dict['bottomLeft']['value'][1]],
                                        [self.dict['bottomRight']['value'][0],self.dict['bottomRight']['value'][1]]])

        self.dict['M'] = cv2.getPerspectiveTransform( self.dict['pts1'], self.dict['pts2'])

    def process(self,frame):
        
        self.frame = frame
        self.originalFrame = copy.copy(frame)

        if self.dict['warpToggle']['value']: self.warp()
        else: self.pointDisplay()
        if self.dict['resizeToggle']['value']: self.resize()
        
        return self.frame

    def pointDisplay(self):
        cv2.circle(self.frame, (self.dict['topLeft']['value'][0], self.dict['topLeft']['value'][1]), 1 , (0, 255, 0), 2)
        cv2.putText(self.frame, 'topLeft' , (self.dict['topLeft']['value'][0]-30, self.dict['topLeft']['value'][1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.circle(self.frame, (self.dict['topRight']['value'][0], self.dict['topRight']['value'][1]), 1 , (0, 255, 0), 2)
        cv2.putText(self.frame, 'topRight' , (self.dict['topRight']['value'][0]-30, self.dict['topRight']['value'][1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.circle(self.frame, (self.dict['bottomLeft']['value'][0], self.dict['bottomLeft']['value'][1]), 1 , (0, 255, 0), 2)
        cv2.putText(self.frame, 'bottomLeft' , (self.dict['bottomLeft']['value'][0]-40, self.dict['bottomLeft']['value'][1]+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.circle(self.frame, (self.dict['bottomRight']['value'][0], self.dict['bottomRight']['value'][1]), 1 , (0, 255, 0), 2)
        cv2.putText(self.frame, 'bottomRight' , (self.dict['bottomRight']['value'][0]-40, self.dict['bottomRight']['value'][1]+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        self.initialise()

    def warp(self):
        self.frame = cv2.warpPerspective(self.frame,self.dict['M'],(640,480))

    def resize(self):
        self.frame = cv2.resize(self.frame ,(self.dict['resizeValue']['value'][0],self.dict['resizeValue']['value'][1]), interpolation = cv2.INTER_CUBIC)

class bckSub(base,object):

    def __init__(self,name,object=None):
        super(bckSub, self).__init__( name )
        if not (object == None): self.referencedObject = object
        self.posAttrList = ['kind','name','saveButton','bckSub','opening','openingToggle','treshType','value1','value2','blur']
        self.notSave = self.notSave = ['kind','name']
        self.dict['kind'] = 'bckSub'
        self.fgbg = cv2.createBackgroundSubtractorMOG2()
        # self.dict['opening'] = {'value':5,'interface':True,'widget':'slider','max':255,'min':0}
        # self.dict['openingToggle'] = {'value':True,'interface':True,'widget':'button','command':'toggleBoolean'}
        # self.dict['treshType'] =  {'value':1,'interface':True,'widget':'multibutton','buttonsValues':[0,1,2,3],'buttonsNames':['mean','gaussian','binary','nothresh']}
        # self.dict['value1'] = {'value':255,'interface':True,'widget':'slider','max':255,'min':0}
        # self.dict['value2'] = {'value':127,'interface':True,'widget':'slider','max':127,'min':0}
        # self.dict['blur'] =  {'value':127,'interface':True,'widget':'slider','max':127,'min':0}
        self.kernel = np.ones((7,7),np.uint8)
    
    
    def process(self,frame):

        #self.kernel = np.ones((self.dict['opening']['value'],self.dict['opening']['value']),np.uint8)
               
        originalFrame = copy.copy(frame)

        if self.dict['bckSub']['value']: 
            frame = self.fgbg.apply(frame)
            frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, self.kernel)
            #frame = cv2.GaussianBlur( frame, ( 17,17 ), 0)
            ret,frame = cv2.threshold(frame,127,255,cv2.THRESH_BINARY)
            # if self.dict['openingToggle']['value']: frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, self.kernel)
            # if self.dict['treshType']['value'] == 0 : frame = cv2.adaptiveThreshold(frame,self.dict['value1']['value'],cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,11,2)
            # elif self.dict['treshType']['value'] == 1 : frame = cv2.adaptiveThreshold(frame,self.dict['value1']['value'],cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
            # elif self.dict['treshType']['value'] == 2 : ret,frame = cv2.threshold(frame,self.dict['value2']['value'],self.dict['value1']['value'],cv2.THRESH_BINARY)
            
        return frame

class thresh(base,object):

    def __init__(self,name,object=None):
        super(thresh, self).__init__( name )
        if not (object == None): self.referencedObject = object
        self.posAttrList = ['kind','name','saveButton','threshValue','treshType']
        self.notSave = self.notSave = ['kind','name']
        self.dict['kind'] = 'thresh'
        self.dict['treshType'] =  {'value':1,'interface':True,'widget':'multibutton','buttonsValues':[0,1,2,3],'buttonsNames':['mean','gaussian','binary','nothresh']}
        self.dict['value1'] = {'value':255,'interface':True,'widget':'slider','max':255,'min':0}
        self.dict['value2'] = {'value':127,'interface':True,'widget':'slider','max':127,'min':0}
    
    def process(self,frame):
        
        self.frame = frame
        self.originalFrame = copy.copy(frame)
        
        if self.dict['treshType']['value'] == 0 : self.frame = cv2.adaptiveThreshold(self.frame,self.dict['value1']['value'],cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,11,2)
        elif self.dict['treshType']['value'] == 1 : self.frame = cv2.adaptiveThreshold(self.frame,self.dict['value1']['value'],cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
        elif self.dict['treshType']['value'] == 2 : ret,self.frame = cv2.threshold(self.frame,self.dict['value2']['value'],self.dict['value1']['value'],cv2.THRESH_BINARY)     

        return self.frame

class binbox(base,object):

    def __init__(self,name,object=None):
        super(binbox, self).__init__( name )
        if not (object == None): self.referencedObject = object
        self.posAttrList = ['OnlyTLBR','kind','name','saveButton','topLeft','topRight','bottomLeft','bottomRight','coordinatesToggle','coordinatesX','coordinatesY','coordinateBoxes','translateCoordX','translateCoordY','revTransCoordX','revTransCoordY','cX','cY','startingValueX','startingValueY','reverseValueX','reverseValueY','area']
        self.notSave = self.notSave = ['kind','name','textCenter','box','coordinateBoxesNumPy']
        self.dict['kind'] = 'binbox'
        self.dict['OrgRectCircle'] = {'value':5,'interface':True,'widget':'slider','max':40,'min':0}
        self.dict['topLeft'] = {'value':[10,10],'interface':True,'widget':'sliderList','max':[640,480],'min':[0,0],'nameList':['X','Y']}
        self.dict['topRight'] = {'value':[20,10],'interface':True,'widget':'sliderList','max':[640,480],'min':[0,0],'nameList':['X','Y']}
        self.dict['bottomLeft'] = {'value':[10,20],'interface':True,'widget':'sliderList','max':[640,480],'min':[0,0],'nameList':['X','Y']}
        self.dict['bottomRight'] = {'value':[20,20],'interface':True,'widget':'sliderList','max':[640,480],'min':[0,0],'nameList':['X','Y']}
        self.dict['coordinatesToggle']= {"value": False,"interface": True,"widget": "button","command": "toggleBoolean","oldValue":False}
        self.dict['coordinatesX'] = {'value':0,'interface':True,'widget':'slider','max':30,'min':0}
        self.dict['coordinatesY'] = {'value':0,'interface':True,'widget':'slider','max':30,'min':0}
        self.dict['startingValueX'] = {'value':0,'interface':True,'widget':'slider','max':52,'min':0}
        self.dict['startingValueY'] = {'value':0,'interface':True,'widget':'slider','max':52,'min':0}
        self.dict['reverseValueX'] = {"value": False,"interface": True,"widget": "button","command": "toggleBoolean"}
        self.dict['reverseValueY'] = {"value": False,"interface": True,"widget": "button","command": "toggleBoolean"}
        self.dict['OnlyTLBR'] = {"value": True,"interface": True,"widget": "button","command": "toggleBoolean"}
        self.dict['OrgRectCorners'] = {"value": False,"interface": True,"widget": "button","command": "toggleBoolean"}
        self.dict['OrgRectCircle'] = {'value':5,'interface':True,'widget':'slider','max':40,'min':0}
        self.dict['coordinateBoxes'] = []
        self.dict['coordinateBoxesNumPy'] = []
        self.dict['translateCoordX'] = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX','AY','AZ']
        self.dict['translateCoordY'] = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','43','44','45','46','47','48','49','50','51','52']
        self.dict['revTransCoordX'] = list(reversed(self.dict['translateCoordX']))
        self.dict['revTransCoordY'] = list(reversed(self.dict['translateCoordY']))
        self.dict['cX'] = []
        self.dict['cY'] = []      

    def recalculateCoordinatesBoxes(self):
        
        self.dict['coordinateBoxes'] = []
        self.dict['coordinateBoxesNumPy'] = []

        if self.dict['OnlyTLBR']['value']:
            
            self.dict['topRight']['value'] = [self.dict['bottomRight']['value'][0],self.dict['topLeft']['value'][1]]
            self.dict['bottomLeft']['value'] = [self.dict['topLeft']['value'][0],self.dict['bottomRight']['value'][1]]

        if self.dict['coordinatesToggle']['value']:

            if 'translateCoordX' in self.notSave: self.notSave.remove('translateCoordX') 
            if 'revTransCoordX' in self.notSave: self.notSave.remove('revTransCoordX') 
            if 'translateCoordY' in self.notSave: self.notSave.remove('translateCoordY') 
            if 'revTransCoordY' in self.notSave: self.notSave.remove('revTransCoordY') 
            if 'translateCoordX' in self.notSave: self.notSave.remove('translateCoordX') 
            if 'revTransCoordX' in self.notSave: self.notSave.remove('revTransCoordX') 
            if 'cX' in self.notSave: self.notSave.remove('cX') 
            if 'cY' in self.notSave: self.notSave.remove('cY') 
            if 'coordinateBoxes' in self.notSave: self.notSave.remove('coordinateBoxes')

        else:
             self.notSave.append('translateCoordX')
             self.notSave.append('revTransCoordX')
             self.notSave.append('translateCoordY')
             self.notSave.append('revTransCoordY')
             self.notSave.append('cX')
             self.notSave.append('cY')
             self.notSave.append('coordinateBoxes')
    
        if self.dict['reverseValueX']['value']: listX = self.dict['revTransCoordX'] 
        else: listX = self.dict['translateCoordX']
        if self.dict['reverseValueY']['value']: listY = self.dict['revTransCoordY'] 
        else: listY = self.dict['translateCoordY'] 
            
        self.dict['cX'] = listX[self.dict['startingValueX']['value']:] + listX[:self.dict['startingValueX']['value']]
        self.dict['cY'] = listY[self.dict['startingValueY']['value']:] + listY[:self.dict['startingValueY']['value']]

        if (self.dict['coordinatesX']['value']==0 or self.dict['coordinatesY']['value']==0): 
            self.dict['coordinatesToggle']["value"] == False
            self.dict['coordinatesToggle']["oldValue"] == False
            return None
        
        x1 = self.dict['topLeft']['value'][0]
        x2 = self.dict['topRight']['value'][0]
        x3 = self.dict['bottomRight']['value'][0]
        x4 = self.dict['bottomLeft']['value'][0]
        y1 = self.dict['topLeft']['value'][1]
        y2 = self.dict['topRight']['value'][1]
        y3 = self.dict['bottomRight']['value'][1]
        y4 = self.dict['bottomLeft']['value'][1]
        nx = self.dict['coordinatesX']['value']
        ny = self.dict['coordinatesY']['value']
        spaceX = abs((( x2 - x4 - x1 +x3 )/2)/nx)
        spaceY = abs((( y2 - y4 + y1 -y3 )/2)/ny)

        for idxY in range(ny):
            
            boxY1 = y1 + spaceY * idxY
            boxY2 = y1 + spaceY * (idxY+1)
            
            for idxX in range(nx):
                
                boxX1 = x1 + spaceX * idxX
                boxX2 = x1 + spaceX * (idxX+1)
                boxNumber = (idxY+1) * (idxX+1)
                box = [[boxX1,boxY1],[boxX2,boxY1],[boxX2,boxY2],[boxX1,boxY2]]
                npbox = np.int0(box)
                center = tuple(npbox.mean(axis=0, dtype=np.int0))
                center = (center[0].item(), center[1].item())
                cx = self.dict['cX'][idxX]
                cy = self.dict['cY'][idxY]
                
                self.dict['coordinateBoxes'].append({'box':box,'X':idxX,'Y':idxY,'center':center,'cX':cx,'cY':cy})
                self.dict['coordinateBoxesNumPy'].append({'box':npbox,'X':idxX,'Y':idxY,'center':center,'cX':cx,'cY':cy})

    def render(self,frame):
        
        self.frame = frame
        self.originalFrame = copy.copy(frame)

        if self.dict['OnlyTLBR']['value']:
            self.dict['topRight']['value'] = [self.dict['bottomRight']['value'][0],self.dict['topLeft']['value'][1]]
            self.dict['bottomLeft']['value'] = [self.dict['topLeft']['value'][0],self.dict['bottomRight']['value'][1]]


        if not(self.dict['coordinatesToggle']['value']==self.dict['coordinatesToggle']['oldValue']): 
                self.dict['coordinatesToggle']['oldValue']=self.dict['coordinatesToggle']['value']
                self.recalculateCoordinatesBoxes()

        if self.dict['coordinatesToggle']['value']==True:        

            if len(self.dict['coordinateBoxesNumPy'])==0:self.recalculateCoordinatesBoxes()

            for box in self.dict['coordinateBoxesNumPy']:
                cv2.drawContours(self.frame,[box['box']],0,(150, 150, 150),1)
                #cv2.circle(self.frame, box['center'], 1 , (100,100,100), 2)
                if box['X'] == self.dict['coordinatesX']['value']-1: cv2.putText(self.frame, box['cY']  ,box['center'], cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255, 255, 255), 1)
                if box['Y'] == self.dict['coordinatesY']['value']-1: cv2.putText(self.frame, box['cX']  ,box['center'], cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255, 255, 255), 1)

        self.dict['box'] = np.int0([self.dict['topLeft']['value'],self.dict['topRight']['value'],self.dict['bottomRight']['value'],self.dict['bottomLeft']['value']])
        self.dict['textCenter'] = tuple(self.dict['box'][:2].mean(axis=0, dtype=np.int0))  
        self.dict['textCenter'] = ( self.dict['textCenter'][0]-10, self.dict['textCenter'][1]+10) 
        
        cv2.drawContours(self.frame,[self.dict['box']],0,(255, 255, 255),1)  

        if self.dict['OrgRectCorners']['value']:
            cv2.circle(self.frame, tuple(self.dict['topLeft']['value']), self.dict['OrgRectCircle']['value'] , (000,000,255), 1)
            cv2.circle(self.frame, tuple(self.dict['topRight']['value']), self.dict['OrgRectCircle']['value'] , (000,000,255), 1)
            cv2.circle(self.frame, tuple(self.dict['bottomRight']['value']), self.dict['OrgRectCircle']['value'] , (000,000,255), 1)
            cv2.circle(self.frame, tuple(self.dict['bottomLeft']['value']), self.dict['OrgRectCircle']['value'] , (000,000,255), 1)
            
        cv2.putText(self.frame, self.dict['name'] ,self.dict['textCenter'], cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
    
        return self.frame
    
    def returnPoints(self):

        return   [self.dict['topLeft']['value'],
                 self.dict['topRight']['value'],
                 self.dict['bottomRight']['value'],
                 self.dict['bottomLeft']['value']]

class blocks(base,object):

    def __init__(self,name,object=None):
        super(blocks, self).__init__( name )
        if not (object == None): self.referencedObject = object
        self.posAttrList = ['kind','name','BlockProp','AreaTopBound','AreaBottomBound','B2x1','B2x2','B2x4','blocchi','persistentModelToggle','persistentModel','proceduralTask','procedureToggle','proceduralTask','task','time','testGraph']
        self.notSave = self.notSave = ['kind','name','speed','contours','oldContours','oldContoursExist','ROI','handCoordinatesTimestamp','handCoordinates','movements','movementsStamps','movementsBlocks','blockInMovement','BlockProp','persistentModel','proceduralTask','config']
        self.dict['kind'] = 'blocks'
        self.dict['blockInMovement']=''
        self.dict['handCoordinatesX']=np.array([])
        self.dict['handCoordinatesY']=np.array([])
        self.dict['handCoordinatesTimestamp']=np.array([])
        self.dict['GazeCoordinatesX']=np.array([])
        self.dict['GazeCoordinatesY']=np.array([])
        self.dict['GazeCoordinatesTimestamp']=np.array([])
        self.dict['GazeLocation'] = []
        self.dict['GazeLocationTimestamp']=np.array([])

        self.ts = time.time()

        self.dict['ROI'] ={'movementThresold':0,'center':[],'box':[],'path':[],'name':[],'gaze':[],'movement':[],'hand':[],'coordinatesToggle':[],'coordinatesX':[],'coordinatesY':[],'coordinateBoxes':[],'coordinateBoxesNumPy':[],'coordinateCenter':[],'cX':[],'cY':[],'displayBoxGaze':[],'displayBoxHand':[],'blockname':[]}
        self.dict['contours']={'contours':[],'color':[],'type':[],'boundingBox':[],'minBoundingBox':[],'areas':[],'ROI':[],'center':[],'ROImovement':[],'ROIhand':[],'ROIindex':[],'movement':[]}
        self.dict['oldContours']={}
        self.dict['oldContoursExist'] = False

        self.dict['BlockProp'] = ['id','boundingBox','minBoundingBox','center','color','size','positionXY','positionROI']     
        self.dict['AreaTopBound'] = {'value':2000,'interface':False,'widget':'slider','max':10000,'min':0}
        self.dict['AreaBottomBound']={'value':128,'interface':False,'widget':'slider','max':10000,'min':0}
        self.dict['B2x1'] = {'value':350,'interface':False,'widget':'slider','max':10000,'min':0}
        self.dict['B2x2'] = {'value':600,'interface':False,'widget':'slider','max':10000,'min':0}
        self.dict['B2x4'] = {'value':1368,'interface':False,'widget':'slider','max':10000,'min':0}
        self.dict['time'] = {'interface':True,'widget':'text'}
        
        self.dict['blocchi'] = {'interface':True,'widget':'text'}
        self.dict['persistentModelToggle'] = {"value": True,"interface": True,"widget": "button","command": "toggleBoolean"}       
        self.dict['persistentModel']= config['persistentModel']

        self.cleanPersistentModel()
        self.persMod=[]

        self.dict['task'] = {'interface':True,'widget':'text'}
        self.dict['procedureToggle'] = {"value": True,"interface": True,"widget": "button","command": "toggleBoolean"}
        self.dict['proceduralTask'] = config['proceduralTask']

        self.cleanProceduralTaskModel()
        self.dict['movements']=[]
        self.dict['movementsStamps']=[]
        self.dict['movementsBlocks']=[]

        time.clock()

        self.dict['testGraph'] = {"interface": True,"widget": "button","command":self.plottest}  

    def loadExternal(self,fileName,key):

        if not os.path.isfile(fileName):
            print('file not existent notthing loaded')
        else: 
            data_file = open(fileName, 'r+')   
            json_content= json.load(data_file)
            return json_content[key] 

    def addContours(self,contours,color):
        
        for idx,cnt in enumerate(contours):
            try:
                M = cv2.moments(cnt)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                self.dict['contours']['center'].append((cX,cY))
            except Exception:
                self.dict['contours']['center'].append((0,0))           

            self.dict['contours']['contours'].append(cnt)
            self.dict['contours']['color'].append(color)
            self.dict['contours']['ROI'].append('undetected')
            self.dict['contours']['ROIhand'].append(False)           
            self.dict['contours']['ROImovement'].append(False)
            self.dict['contours']['ROIindex'].append('undetected')
            self.dict['contours']['type'].append('noType')
            self.dict['contours']['areas'].append(cv2.contourArea(cnt))
            self.dict['contours']['movement'].append(False)
            self.dict['contours']['minBoundingBox'].append('empty')

    def addROI(self,dictionary):
        
        for key in dictionary: 

            box = np.int0([dictionary[key].dict['topLeft']['value'],
                            dictionary[key].dict['topRight']['value'],
                            dictionary[key].dict['bottomRight']['value'],
                            dictionary[key].dict['bottomLeft']['value']])
            
            center = tuple(box[:2].mean(axis=0, dtype=np.int0))
            center = ( center[0]-10,center[1]+10) 

            self.dict['ROI']['box'].append(box) 
            self.dict['ROI']['displayBoxGaze'].append(np.sum([box,np.int64([[5,5],[-5,5],[-5,-5],[5,-5]])],axis=0)) 
            self.dict['ROI']['displayBoxHand'].append(np.sum([box,np.int64([[-5,-5],[5,-5],[5,5],[-5,5]])],axis=0))
            self.dict['ROI']['path'].append(pth.Path(box))
            self.dict['ROI']['center'].append(center)
            self.dict['ROI']['name'].append(key)
            self.dict['ROI']['movement'].append(False)
            self.dict['ROI']['gaze'].append(False)
            self.dict['ROI']['hand'].append(False)
            self.dict['ROI']['movementThresold'] = (dictionary[key].dict['topRight']['value'][0]-dictionary[key].dict['topLeft']['value'][0])*(dictionary[key].dict['bottomLeft']['value'][1]-dictionary[key].dict['topLeft']['value'][1])/5
            self.dict['ROI']['blockname'].append(False)
            #self.dict['ROI']['coordinatesToggle'].append(dictionary[key].dict['coordinatesToggle'])
            
            if len(dictionary[key].dict['coordinateBoxes']) > 0:
                
                self.dict['ROI']['coordinatesToggle'].append(True)  
                self.dict['ROI']['coordinatesX'].append([]) 
                self.dict['ROI']['coordinatesY'].append([]) 
                self.dict['ROI']['cX'].append([]) 
                self.dict['ROI']['cY'].append([]) 
                self.dict['ROI']['coordinateBoxes'].append(dictionary[key].dict['coordinateBoxes'])
                self.dict['ROI']['coordinateBoxesNumPy'].append([])
                self.dict['ROI']['coordinateCenter'].append([])
            
                for idx,boxList in enumerate(self.dict['ROI']['coordinateBoxes'][-1]):
                   self.dict['ROI']['coordinateBoxesNumPy'][-1].append(np.int0(boxList['box']))
                   self.dict['ROI']['coordinateCenter'][-1].append(boxList['center'])
                   self.dict['ROI']['coordinatesX'][-1].append(boxList['X'])
                   self.dict['ROI']['coordinatesY'][-1].append(boxList['Y'])
                   self.dict['ROI']['cX'][-1].append(boxList['cX'])
                   self.dict['ROI']['cY'][-1].append(boxList['cY'])

            else:   
                self.dict['ROI']['coordinatesX'].append([]) 
                self.dict['ROI']['coordinatesY'].append([]) 
                self.dict['ROI']['cX'].append([]) 
                self.dict['ROI']['cY'].append([]) 
                self.dict['ROI']['coordinateBoxes'].append([])
                self.dict['ROI']['coordinateBoxesNumPy'].append([]) 
                self.dict['ROI']['coordinateCenter'].append([])
                self.dict['ROI']['coordinatesToggle'].append(False)       
    
    def addExclusion(self,zone):     
            
        self.exclusionBox_tl = np.int0([zone.dict['topLeft']['value']])  #lowerleft
        self.exclusionBox_br = np.int0([zone.dict['bottomRight']['value']])  # upper-right

    def addGaze(self,name):
        
        self.dict['Gaze'] = name

    def renderROIs(self,frame):
        
        if len(self.dict['ROI']['movement']) == 0: self.dict['ROI']['movement'] =self.dict['ROI']['hand']
        if len(self.dict['ROI']['hand']) == 0: self.dict['ROI']['hand'] =self.dict['ROI']['movement']

        ####render bins
        for idx,ROI in enumerate(self.dict['ROI']['box']):

            if self.dict['ROI']['coordinatesToggle'][idx]: 
                cv2.drawContours(frame,self.dict['ROI']['coordinateBoxesNumPy'][idx],-1,(100,100,100),1)
            
            if self.dict['ROI']['hand'][idx]: 
                cv2.drawContours(frame,[self.dict['ROI']['displayBoxHand'][idx]],0,(255,255,255),1)

            if  self.dict['ROI']['gaze'][idx]: 
                cv2.drawContours(frame,[self.dict['ROI']['displayBoxGaze'][idx]],0,(255,255,255),1)

            rgb = (255,255,255)
            cv2.drawContours(frame,[ROI],0,rgb,1)
            cv2.putText(frame, self.dict['ROI']['name'][idx] ,self.dict['ROI']['center'][idx], cv2.FONT_HERSHEY_SIMPLEX, 0.35, rgb, 1)

        ####render boundingbox       
        for idx,cnt in enumerate(self.dict['contours']['minBoundingBox']):
            if idx > len(self.dict['contours']['color'])-1:
                print('azz')

            rgb = self.dict['contours']['color'][idx]
            box = cv2.boxPoints(cnt)
            box = np.int0(box)
            cv2.drawContours(frame,[box],0,rgb,1)
            cv2.putText(frame, self.dict['contours']['type'][idx] ,(box[0][0]-10,box[0][1]+20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, rgb, 1)
        
        ####render blocks  
        for idx,blockName in enumerate(self.dict['persistentModel']): 
            cnt = self.dict['persistentModel'][blockName]['minBBox']
            coordinates = self.dict['persistentModel'][blockName]['coordinatesIndexes']
            ROIindex = self.dict['persistentModel'][blockName]['ROIindex']

            if not(cnt ==''):
                rgb = self.dict['persistentModel'][blockName]['color']
                box = cv2.boxPoints(cnt)
                box = np.int0(box)
                thickenss = 3 if self.dict['persistentModel'][blockName]['blocked'] else 2
                cv2.drawContours(frame,[box],0,rgb,thickenss)
                cv2.putText(frame,blockName.replace("blocco","") ,(box[1][0]-10,box[1][1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, rgb, 1)
            
                if not(self.dict['persistentModel'][blockName]['positionList']==[]): 
                    lenght = len(self.dict['persistentModel'][blockName]['positionList']) - 1     
                    for index,item in enumerate(self.dict['persistentModel'][blockName]['positionList']):
                        try:
                            if index == lenght:break
                            item2 = self.dict['persistentModel'][blockName]['positionList'][index+1]              
                            cv2.circle(frame, (item[0],item[1]), 1 , rgb, 2)
                            cv2.line(frame,(item[0],item[1]),(item2[0],item2[1]),rgb,2)
                        except Exception as e: print(e)


        self.dict['oldContours'] = copy.copy(self.dict['contours'])
        self.dict['oldContoursExist'] = True
        self.dict['contours']={'contours':[],'color':[],'type':[],'boundingBox':[],'minBoundingBox':[],'areas':[],'ROI':[],'center':[],'ROImovement':[],'ROIhand':[],'ROIindex':[],'movement':[]}
        

        return frame

    def movementDetection(self,bckSub):
        
        self.dict['ROI']['movement']=[]
        
        for idx,ROI in enumerate(self.dict['ROI']['box']): 
            imgROI = bckSub[ ROI[0][1]:ROI[2][1],ROI[0][0]:ROI[2][0]]                 
            count = cv2.countNonZero(imgROI)
            if count>0: self.dict['ROI']['movement'].append(True)
            else: self.dict['ROI']['movement'].append(False)
        
    def handDetection(self,handPos,handCoordinates):
       
        self.dict['ROI']['hand']=[]
        
        for idx,ROI in enumerate(self.dict['ROI']['box']): 
            imgROI = handPos[ ROI[0][1]:ROI[2][1],ROI[0][0]:ROI[2][0]]                 
            count = cv2.countNonZero(imgROI)
            if count>0: self.dict['ROI']['hand'].append(True)
            else: self.dict['ROI']['hand'].append(False)
            if not(handCoordinates==0):
                self.dict['handCoordinatesX'] = np.append(self.dict['handCoordinatesX'],handCoordinates[0] ) 
                self.dict['handCoordinatesY'] = np.append(self.dict['handCoordinatesY'],handCoordinates[1] )
                self.dict['handCoordinatesTimestamp'] = np.append(self.dict['handCoordinatesTimestamp'],self.getStampNum() )    

    def gazeDetection(self):
        
        if not 'Gaze' in self.dict: return

        gazeList = self.dict['Gaze'].getTrsfmGaze()      

        try:
            gazeList
            point  = np.mean(gazeList,0)
            
            self.dict['GazeCoordinatesX'] = np.append(self.dict['GazeCoordinatesX'],gazeList[:,0] ) 
            self.dict['GazeCoordinatesY'] = np.append(self.dict['GazeCoordinatesY'],gazeList[:,1] )
            stmpN = self.getStampNum()
            self.dict['GazeCoordinatesTimestamp'] = np.append(self.dict['GazeCoordinatesTimestamp'],[ stmpN for gaze in gazeList] )  
            
            for idx,path in enumerate(self.dict['ROI']['path']):
                if path.contains_points([point]): 
                    self.dict['ROI']['gaze'][idx]=True
                    if self.dict['ROI']['blockname'][idx]: 
                        self.dict['GazeLocation'].append(self.dict['ROI']['blockname'][idx])
                        self.dict['GazeLocationTimestamp'] = np.append(self.dict['GazeLocationTimestamp'],stmpN)
                    else: 
                        self.dict['GazeLocation'].append(self.dict['ROI']['name'][idx])
                        self.dict['GazeLocationTimestamp'] = np.append(self.dict['GazeLocationTimestamp'],stmpN)
                else: 
                    self.dict['ROI']['gaze'][idx] = False 
                  
        except Exception as e:
            
            for idx,path in enumerate(self.dict['ROI']['path']):self.dict['ROI']['gaze'][idx] = False 

    def plottest(self):
        
        n = 50  # the larger n is, the smoother curve will be
        b = [1.0 / n] * n
        a = 1
        handCoordinatesX = lfilter(b,a,self.dict['handCoordinatesX'][1:])
        GazeCoordinatesX = self.dict['GazeCoordinatesX']
        
        #### RAW DATA
        plt.figure(1)
        plt.subplot(311)
        
        plt.ylabel('X movment Raw')

        plt.plot(self.dict['handCoordinatesTimestamp'][1:],handCoordinatesX , 'k--', linewidth=0.2)
        plt.plot(self.dict['GazeCoordinatesTimestamp'],GazeCoordinatesX , 'k--', linewidth=0.4)

        self.dict['colorPlot']={'blocco1':'r',
                                'blocco2':'b',
                                'blocco3':'g',                              
                                'blocco4':'y',
                                'blocco5':'b',
                                'blocco6':'g',
                                'blocco7':'y',
                                'blocco8':'r',
                                'areaFirst':'k',
                                'areaSecond':'k',
                                'first':'k',
                                'second':'k',
                                'third':'k',
                                'fourth':'k',
                                'fifth':'k',
                                'sixth':'k',
                                'seventh':'k',
                                'eight':'k',
                                'Model':'K'    
                                }


        for idx,movement in enumerate(self.dict['movements']):
            plt.plot(self.dict['movementsStamps'][idx],self.dict['movements'][idx][:,0],  self.dict['colorPlot'][self.dict['movementsBlocks'][idx]])
        
        xmax = self.dict['GazeCoordinatesTimestamp'][-1] if self.dict['GazeCoordinatesTimestamp'][-1]>self.dict['handCoordinatesTimestamp'][-1] else self.dict['handCoordinatesTimestamp'][-1]

        plt.xlim([0,xmax+0.2])

        #### GAZE
        plt.subplot(312)
        plt.grid(True)
        
        # Set the ticks and labels 
        ticks = np.arange(-0.2,11.8, 1)
        labels = np.flip(np.array(['B8','B7','B6','B5','B4','B3','B2','B1','M','R','W2','W1']),0)
        plt.yticks(ticks, labels)
        plt.ylabel('Gaze')
        plt.ylim([0,15])

        self.dict['BlockPlot']={'areaFirst':0,
                                'areaSecond':1,
                                'first':2,
                                'second':2,
                                'third':2,
                                'fourth':2,
                                'fifth':2,
                                'sixth':2,
                                'seventh':2,
                                'eight':2,
                                'Model':3,
                                'blocco1':4,
                                'blocco2':5,
                                'blocco3':6,                              
                                'blocco4':7,
                                'blocco5':8,
                                'blocco6':9,
                                'blocco7':10,
                                'blocco8':11,
                                 }
        
        gazeLocation = [ self.dict['BlockPlot'][item] for item in self.dict['GazeLocation'] ]
        lastLocation = ''
        secondpointbool=False
        firstpointbool=False
        SubtaskArray = []

        for idx,Location in enumerate(gazeLocation):
            if lastLocation == Location: continue
            elif firstpointbool==False:
                stamps=[]
                lastLocation = Location
                firstpointbool=True
                stamps.append(self.dict['GazeLocationTimestamp'][idx])
            elif secondpointbool==False:
                secondpointbool=True
                stamps.append(self.dict['GazeLocationTimestamp'][idx-1])
            else:
                SubtaskArray.append([np.array(stamps),np.array([lastLocation,lastLocation]),self.dict['colorPlot'][self.dict['GazeLocation'][idx-2]]])
                secondpointbool=False
                stamps=[]
                stamps.append(self.dict['GazeLocationTimestamp'][idx])
                lastLocation = Location

        ticks2=np.array([])
        labels2=np.array([])
        for gaze in SubtaskArray:
            ticks2 = np.append(ticks2,gaze[0])
            labels2 = np.append(labels2,[''])
            plt.plot(gaze[0],gaze[1],gaze[2], linewidth=5, linestyle='dashed',dashes=(0.2,0.1), solid_capstyle='butt' )

        plt.xlim([0,xmax+0.2])
        plt.xticks(ticks2,labels2)
        
        #### MOVEMENT
        plt.subplot(313)
        plt.grid(True)
        
        ticks = np.arange(-0.2,11.8, 1)
        labels = np.flip(np.array(['B8','B7','B6','B5','B4','B3','B2','B1','M','R','W1','W2']),0)
        plt.yticks(ticks, labels)
        plt.ylabel('Movement')
        plt.ylim([0,15])
        
        MovementArray = []
        for idx,movment in enumerate(self.dict['movements']):
            stamps = np.array([self.dict['movementsStamps'][idx][0],self.dict['movementsStamps'][idx][-1]])
            block = np.array([self.dict['BlockPlot'][self.dict['movementsBlocks'][idx]],self.dict['BlockPlot'][self.dict['movementsBlocks'][idx]]])
            color = self.dict['colorPlot'][self.dict['movementsBlocks'][idx]]
            MovementArray.append([stamps,block,color])

        ticks = ticks2
        labels = labels2
        
        for move in MovementArray:
            ticks = np.append(ticks,move[0])
            labels = np.append(labels,[''])
            plt.plot(move[0],move[1],move[2], linewidth=5,  solid_capstyle='butt' )
        
        plt.xlim([0,xmax+0.2])
        plt.xticks(ticks,labels)

        #### PROCEDURE
        ##############
        # plt.subplot(514)
        # plt.grid(True)
        
        # ticks = np.arange(0,3, 1)
        # labels = np.flip(np.array(['Correct','Error','']),0)
        # plt.yticks(ticks, labels)
        # plt.ylabel('Procedure')

        # Procedure = []
        # for idx,taskName in enumerate(self.dict['proceduralTask']):
            
        #     if idx>len(self.dict['movementsStamps'])-1: continue

        #     if 'associatedMovement' in self.dict['proceduralTask'][taskName]:
        #         index = self.dict['proceduralTask'][taskName]['associatedMovement']
        #         taskNumber = [1,1]    
        #         color = 'g'     
        #     else:
        #         index = idx
        #         taskNumber = [0,0]
        #         color= 'r'

        #     if index < 1: stamps = np.array([0,self.dict['movementsStamps'][index][-1]])
        #     else: stamps = np.array([self.dict['movementsStamps'][index-1][-1],self.dict['movementsStamps'][index][-1]])
           
        #     gazebool = [ True if gaze>stamps[0] and gaze<stamps[1] else False for idx,gaze in enumerate(self.dict['GazeLocationTimestamp']) ]
            
        #     GazeLocationTimestamp = self.dict['GazeLocationTimestamp'][gazebool]
        #     GazeLocationName = np.array(self.dict['GazeLocation'])[gazebool]
        #     GazeLocation = [ self.dict['BlockPlot'][item] for item in GazeLocationName ]

        #     lastLocation = ''
        #     secondpointbool=False
        #     firstpointbool=False
        #     SubtaskArray = []

        #     for idx2,Location in enumerate(GazeLocation):
        #         if lastLocation == Location: continue
        #         elif firstpointbool==False:
        #             subtaskstamps=[]
        #             lastLocation = Location
        #             firstpointbool=True
        #             subtaskstamps.append(GazeLocationTimestamp[idx2])
        #         elif secondpointbool==False:
        #             secondpointbool=True
        #             subtaskstamps.append(GazeLocationTimestamp[idx2-1])
        #         else:
        #             correctWrong = 2 if self.dict['proceduralTask'][taskName]['block'] == GazeLocationName[idx2-2] or GazeLocationName[idx2-2] == 'areaFirst' else 1
        #             if not GazeLocationName[idx2-2] == 'areaFirst': SubtaskArray.append([np.array(subtaskstamps),correctWrong])
        #             secondpointbool=False
        #             subtaskstamps=[]
        #             subtaskstamps.append(GazeLocationTimestamp[idx2])
        #             lastLocation = Location

        #     movmentStamps = np.array([self.dict['movementsStamps'][idx][0],self.dict['movementsStamps'][idx][-1]])
        #     correctWrong = 2 if self.dict['proceduralTask'][taskName]['block'] == self.dict['movementsBlocks'][index] else 1
        #     SubtaskArray.append([np.array(movmentStamps),correctWrong])

        #     Procedure.append([stamps,taskNumber,color,SubtaskArray])
                
        # ticks = np.array([])
        # labels = np.array([])
        # correct = []
        # wrong = []
        # indexCorrect = []
        # indexWrong = []
        # widthWrong = []
        # widthCorrect = []

        # for idx,task in enumerate(Procedure):

        #     ticks = np.append(ticks,task[0][1])
        #     labels = np.append(labels,['',''])

        #     if task[2]=='g': 
        #         correct.append(2)
        #         indexCorrect.append(np.average(task[0])) 
        #         widthCorrect.append(task[0][1]-task[0][0])  
        #     else: 
        #         wrong.append(1)
        #         indexWrong.append(np.average(task[0]))   
        #         widthWrong.append(task[0][1]-task[0][0])

        # plt.bar(indexCorrect, correct, widthCorrect, color='g')
        # plt.bar(indexWrong, wrong, widthWrong, color='r')

        # plt.ylim([0,4])        
        # plt.xlim([0,xmax+0.2])
        # plt.xticks(ticks,labels)

        # #### PROCEDURE
        # ##############
        # plt.subplot(515)
        # plt.grid(True)
        
        # ticks = np.arange(0,3, 1)
        # labels = np.flip(np.array(['Correct','Error','']),0)
        # plt.yticks(ticks, labels)
        # plt.ylabel('Procedure')
            
        # ticks = np.array([])
        # labels = np.array([])
        # correct = []
        # wrong = []
        # indexCorrect = []
        # indexWrong = []
        # widthWrong = []
        # widthCorrect = []

        # for task in Procedure:
        #     SubtaskArray = task[3]
        #     for subtask in SubtaskArray:
        #         ticks = np.append(ticks,subtask[0])
        #         labels = np.append(labels,['',''])
                
        #         if subtask[1]==2: 
        #             correct.append(2)
        #             indexCorrect.append(np.average(subtask[0])) 
        #             widthCorrect.append(subtask[0][1]-subtask[0][0])  
        #         else: 
        #             wrong.append(1)
        #             indexWrong.append(np.average(subtask[0])) 
        #             widthWrong.append(subtask[0][1]-subtask[0][0])  

        # plt.bar(indexCorrect, correct, widthCorrect, color='g')
        # plt.bar(indexWrong, wrong, widthWrong, color='r')

        # plt.ylim([0,4])        
        # plt.xlim([0,xmax+0.2])
        # plt.xticks(ticks,labels)

        ##RENDER ALL
        plt.show()

    def detectMinBoundingBoxes(self):

        for idx,cnt in enumerate(self.dict['contours']['contours']):
            self.dict['contours']['minBoundingBox'][idx]= cv2.minAreaRect(cnt)
            
    def detectType(self):
        
        for idx,area in enumerate(self.dict['contours']['areas']):
            if area < self.dict['AreaBottomBound']['value'] : self.dict['contours']['type'][idx]=('difficult to say')  
            elif area < self.dict['B2x1']['value'] : self.dict['contours']['type'][idx]=('B2x1')
            elif area < self.dict['B2x2']['value'] : self.dict['contours']['type'][idx]=('B2x2')
            elif area < self.dict['B2x4']['value'] : self.dict['contours']['type'][idx]=('B2x4')
            else: self.dict['contours']['type'].append('larger than 2x3')
    
    def sizeFiltering(self):
        
        for idx,c in enumerate(self.dict['contours']['contours']):
            if ((self.dict['contours']['areas'][idx] > self.dict['AreaTopBound']['value']) or  
               (self.dict['contours']['areas'][idx] < self.dict['AreaBottomBound']['value'])): 
                self.setContoursToRemove(idx)  

        self.removeContours()  
    
    def adjustBlockPosInWa(self,blockName,idx):
        
        block = self.dict['persistentModel'][blockName]
        if not(self.dict['contours']['ROI'][idx]=='areaFirst' or self.dict['contours']['ROI'][idx]=='areaSecond'): return
        #elif not(block['blocked']):return
        elif self.dict['contours']['ROIhand'][idx]:return
        
        a=1
        b=2
        betterRatio = False
        betterOrientation = False
        betterArea = False
        sameArea = False

        #check area distance
        e = (int( abs(block['area'] - self.dict[block['type']]['value']) ) /10 )*10
        f = ( int(abs(self.dict['contours']['areas'][idx] - self.dict[block['type']]['value']))/10)*10
        betterArea = f<e
        sameArea = f==e
           
        #check orientation and edge ratio         
        if (block['type']=='B2x1' or block['type']=='B2x4'):
            if abs(block['minBBox'][2])>45:
                a = 0.5 - abs(block['minBBox'][1][0] / block['minBBox'][1][1])
                b = 0.5 - abs(self.dict['contours']['minBoundingBox'][idx][1][0] / self.dict['contours']['minBoundingBox'][idx][1][1])
                betterRatio = a-b>0.15
                c = abs(block['minBBox'][2])
                d = abs(self.dict['contours']['minBoundingBox'][idx][2])
                betterOrientation = c-d<0
            elif abs(block['minBBox'][2])<45:   
                a = 2 - abs(block['minBBox'][1][0] / block['minBBox'][1][1])
                b = 2 - abs(self.dict['contours']['minBoundingBox'][idx][1][0] / self.dict['contours']['minBoundingBox'][idx][1][1])
                betterRatio = a-b>0.15
                c = abs(block['minBBox'][2])
                d = abs(self.dict['contours']['minBoundingBox'][idx][2])
                betterOrientation = c-d>0
        elif block['type']=='B2x2':
            a = 1 - abs(block['minBBox'][1][0] / block['minBBox'][1][1])
            b = 1 - abs(self.dict['contours']['minBoundingBox'][idx][1][0] / self.dict['contours']['minBoundingBox'][idx][1][1])
            betterRatio = a-b>0.15
            c = abs(block['minBBox'][2])
            d = abs(self.dict['contours']['minBoundingBox'][idx][2])
            betterOrientation = c-d<0 if abs(block['minBBox'][2])>45 else c-d>0

        if (((betterRatio or betterOrientation) and sameArea) or betterArea): 
            self.applyBlock(blockName,idx)
            block['adjusted']=True

    def setContoursToRemove(self,idx):

        self.dict['contours']['contours'][idx]='remove'
        self.dict['contours']['areas'][idx]='remove'
        self.dict['contours']['color'][idx]='remove'
        self.dict['contours']['center'][idx]='remove'
        self.dict['contours']['ROI'][idx]='remove'
        self.dict['contours']['ROImovement'][idx]='remove'
        self.dict['contours']['ROIhand'][idx]='remove'
        self.dict['contours']['ROIindex'][idx]='remove'
        self.dict['contours']['type'][idx]='remove'
        self.dict['contours']['movement'][idx]='remove'
        self.dict['contours']['minBoundingBox'][idx]='remove'

    def removeContours(self):

        self.dict['contours']['contours'][:] = [item for item in self.dict['contours']['contours'] if item != 'remove']
        self.dict['contours']['areas'][:] = [item for item in self.dict['contours']['areas'] if item != 'remove']
        self.dict['contours']['color'][:] = [item for item in self.dict['contours']['color'] if item != 'remove']
        self.dict['contours']['center'][:] = [item for item in self.dict['contours']['center'] if item != 'remove']
        self.dict['contours']['ROI'][:] = [item for item in self.dict['contours']['ROI'] if item != 'remove']
        self.dict['contours']['ROImovement'][:] = [item for item in self.dict['contours']['ROImovement'] if item != 'remove']
        self.dict['contours']['ROIhand'][:] = [item for item in self.dict['contours']['ROIhand'] if item != 'remove']
        self.dict['contours']['ROIindex'][:] = [item for item in self.dict['contours']['ROIindex'] if item != 'remove']
        self.dict['contours']['type'][:] = [item for item in self.dict['contours']['type'] if item != 'remove']
        self.dict['contours']['movement'][:] = [item for item in self.dict['contours']['movement'] if item != 'remove']
        self.dict['contours']['minBoundingBox'][:] = [item for item in self.dict['contours']['minBoundingBox'] if item != 'remove']

    def detectPosition(self):
        
        if len(self.dict['contours']['contours']) > 0:
            
            index = 0
            
            for bin in self.dict['ROI']['box']:
                
                ll = bin[0]  # lowerleft
                ur = bin[2]  # upper-right

                inidx = np.all(np.logical_and(ll <= self.dict['contours']['center'], self.dict['contours']['center'] <= ur), axis=1)
                nonZeroIndex = np.nonzero(inidx)
                if len(nonZeroIndex[0])>0 : 
                    for idx in nonZeroIndex[0]:
                         self.dict['contours']['ROI'][idx] =  self.dict['ROI']['name'][index]
                         self.dict['contours']['ROIindex'][idx] = index
                         self.dict['contours']['ROIhand'][idx] = self.dict['ROI']['hand'][index]
                         self.dict['contours']['ROImovement'][idx]= self.dict['ROI']['movement'][index]
                index += 1

    def PMcompute(self):

        for blockName in self.dict['persistentModel']:
            
            block = self.dict['persistentModel'][blockName] 
            
            if len(block['ROIHistory'])>3:
                a = block['ROIHistoryTimeStamp'][-1]
                b = block['ROIHistoryTimeStamp'][-2]
                if a-b<2:
                    block['ROIHistoryTimeStamp'][-2] = block['ROIHistoryTimeStamp'][-1]
                    block['ROIHistory'][-2] = block['ROIHistory'][-1]
                    del block['ROIHistoryTimeStamp'][-1]
                    del block['ROIHistory'][-1]

            if block['adjusted']:
                block['ROIHistory'][-1] = block['ROI']
                block['checkProcedure'] = True
                block['adjusted']=False
                continue
            
            if not(block['ROI']=='undetected'):
                if not(block['ROIHistory'][-1:]==[block['ROI']]): 
                    block['ROIHistory'].append(block['ROI'])
                    block['ROIHistoryTimeStamp'].append(self.getStampNum())
                    block['checkProcedure'] = True
                else: block['checkProcedure'] = False
                if not(block['ROI']==block['lastDtcROI']): 
                    block['lastROI'] = block['lastDtcROI'] 
                block['lastDtcROI'] = block['ROI']

            block['ROI'] = 'undetected'

    def twoPDistance(self,point1,point2):
        
        distance = np.linalg.norm(np.float32(point1)-np.float32(point2))
        
        return distance
    
    def convertPersModToNP(self):

        self.persMod = np.array([ [key,
            block['color'][0],
            block['color'][1],
            block['color'][2],
            block['colorName'],
            block['type'],
            block['ROI'],
            block['lastROI'],
            block['lastDtcROI'],
            block['movement'],
            block['minBBox'],
            block['oldMinBBox'],
            block['center'],
            block['contoursID'],
            block['ROIHistory'],
            block['coordinatesIndexes'],
            block['coordinatesFirst'],
            block['coordinatesLast'],
            block['ROIindex'],
            block['checkProcedure'],
            block['blocked'],
            block['positionList'],
            block['timeList'],
            block['deleteList']] for (key,block) in self.dict['persistentModel'].items()],dtype=object)
   
    def removeContoursInExclusionZone(self):

        if len(self.dict['contours']['center'])>0:
            inidx = np.all(np.logical_and(self.exclusionBox_tl <= self.dict['contours']['center'], self.dict['contours']['center'] <= self.exclusionBox_br), axis=1)
            #deleteIndexes = np.nonzero(inidx)[0]
            deleteIndexes = np.nonzero(inidx==False)[0]

            if len(deleteIndexes)>0:

                for idx in deleteIndexes:    
                    self.setContoursToRemove(idx) 
                    removeQuestion = True
                    
                self.removeContours()  

    def removeContoursInBlockedBlocks(self):

        for blockName in self.dict['persistentModel']:
            value = 1
            #if not(self.dict['persistentModel'][blockName]['blocked']): continue
            
            if self.dict['blockInMovement']==blockName:continue
            if not(self.dict['persistentModel'][blockName]['blocked']): value = 1          
            block = self.dict['persistentModel'][blockName]
            if block['minBBox']=='': continue
            block['deletedContourn']=False

            removeQuestion = False
       
            if abs(block['minBBox'][2])<45:
                halfW = np.divide(block['minBBox'][1][0],2) 
                halfH = np.divide(block['minBBox'][1][1],2)
            else:
                halfW = np.divide(block['minBBox'][1][1],2)
                halfH = np.divide(block['minBBox'][1][0],2)

            ll = np.int0([block['minBBox'][0][0]-halfW/value,block['minBBox'][0][1]-halfH/value])  #lowerleft
            ur = np.int0([block['minBBox'][0][0]+halfW/value,block['minBBox'][0][1]+halfH/value])  # upper-right

            if len(self.dict['contours']['center'])>0:
                inidx = np.all(np.logical_and(ll <= self.dict['contours']['center'], self.dict['contours']['center'] <= ur), axis=1)
                deleteIndexes = np.nonzero(inidx)[0]

                if len(deleteIndexes)>0: 
                    block['deletedContourn']=True

                for idx in deleteIndexes:
                    sameColor = self.dict['contours']['color'][idx] == block['color']
                    if sameColor:
                        self.adjustBlockPosInWa(blockName,idx) 
                        self.setContoursToRemove(idx) 
                        removeQuestion = True
                        
            if removeQuestion: self.removeContours()  

    def PMassociateDetectedAndExpectedMultiple(self):
        
        for idx,contours in enumerate(self.dict['contours']['contours']):  
           
            cntHndMvmnt = self.dict['contours']['ROIhand'][idx]
            cntMvmnt = self.dict['contours']['ROImovement'][idx] 
            cntRoiUndt = self.dict['contours']['ROI'][idx] == 'undetected'
            
            for blockName in self.dict['persistentModel']:
                
                block = self.dict['persistentModel'][blockName]
                sameColor = self.dict['contours']['color'][idx] == block['color']
                
                if not(block['ROI'] == 'undetected'): continue
                elif block['blocked']: continue
                elif not(sameColor): continue
                
                sameType = self.dict['contours']['type'][idx] == block['type']    
                
                distance = 20

                if (sameType and not(cntRoiUndt) and not(cntHndMvmnt) and not(cntMvmnt)): 

                    block['confidence2'] += 1
                    if block['confidence2'] > 5:
                        block['ROI'] = self.dict['contours']['ROI'][idx]
                        block['ROIindex'] = self.dict['contours']['ROIindex'][idx]
                        block['minBBox'] = self.dict['contours']['minBoundingBox'][idx]
                        block['center'] = self.dict['contours']['center'][idx]

                        self.dict['ROI']['blockname'][ self.dict['ROI']['name'].index(block['ROI']) ] = blockName

                        self.calculateCoordinates(idx,blockName)
                        if not(block['positionList'] == []):block['deleteList'] = True
                        block['confidence2']=0
                        break 

                if (cntHndMvmnt or cntMvmnt) :
                     
                    if block['positionList']==[]: 
                        block['positionList'].append(block['center'])
                        block['timeList'].append(self.getStampNum())
                    
                    if block['positionList'][-1]=='' or self.dict['contours']['center'][0] =='': distance =1000
                    else: distance = self.twoPDistance(block['positionList'][-1],self.dict['contours']['center'][0])
                
                    if distance < 5 and sameType:
                        block['confidence1'] += 1
                        if block['confidence1'] > 10:
                            block['ROI'] = self.dict['contours']['ROI'][idx]
                            block['ROIindex'] = self.dict['contours']['ROIindex'][idx]
                            block['minBBox'] = self.dict['contours']['minBoundingBox'][idx]
                            block['center'] = self.dict['contours']['center'][idx]
                            self.calculateCoordinates(idx,blockName)
                            if not(block['positionList'] == []):block['deleteList'] = True
                            block['confidence1']=0
                            break
                    
                    elif sameType:
                        block['confidence1'] += 1
                        if block['confidence1'] > 50:
                            block['ROI'] = self.dict['contours']['ROI'][idx]
                            block['ROIindex'] = self.dict['contours']['ROIindex'][idx]
                            block['minBBox'] = self.dict['contours']['minBoundingBox'][idx]
                            block['center'] = self.dict['contours']['center'][idx]
                            self.calculateCoordinates(idx,blockName)
                            if not(block['positionList'] == []):block['deleteList'] = True
                            block['confidence1']=0
                            break
                 
    def PMassociateDetectedAndExpectedOne(self):

        if self.dict['blockInMovement']=='': 
            for blockName in self.dict['persistentModel']:
                               
                block = self.dict['persistentModel'][blockName]
                sameColor = self.dict['contours']['color'][0] == block['color']                   
                if not(sameColor) or block['blocked']==True :continue
                
                if self.dict['contours']['ROI'][0] == block['lastDtcROI'] : 
                    self.dict['blockInMovement']=blockName
                    block['stopped']=False
                    print(blockName+' on the move')
                    break
            
            if self.dict['blockInMovement']=='':
                for blockName in self.dict['persistentModel']:
                    
                    block = self.dict['persistentModel'][blockName]
                    sameColor = self.dict['contours']['color'][0] == block['color']                   
                    if not(sameColor) or block['blocked']==True :continue
                    
                    if block['deletedContourn']==False: 
                        self.dict['blockInMovement']=blockName
                        block['stopped']=False
                        print(blockName+' on the move')
                        break  
       
        else:

            block = self.dict['persistentModel'][self.dict['blockInMovement']]
            sameColor = self.dict['contours']['color'][0] == block['color'] 

            if not(sameColor):
                block['stopped']
                self.dict['blockInMovement']=''

            elif block['stopped']: 

                if not(block['positionList']==[]): 
                    block['positionList'].append(block['center'])
                    block['timeList'].append(self.getStampNum())
                    
                    distance = self.twoPDistance(block['positionList'][-1],self.dict['contours']['center'][0])
                    sameType = self.dict['contours']['type'][0] == block['type']
                    undetectedROI = self.dict['contours']['ROIindex'][0] == 'undetected'
                    
                    if distance>5 and not(undetectedROI):
                        block['stopped']=False
                        print(self.dict['blockInMovement']+' on the move')

                    elif distance<5 and sameType and not(undetectedROI):
                        block['confidence1']+=1
                        if block['confidence1']>5:                       
                            self.resetBlock(self.dict['blockInMovement'],0)
                            self.dict['blockInMovement']=''
                else:
                    self.dict['blockInMovement']=''

            else:

                if block['positionList']==[]: 
                    block['positionList'].append(block['center'])
                    block['timeList'].append(self.getStampNum())

                if block['positionList'][-1]=='' or self.dict['contours']['center'][0] =='': distance =1000
                else: distance = self.twoPDistance(block['positionList'][-1],self.dict['contours']['center'][0])
               
                sameType = self.dict['contours']['type'][0] == block['type'] 
                undetectedROI = self.dict['contours']['ROIindex'][0] == 'undetected'
                
                if distance<1: block['confidence1']+=5
                elif distance<2: block['confidence1']+=4
                elif distance<3: block['confidence1']+=3
                elif distance<4: block['confidence1']+=2
                elif distance<5: block['confidence1']+=1
                elif distance<6: block['confidence1']-=1
                elif distance<7: block['confidence1']-=2
                elif distance<8: block['confidence1']-=3
                elif distance<9: block['confidence1']-=4
                elif distance<10: block['confidence1']-=5
                else: block['confidence1']=0
                   
                if block['confidence1']>30 and sameType and not(undetectedROI): 
                    block['stopped']=True
                    if not(block['positionList'] == []):block['deleteList'] = True
                    block['confidence1']=0
                    print(self.dict['blockInMovement']+' stopped')
                    self.applyBlock(self.dict['blockInMovement'],0)
                    self.resetBlock(self.dict['blockInMovement'],0)
                
                if block['confidence1']>60 and not(undetectedROI):
                    block['stopped']=True
                    if not(block['positionList'] == []):block['deleteList'] = True
                    block['confidence1']=0
                    print(self.dict['blockInMovement']+' stopped')
                    self.applyBlock(self.dict['blockInMovement'],0)
                    block['confidence1']=0

                else:
                    block['positionList'].append(self.dict['contours']['center'][0])
                    block['timeList'].append(self.getStampNum())

    def applyBlock(self,blockName,idx):

        block = self.dict['persistentModel'][blockName]
        block['ROI'] = self.dict['contours']['ROI'][idx]
        block['ROIindex'] = self.dict['contours']['ROIindex'][idx]
        block['minBBox'] = self.dict['contours']['minBoundingBox'][idx]
        block['area'] = self.dict['contours']['areas'][idx]
        block['center'] = self.dict['contours']['center'][idx]
        self.calculateCoordinates(idx,blockName)
           
    def resetBlock(self,blockName,idx):

        block = self.dict['persistentModel'][blockName]
        if not(block['positionList'] == []):block['deleteList'] = True
        block['confidence1']=0
        block['confidence2']=0
  
    def calculateCoordinates(self,idx,blockName):

        block = self.dict['persistentModel'][blockName]
        
        if self.dict['contours']['ROIindex'][idx]=='undetected': return

        if self.dict['ROI']['coordinatesToggle'][self.dict['contours']['ROIindex'][idx]]:
                            
            listOfCenters = self.dict['ROI']['coordinateCenter'][self.dict['contours']['ROIindex'][idx]] 
            listOfCoordinatesX = self.dict['ROI']['cX'][self.dict['contours']['ROIindex'][idx]]
            listOfCoordinatesY = self.dict['ROI']['cY'][self.dict['contours']['ROIindex'][idx]]

            if abs(block['minBBox'][2])<45:
                halfW = np.divide(block['minBBox'][1][0],2) 
                halfH = np.divide(block['minBBox'][1][1],2)
            else:
                halfW = np.divide(block['minBBox'][1][1],2)
                halfH = np.divide(block['minBBox'][1][0],2)

            ll = np.int0([block['minBBox'][0][0]-halfW,block['minBBox'][0][1]-halfH])  #lowerleft
            ur = np.int0([block['minBBox'][0][0]+halfW,block['minBBox'][0][1]+halfH])  # upper-right

            inidx = np.all(np.logical_and(ll <= listOfCenters, listOfCenters <= ur), axis=1)
            
            try: 
                block['coordinatesIndexes'] = np.nonzero(inidx)[0]
                firstCoordinateIndex = block['coordinatesIndexes'][0]
                lastCoordinateIndex = block['coordinatesIndexes'][-1]
                xF = listOfCoordinatesX[firstCoordinateIndex]
                yF = listOfCoordinatesY[firstCoordinateIndex]
                xL = listOfCoordinatesX[lastCoordinateIndex]
                yL = listOfCoordinatesY[lastCoordinateIndex]
                block['coordinatesFirst'] = [xF,yF]
                block['coordinatesLast'] = [xL,yL]
                block['ROI'] = block['ROI'] +' ' + str(xL) +',' + str(yL) +' ' + str(xF) +',' + str(yF)
            except Exception as e: print(e)

    def cleanPersistentModel(self):

         for blockName in self.dict['persistentModel']:
             block = self.dict['persistentModel'][blockName]
             block['ROI']=''
             block['lastROI']=''
             block['lastDtcROI']=''
             block['movement']=''
             block['minBBox']=''
             block['oldMinBBox']=''
             block['center']=''
             block['contoursID']=''
             block['ROIHistory']=[]
             block['ROIHistoryTimeStamp']=[]
             block['coordinatesIndexes']=[]
             block['coordinatesFirst'] = []
             block['coordinatesLast'] = []
             block['ROIindex'] = []
             block['checkProcedure'] = False
             block['blocked'] = False
             block['positionList'] = []
             block['timeList']=[]
             block['deleteList']=False
             block['confidence1']=0
             block['confidence2']=0
             block['stopped']=True
             block['deletedContourn']=False
             block['area']=0
             block['adjusted']=False

    def getStamp(self): 
        
        timenow  = round(Timestamp.getTime(),2)
        sec = int(timenow)
        milli = int(( timenow - sec ) *100) 
        minutes = int(sec/60)
        stringa = str(minutes) + ':' + str(sec%60)+':'+str(milli)
        return stringa
    
    def getStampNum(self): 
        return Timestamp.getTime()    

    def checkProcederualTask(self):
        
        for blockName in self.dict['persistentModel']:
            block = self.dict['persistentModel'][blockName]
            if block['checkProcedure']:
                for taskName in self.dict['proceduralTask']:
                    task = self.dict['proceduralTask'][taskName]
                    if (task['completed']==False and 
                        task['block']==blockName and
                        task['targetROI']==block['ROIHistory'][-1]):
                        task['completed'] = True
                        block['blocked'] = True
                        task['associatedMovement'] = len(self.dict['movements']) - 1 
                        task['timestamp']=copy.copy(self.dict['movementsStamps'][-1])
                        
    def copyToMovements(self,positionList,timeList,blockName):
        if positionList[0]=='':
            self.dict['movements'].append(np.array(positionList[1:]))
            self.dict['movementsStamps'].append(np.array(timeList[1:]))
        else:
            self.dict['movements'].append(np.array(positionList))
            self.dict['movementsStamps'].append(np.array(timeList))
        self.dict['movementsBlocks'].append(blockName)
        pass
        
    def cleanPositionList(self):

        for blockName in self.dict['persistentModel']:
            block = self.dict['persistentModel'][blockName]       
            if block['deleteList']:                                     
                self.copyToMovements(block['positionList'],block['timeList'],blockName)
                block['positionList'] = []
                block['timeList'] = []
                block['deleteList'] = False                           
                block['lastContourIndex'] = 0

    def cleanProceduralTaskModel(self):
        
        for taskName in self.dict['proceduralTask']:
            task = self.dict['proceduralTask'][taskName]
            task['error'] = False
            task['completed']= False
            task['timestamp']=''
         
    def process(self):

        self.removeContoursInExclusionZone()
        self.sizeFiltering()
        self.detectMinBoundingBoxes()
        self.detectPosition()
        self.removeContoursInBlockedBlocks()       
        self.detectType()
        
        if self.dict['persistentModelToggle']['value']: 
            if len(self.dict['contours']['contours'])>1:self.PMassociateDetectedAndExpectedMultiple()
            elif len(self.dict['contours']['contours'])==1:self.PMassociateDetectedAndExpectedOne()
            self.PMcompute()
        else: self.cleanPersistentModel()
        
        if self.dict['procedureToggle']['value']:
            self.cleanPositionList()
            self.checkProcederualTask()           
        else: self.cleanProceduralTaskModel()

class eyeTrackerData(base,object):

    def __init__(self,name,object=None):
        super(eyeTrackerData, self).__init__( name )
        if not (object == None): self.referencedObject = object
        self.posAttrList = ['kind','name','path','startstamp','key']
        self.notSave = self.notSave = ['kind','name']
        self.dict['kind'] = 'eyeTrackerData'
        self.dict['timestamp']=[]
        self.dict['framenumber']=[]
        self.dict['posX']=[]
        self.dict['posY']=[] 
        self.dict['Ftimestamp']=[]
        self.dict['Fframenumber']=[]
        self.dict['FposX']=[]
        self.dict['FposY']=[] 
        self.posPrepeared=False

    def initialise(self):

        if 'path' in self.dict: self.loadGazePosition()
        if 'startstamp' in self.dict: self.applyStartStamp()

    def loadGazePosition(self):
        csvfile = open(self.dict['path']+'gaze_positions.csv')
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        boolvar = False
        for row in reader:
            rowlist = row[0].split(',')
            if boolvar:
                self.dict['timestamp'].append(float(rowlist[0]))
                self.dict['framenumber'].append(int(rowlist[1]))
                self.dict['posX'].append(float(rowlist[3][:10]))
                self.dict['posY'].append(float(rowlist[4][:10])) 
            boolvar = True

    def applyStartStamp(self):
        val = self.dict['startstamp']
        self.dict['timestamp'] = self.dict['timestamp'][val:]
        self.dict['framenumber'] = self.dict['framenumber'][val:]
        self.dict['framenumber'] = [x - self.dict['framenumber'][0] for x in self.dict['framenumber']]
        self.dict['posX'] = self.dict['posX'][val:]
        self.dict['posY'] = self.dict['posY'][val:]
        pass
        
    def prepearPos(self,frame):
        
        self.currentShape = frame.shape[:2]
        indexes = [i for i,x in enumerate(self.dict['framenumber']) if x==Timestamp.getFrameNumber(self.dict['key'])]
        self.listpos=[]
        self.posPrepeared=True
        
        for index in indexes: 

            posX = int(frame.shape[1]*self.dict['posX'][index])
            posY = abs(int(frame.shape[0]*self.dict['posY'][index])-frame.shape[0])
            self.listpos.append((posX,posY))
            cv2.circle(frame, (posX,posY), 10 , (255,0,0), 2)

    def roiTrimming(self,roi):
        
        if not(self.posPrepeared): return

        try: self.x
        except: self.x, self.y, self.w, self.h = roi
        
        self.listpos = [list((point-[self.x,self.y]).ravel()) for point in np.array(self.listpos)]

        self.currentShape = (self.h,self.w)

    def associateWIthInvMap(self, tuplepoint, invMap):

        try:
             newPoint = invMap[tuplepoint]
        except:
             newPoint = [0,0]
       
        return newPoint

    def changeInPixelMapping(self,invMap):
        
        if not(self.posPrepeared): return

        self.listpos = [self.associateWIthInvMap(tuple(point.ravel()),invMap) for point in np.int32(self.listpos)]

    def associateWithSC(self,point):

         try:  newPoint = [ int(self.mx(point[0].item())) , int(self.my(point[1]).item()) ]
         except: newPoint = [0,0]
         return newPoint 

    def changeInScale(self,values): 

        if not(self.posPrepeared): return

        try: self.mx
        except:
            from scipy.interpolate import interp1d
            self.mx = interp1d([0,self.currentShape[1]],[0,values[0]])
            self.my = interp1d([0,self.currentShape[0]],[0,values[1]])
        
        self.listpos = [ self.associateWithSC(point) for point in self.listpos if point[0]<self.currentShape[1] and point[1]<self.currentShape[0] ]

    def getGaze(self):

        if not(self.posPrepeared): return 

        return self.listpos

    def renderGaze(self,frame):

        if not(self.posPrepeared): return

        for index,point in enumerate(self.listpos):
            cv2.circle(frame, (tuple(point)), 10 , (0,255,0), 2)
            if index==len(self.listpos)-1: break    
            cv2.line(frame,tuple(self.listpos[index]),tuple(self.listpos[index+1]),(0,0,255),2)

        return frame 

class cameraUndistortion(base,object):

    def __init__(self,name,calibrationName,invMap,object=None):
        super(cameraUndistortion, self).__init__( name )
        if not (object == None): self.referencedObject = object
        self.posAttrList = ['kind','name']
        self.notSave = self.notSave = ['kind','name']
        self.dict['kind'] = 'cameraUndistortion'
        self.boolFirstTime=True
        self.h = 720
        self.w = 1280
        self.shape = (self.h,self.w)

        with np.load(calibrationName) as X:
            self.mtx, self.dist, self.rvecs, self.tvecs = [X[i] for i in ('mtx','dist','rvecs','tvecs')]
       
        self.newcameramtx, self.roi=cv2.getOptimalNewCameraMatrix(self.mtx, self.dist, (self.w,self.h), 1, (self.w,self.h))
        self.mapx, self.mapy = cv2.initUndistortRectifyMap(self.mtx, self.dist, None, self.newcameramtx, (self.w,self.h), 5)
        self.x, self.y, self.w, self.h = self.roi

        try: self.invMap = np.load(invMap)
        except Exception as e: 
            import scipy.spatial
            YX = np.indices((720,1280)).swapaxes(0,2).swapaxes(0,1).reshape(-1,2)
            data = np.int32([ [ self.mapx[tuple(point.ravel())] , self.mapy[tuple(point.ravel())] ]for point in YX ])
            tree = scipy.spatial.cKDTree(data)
            XY = np.indices((1280,720)).swapaxes(0,2).swapaxes(0,1).reshape(-1,2)
            self.invMap = np.int32([np.flip(np.unravel_index(tree.query(point)[1],self.shape),0) for point in XY]).reshape(1280,720,2)
            save('invMap',invMap)

    def process(self,frame):

        frame = cv2.remap(frame, self.mapx, self.mapy, cv2.INTER_LINEAR)
        frame = frame[self.y:self.y+self.h, self.x:self.x+self.w]   
        
        return frame

class perspective(base,object):

    def __init__(self,name,object=None):
        super(perspective, self).__init__( name )
        if not (object == None): self.referencedObject = object
        self.posAttrList = ['kind','name','renderCnt','renderCnt','Th/Opening','Threshold1','Threshold2','Erosion','Dilate','AreaTopBound','AreaBottomBound']
        self.notSave = self.notSave = ['kind','name']
        self.dict['kind'] = 'perspective'
        self.orgRect = np.float32([[0,0],[840,0],[840,140],[0,140]]).reshape(-1,1,2)
        self.checkersize=[5,5]
        self.kernel = np.ones((2,2),np.uint8)
        self.shp =np.float32([[0,0],[640,0],[640,480],[0,480],[0,0]])
        self.trnsfPtsBool=False
        self.trgRectBool = False
        self.dict['TargetRect'] = {"value": False,"interface": True,"widget": "button","command": "toggleBoolean"}   
        self.dict['renderCnt'] = {"value": False,"interface": True,"widget": "button","command": "toggleBoolean"}    
        self.dict['Th/Opening'] = {"value": False,"interface": True,"widget": "button","command": "toggleBoolean"}    
        self.dict['Threshold1'] = {'value':180,'interface':True,'widget':'slider','max':255,'min':0}
        self.dict['Threshold2'] = {'value':255,'interface':True,'widget':'slider','max':255,'min':0}
        self.dict['Erosion'] = {'value':1,'interface':True,'widget':'slider','max':10,'min':0}
        self.dict['Dilate'] = {'value':2,'interface':True,'widget':'slider','max':10,'min':0}
        self.dict['AreaTopBound'] = {'value':10000,'interface':True,'widget':'slider','max':20000,'min':0}
        self.dict['AreaBottomBound'] = {'value':0,'interface':True,'widget':'slider','max':20000,'min':0}

    def addGaze(self,gazeObjct):
        self.gazeObject = gazeObjct

    def transformGaze(self):
        
        try: self.gazeObject
        except: return 

        if self.gazeObject and  self.MtrxTimestamp==Timestamp.getTime():
            self.gaze =  np.float32(self.gazeObject.getGaze()).reshape(1,-1,2)
            if len(self.gaze[0])>0:
                self.trnsfGaze = np.int32(cv2.perspectiveTransform(self.gaze,self.invMtrx)).reshape(-1,2)
                self.trnsfGazeTimestamp = Timestamp.getTime()

    def renderTrsfmGaze(self,frame):
        
        try: self.trnsfGaze
        except: return frame

        if self.trnsfGazeTimestamp+0.2>Timestamp.getTime():

            for index,point in enumerate(self.trnsfGaze):
                cv2.circle(frame, (tuple(point)), 10 , (0,255,0), 2)
                if index==len(self.trnsfGaze)-1: break    
                cv2.line(frame,tuple(self.trnsfGaze[index]),tuple(self.trnsfGaze[index+1]),(0,0,255),2)
            
            cv2.putText(frame, 'eye gaze' ,tuple(self.trnsfGaze[-1]), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)

        return frame
    
    def getTrsfmGaze(self):

        try: self.trnsfGaze
        except: return 
        
        if self.trnsfGazeTimestamp+0.2>Timestamp.getTime():
            return self.trnsfGaze

    def addOrgRect(self,points):

        self.orgRect = np.float32(points).reshape(-1,1,2)         

    def addBins(self,bins):

        self.bins = np.float32(bins)
    
    def addwAreas(self,wAreas):

        self.wAreas = np.float32(wAreas)

    def renderAll(self,frame):
        
        if self.stoprendering: return frame

        self.trnsfBins = np.int32(cv2.perspectiveTransform(self.bins,self.Mtrx))
        self.trnsfwAreas = np.int32(cv2.perspectiveTransform(self.wAreas,self.Mtrx))

        cv2.drawContours(frame,self.trnsfBins,-1,(255, 255, 255),1) 
        cv2.drawContours(frame,self.trnsfwAreas,-1,(255, 255, 255),1) 

        return frame

    def draw(self,img,points):

        for idx,vertex in enumerate(points):
        
            if idx < len(points)-1: 
                pointA = tuple(vertex.ravel())
                pointB = tuple(points[idx+1].ravel())
                img = cv2.line(img, pointA, pointB, (0,0,255), 1)
            
        return img

    def simplify(self,cnt):

        epsilon = 0.01*cv2.arcLength(cnt,True)
        approx = cv2.approxPolyDP(cnt,epsilon,True)
        return 4 - len(approx)
    
    def calcMtrx(self,trgRect):
        self.Mtrx = cv2.getPerspectiveTransform(self.orgRect,trgRect)
        self.invMtrx = cv2.getPerspectiveTransform(trgRect,self.orgRect)
        self.MtrxTimestamp = Timestamp.getTime()
        
    def areaCutOut(self,contours):
        
        contourslist = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.dict['AreaTopBound']['value'] and area > self.dict['AreaBottomBound']['value']:
                contourslist.append(cnt)

        return contourslist

    def process(self,frame):
        
        #gray threshold opening contours
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret,th1 = cv2.threshold(gray,self.dict['Threshold1']['value'],self.dict['Threshold2']['value'],cv2.THRESH_BINARY)
        erosion = cv2.erode(th1,self.kernel,iterations = self.dict['Erosion']['value'])
        dilation = cv2.dilate(erosion,self.kernel,iterations = self.dict['Dilate']['value'])
        opening, contours, hierarchy = cv2.findContours(dilation,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours)>0:

            #select contours with larger area
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:4]
            contours = self.areaCutOut(contours)
            contours = sorted(contours, key=self.simplify, reverse=True)

            if len(contours)>1:

                # crop the image
                x,y,w,h = cv2.boundingRect(contours[0])    
                openingtrim = gray[y:y+h, x:x+w]    
                x2,y2,w2,h2 = cv2.boundingRect(contours[1])    
                openingtrim2 = gray[y2:y2+h2, x2:x2+w2]    

                # find circle grid in the cropped image
                ret, corners = cv2.findCirclesGrid(openingtrim, (self.checkersize[0],self.checkersize[1]), None)
                ret2, corners2 = cv2.findCirclesGrid(openingtrim2, (self.checkersize[0],self.checkersize[1]), None)
                self.trgRectBool = False

                if (ret == True) and (ret2 ==True):

                    # uncrop results of circles find on the cropped area 
                    corners = np.add(corners,np.array([x,y],np.float32))
                    corners2 =  np.add(corners2,np.array([x2,y2],np.float32))

                    if not(corners[0][0][0]<corners2[0][0][0]):
                        corners3 = corners
                        corners = corners2
                        corners2 = corners3

                    #target Rect
                    self.trgRect = np.array([corners[4],corners2[0],corners2[20],corners[24]],np.float32)
                    
                    #transformation
                    self.calcMtrx(self.trgRect)

                    self.shp = self.shp.reshape(1,-1,2)
                    self.trnsfPts = cv2.perspectiveTransform(self.shp,self.Mtrx)
                    self.trnsfPts = self.trnsfPts.reshape(-1,2)
                    self.trnsfPtsBool = True
                    self.trgRectBool = True
                    self.lastTimestamp = Timestamp.getTime()
                    self.stoprendering = False
                    self.transformGaze()


        if self.dict['Th/Opening']['value']: frame =  cv2.cvtColor(opening, cv2.COLOR_GRAY2BGR)       
        if self.trnsfPtsBool and self.lastTimestamp+0.2>Timestamp.getTime(): frame= self.draw(frame,self.trnsfPts)
        else: self.stoprendering = True
        if self.dict['renderCnt']['value'] and len(contours)>0:  cv2.drawContours(frame, contours, -1, (0,255,0), 3)
        if self.trgRectBool and self.dict['TargetRect']['value']: frame= self.draw(frame,self.trgRect) 

        return frame

#initialise Timestamp object
############################

Timestamp = timeStamp()
