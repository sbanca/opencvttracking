import os.path
import json
import cv2
import time
import numpy as np
import os.path
import json
import copy


class timingPerformance:

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
        self.posAttrList = ['name','kind','saveButton','config']
        self.notSave = ['name','kind']
        self.dict['saveButton'] = {'interface':True,'widget':'button','command':'saveobject'}

    def config(self, cnf=None, **kw):

        #save each parameter separatly
        for idx,attr in enumerate(self.posAttrList):
            if attr in kw.keys(): 
                self.dict[attr] = kw[attr]
            if not (cnf == None): 
                if attr in cnf.keys(): 
                    self.dict[attr] = cnf[attr]   

        #save a record of the all config string
        if not (kw == None): 
            self.dict['config'] = list(kw.keys())
        if not (cnf == None): 
            self.dict['config'] = list(cnf.keys())
         

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
            if value not in self.notSave:
                newObject[value] = self.dict[value]
        
        if not self.dict['kind'] in existingDict: existingDict[self.dict['kind']] = { }
        if not self.dict['name'] in existingDict[self.dict['kind']]: existingDict[ self.dict['kind'] ][ self.dict['name'] ] = { }
        existingDict[ self.dict['kind'] ][ self.dict['name'] ] =  newObject  


        return existingDict

class HSVMask(base,object):
    
    def __init__(self,name,object=None):
        super(HSVMask, self).__init__( name )
        if not (object == None): self.referencedObject = object
        self.posAttrList = ['kind','name','bottomBoundary','topBoundary','erosion','dilation','blur','minBBoxes','drawMinBBoxes','AreaTopBound','AreaBottomBound','StrokeThikness','strokeRgb','saveButton', 'detect', 'filterC' ,'Contours' ,'drawLabel','trim','boundingBoxIncrement']
        self.notSave = ['kind','name']
        self.dict['kind'] = 'HSVMask'
        self.count=0


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
        mask = cv2.inRange(self.hsvFrame ,bottomBoundary ,topBoundary )
    
        #refine mask
        mask = cv2.dilate(mask, None, iterations= self.dict['dilation']['value']) 
        mask = cv2.erode(mask, None, iterations= self.dict['erosion']['value'])
        
        #result bitwise
        self.detectResult = cv2.bitwise_and( self.frame, self.frame, mask = mask)

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
        self.posAttrList = ['kind','name','saveButton','bckSub']
        self.notSave = self.notSave = ['kind','name']
        self.dict['kind'] = 'bckSub'
        self.fgbg = cv2.createBackgroundSubtractorMOG2()
        # self.dict['opening'] = {'value':5,'interface':True,'widget':'slider','max':255,'min':0}
        # self.dict['openingToggle'] = {'value':True,'interface':True,'widget':'button','command':'toggleBoolean'}
        # self.dict['treshType'] =  {'value':1,'interface':True,'widget':'multibutton','buttonsValues':[0,1,2,3],'buttonsNames':['mean','gaussian','binary','nothresh']}
        # self.dict['value1'] = {'value':255,'interface':True,'widget':'slider','max':255,'min':0}
        # self.dict['value2'] = {'value':127,'interface':True,'widget':'slider','max':127,'min':0}
        # self.dict['blur'] =  {'value':127,'interface':True,'widget':'slider','max':127,'min':0}
        self.kernel = np.ones((10,10),np.uint8)
    
    
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
        self.posAttrList = ['kind','name','saveButton','topLeft','topRight','bottomLeft','bottomRight']
        self.notSave = self.notSave = ['kind','name','textCenter','box']
        self.dict['kind'] = 'binbox'
        self.dict['topLeft'] = {'value':[10,10],'interface':True,'widget':'sliderList','max':[640,480],'min':[0,0],'nameList':['X','Y']}
        self.dict['topRight'] = {'value':[20,10],'interface':True,'widget':'sliderList','max':[640,480],'min':[0,0],'nameList':['X','Y']}
        self.dict['bottomLeft'] = {'value':[10,20],'interface':True,'widget':'sliderList','max':[640,480],'min':[0,0],'nameList':['X','Y']}
        self.dict['bottomRight'] = {'value':[20,20],'interface':True,'widget':'sliderList','max':[640,480],'min':[0,0],'nameList':['X','Y']}

    def render(self,frame):
        
        self.frame = frame
        self.originalFrame = copy.copy(frame)

        self.dict['box'] = np.int0([self.dict['topLeft']['value'],self.dict['topRight']['value'],self.dict['bottomRight']['value'],self.dict['bottomLeft']['value']])
        self.dict['textCenter'] = tuple(self.dict['box'][:2].mean(axis=0, dtype=np.int0))  
        self.dict['textCenter'] = ( self.dict['textCenter'][0]-10, self.dict['textCenter'][1]+10) 
        
        cv2.drawContours(self.frame,[self.dict['box']],0,(255, 255, 255),1)     
        cv2.putText(self.frame, self.dict['name'] ,self.dict['textCenter'], cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
    
        return self.frame

class blocks(base,object):

    def __init__(self,name,object=None):
        super(blocks, self).__init__( name )
        if not (object == None): self.referencedObject = object
        self.posAttrList = ['kind','name']
        self.notSave = self.notSave = ['kind','name']
        self.dict['kind'] = 'blocks'
        self.dict['ROI'] ={'center':[],'box':[],'name':[],'movement':[],'hand':[]}
        self.dict['input'] = []
        self.dict['detctRepr'] = []
        self.dict['persRepr'] = []
        self.dict['BlockProp'] = ['id','boundingBox','minBoundingBox','center','color','size','positionXY','positionROI']     

    def addROI(self,dictionary):
        
        for key in dictionary: 

            box = np.int0([dictionary[key].dict['topLeft']['value'],
                            dictionary[key].dict['topRight']['value'],
                            dictionary[key].dict['bottomRight']['value'],
                            dictionary[key].dict['bottomLeft']['value']])
            
            center = tuple(box[:2].mean(axis=0, dtype=np.int0))
            center = ( center[0]-10,center[1]+10) 

            self.dict['ROI']['box'].append(box) 
            self.dict['ROI']['center'].append(center)
            self.dict['ROI']['name'].append(key)
                
    def renderROIs(self,frame):
        
        if len(self.dict['ROI']['movement']) == 0: self.dict['ROI']['movement'] =self.dict['ROI']['hand']
        if len(self.dict['ROI']['hand']) == 0: self.dict['ROI']['hand'] =self.dict['ROI']['movement']

        for idx,ROI in enumerate(self.dict['ROI']['box']): 
            if self.dict['ROI']['hand'][idx]: rgb = (0,255,0)
            elif  self.dict['ROI']['movement'][idx]: rgb = (0,0,255)
            else: rgb = (255,255,255)
            cv2.drawContours(frame,[ROI],0,rgb,1)
            cv2.putText(frame, self.dict['ROI']['name'][idx] ,self.dict['ROI']['center'][idx], cv2.FONT_HERSHEY_SIMPLEX, 0.35, rgb, 1)
        return frame

    def movementDetection(self,bckSub):
        
        self.dict['ROI']['movement']=[]
        
        for idx,ROI in enumerate(self.dict['ROI']['box']): 
            imgROI = bckSub[ ROI[0][1]:ROI[2][1],ROI[0][0]:ROI[2][0]]                 
            count = cv2.countNonZero(imgROI)
            if count>0: self.dict['ROI']['movement'].append(True)
            else: self.dict['ROI']['movement'].append(False)
        

    def handDetection(self,handPos):
       
        self.dict['ROI']['hand']=[]
        
        for idx,ROI in enumerate(self.dict['ROI']['box']): 
            imgROI = handPos[ ROI[0][1]:ROI[2][1],ROI[0][0]:ROI[2][0]]                 
            count = cv2.countNonZero(imgROI)
            if count>0: self.dict['ROI']['hand'].append(True)
            else: self.dict['ROI']['hand'].append(False)

    def minBoundingBox(self):
        #work out min bbox
        pass    

    def boundingBox(self):
        #work out bounding box based on contours
        pass
    
    def sizeFiltering(self):
        #filter the contours based on area size
        pass

    def renderBlocks(self,frame):    
        #render on a frame
        pass
    
    def center(self):
        #positionXY calculate centers from contours
        pass

    def positionROI(self):
        #calculate in which region of interest the blocks are 
        pass

    def process(self):
        #detected to inform persistent model
        pass