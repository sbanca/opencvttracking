import os.path
import json
import cv2
import time
import datetime
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
        self.mask = np.zeros((480,640), np.uint8)


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

    
    def drawContours(self): 
        cv2.drawContours(self.frame, self.contours, -1, self.dict['strokeRgb']['value'],self.dict['StrokeThikness']['value'])

    
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
        
        value = self.dict['maxMinPoint']['value']
        most=(0,0)

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
        self.kernel = np.ones((11,11),np.uint8)
    
    
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
        self.posAttrList = ['kind','name','saveButton','topLeft','topRight','bottomLeft','bottomRight','coordinatesToggle','coordinatesX','coordinatesY','coordinateBoxes','translateCoordX','translateCoordY','revTransCoordX','revTransCoordY','cX','cY','startingValueX','startingValueY','reverseValueX','reverseValueY','area']
        self.notSave = self.notSave = ['kind','name','textCenter','box','coordinateBoxesNumPy']
        self.dict['kind'] = 'binbox'
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
        cv2.putText(self.frame, self.dict['name'] ,self.dict['textCenter'], cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
    
        return self.frame

class blocks(base,object):

    def __init__(self,name,object=None):
        super(blocks, self).__init__( name )
        if not (object == None): self.referencedObject = object
        self.posAttrList = ['kind','name','BlockProp','AreaTopBound','AreaBottomBound','2x1','2x2','2x4','blocchi','persistentModelToggle','persistentModel','proceduralTask']
        self.notSave = self.notSave = ['kind','name','contours','oldContours','ROI']
        self.dict['kind'] = 'blocks'
        self.dict['blockInMovement']=''
        self.dict['handPosition']=[]
        
        self.ts = time.time()

        self.dict['ROI'] ={'movementThresold':0,'center':[],'box':[],'name':[],'movement':[],'hand':[],'coordinatesToggle':[],'coordinatesX':[],'coordinatesY':[],'coordinateBoxes':[],'coordinateBoxesNumPy':[],'coordinateCenter':[],'cX':[],'cY':[]}
        self.dict['contours']={'contours':[],'color':[],'type':[],'boundingBox':[],'minBoundingBox':[],'areas':[],'ROI':[],'center':[],'ROImovement':[],'ROIhand':[],'ROIindex':[]}
        self.dict['oldContours']={}

        self.dict['BlockProp'] = ['id','boundingBox','minBoundingBox','center','color','size','positionXY','positionROI']     
        self.dict['AreaTopBound'] = {'value':2000,'interface':False,'widget':'slider','max':10000,'min':0}
        self.dict['AreaBottomBound']={'value':128,'interface':False,'widget':'slider','max':10000,'min':0}
        self.dict['2x1'] = {'value':427,'interface':False,'widget':'slider','max':10000,'min':0}
        self.dict['2x2'] = {'value':769,'interface':False,'widget':'slider','max':10000,'min':0}
        self.dict['2x4'] = {'value':1368,'interface':False,'widget':'slider','max':10000,'min':0}
        self.dict['time'] = {'interface':True,'widget':'text'}
        
        self.dict['blocchi'] = {'interface':True,'widget':'text'}
        self.dict['persistentModelToggle'] = {"value": True,"interface": True,"widget": "button","command": "toggleBoolean"}       
        self.dict['persistentModel']={'blocco1':{'color':[0,255,0],'colorName':'Green','type':'2x1'},
                                     'blocco2':{'color':[0,255,0],'colorName':'Green','type':'2x2'},
                                     'blocco3':{'color':[0,255,0],'colorName':'Green','type':'2x4'},
                                     'blocco4':{'color':[255,0,0],'colorName':'Blue','type':'2x1'},
                                     'blocco5':{'color':[255,0,0],'colorName':'Blue','type':'2x2'},
                                     'blocco6':{'color':[255,0,0],'colorName':'Blue','type':'2x4'},
                                     'blocco7':{'color':[0,0,255],'colorName':'Red','type':'2x1'},
                                     'blocco8':{'color':[0,0,255],'colorName':'Red','type':'2x2'},
                                     'blocco9':{'color':[0,0,255],'colorName':'Red','type':'2x4'},
                                     'blocco10':{'color':[0,255,255],'colorName':'Yellow','type':'2x1'},
                                     'blocco11':{'color':[0,255,255],'colorName':'Yellow','type':'2x2'},
                                     'blocco12':{'color':[0,255,255],'colorName':'Yellow','type':'2x4'}}
        self.cleanPersistentModel()
        self.persMod=[]

        self.dict['task'] = {'interface':True,'widget':'text'}
        self.dict['procedureToggle'] = {"value": True,"interface": True,"widget": "button","command": "toggleBoolean"}
        self.dict['proceduralTask'] = {1:{'block':'blocco10','targetROI':'areaSecond J,16 K,16'},
                                       2:{'block':'blocco3','targetROI':'areaFirst AJ,15 AM,16'},
                                       3:{'block':'blocco6','targetROI':'areaSecond L,14 O,15'},
                                       4:{'block':'blocco7','targetROI':'areaFirst AJ,14 AJ,15'},
                                       5:{'block':'blocco2','targetROI':'areaSecond N,15 O,16'}}
        self.cleanProceduralTaskModel()
        time.clock()

    def addContours(self,contours,color):
        
        for idx,cnt in enumerate(contours):
            try:
                M = cv2.moments(cnt)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                self.dict['contours']['center'].append((cX-10,cY+10))
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
            self.dict['ROI']['movement'].append(False)
            self.dict['ROI']['hand'].append(False)
            self.dict['ROI']['movementThresold'] = (dictionary[key].dict['topRight']['value'][0]-dictionary[key].dict['topLeft']['value'][0])*(dictionary[key].dict['bottomLeft']['value'][1]-dictionary[key].dict['topLeft']['value'][1])/5
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

            

    def renderROIs(self,frame):
        
        if len(self.dict['ROI']['movement']) == 0: self.dict['ROI']['movement'] =self.dict['ROI']['hand']
        if len(self.dict['ROI']['hand']) == 0: self.dict['ROI']['hand'] =self.dict['ROI']['movement']

        for idx,ROI in enumerate(self.dict['ROI']['box']):

            if self.dict['ROI']['coordinatesToggle'][idx]: 
                cv2.drawContours(frame,self.dict['ROI']['coordinateBoxesNumPy'][idx],-1,(100,100,100),1)
                #cv2.drawContours(frame,self.dict['ROI']['coordinateCenter'][idx],-1,(150,150,150),2)
                # for idx2,box in enumerate(self.dict['ROI']['coordinateBoxesNumPy'][idx]):
                #     if self.dict['ROI']['coordinatesX'][idx][idx2]==self.dict['ROI']['coordinatesX'][idx][-1]:
                #         cy = self.dict['ROI']['cY'][idx][idx2] 
                #         center = (self.dict['ROI']['coordinateCenter'][idx][idx2][0],self.dict['ROI']['coordinateCenter'][idx][idx2][1])
                #         cv2.putText(frame, cy , center , cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255, 255, 255), 1)
                #     if self.dict['ROI']['coordinatesY'][idx][idx2]==self.dict['ROI']['coordinatesY'][idx][-1]:
                #         cx = self.dict['ROI']['cX'][idx][idx2] 
                #         center = (self.dict['ROI']['coordinateCenter'][idx][idx2][0],self.dict['ROI']['coordinateCenter'][idx][idx2][1])
                #         cv2.putText(frame,cx , center , cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255, 255, 255), 1)


            if self.dict['ROI']['hand'][idx]: rgb = (0,255,0)
            elif  self.dict['ROI']['movement'][idx]: rgb = (0,0,255)
            else: rgb = (255,255,255)
            cv2.drawContours(frame,[ROI],0,rgb,1)
            cv2.putText(frame, self.dict['ROI']['name'][idx] ,self.dict['ROI']['center'][idx], cv2.FONT_HERSHEY_SIMPLEX, 0.35, rgb, 1)
        
        for idx,cnt in enumerate(self.dict['contours']['minBoundingBox']): 
            rgb = self.dict['contours']['color'][idx]
            box = cv2.boxPoints(cnt)
            box = np.int0(box)
            cv2.drawContours(frame,[box],0,rgb,1)
            #cv2.putText(frame, self.dict['contours']['type'][idx] + ' ' + str(self.dict['contours']['ROI'][idx]) ,(box[0][0]-10,box[0][1]+20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, rgb, 1)
            cv2.putText(frame, self.dict['contours']['type'][idx] ,(box[0][0]-10,box[0][1]+20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, rgb, 1)
        
        for idx,blockName in enumerate(self.dict['persistentModel']): 
            cnt = self.dict['persistentModel'][blockName]['minBBox']
            coordinates = self.dict['persistentModel'][blockName]['coordinatesIndexes']
            ROIindex = self.dict['persistentModel'][blockName]['ROIindex']
            
            for index in coordinates:
                try: cv2.drawContours(frame,[self.dict['ROI']['coordinateBoxesNumPy'][ROIindex][index]],-1,(255,255,255),1)
                except: pass
                # try:
                #     center = self.dict['ROI']['coordinateCenter'][ROIindex][index]
                #     cv2.circle(frame, (center[0],center[1]), 1 , (255,255,255), 2)
                # except: pass
                

            if not(cnt ==''):
                rgb = self.dict['persistentModel'][blockName]['color']
                box = cv2.boxPoints(cnt)
                box = np.int0(box)
                cv2.drawContours(frame,[box],0,rgb,2)
                cv2.putText(frame, str(idx+1) ,(box[1][0]-10,box[1][1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, rgb, 1)
            
                if not(self.dict['persistentModel'][blockName]['positionList']==[]): 
                    lenght = len(self.dict['persistentModel'][blockName]['positionList']) - 1     
                    for index,item in enumerate(self.dict['persistentModel'][blockName]['positionList']):
                        try:
                            if index == lenght:break
                            item2 = self.dict['persistentModel'][blockName]['positionList'][index+1]              
                            cv2.circle(frame, (item[0],item[1]), 1 , rgb, 2)
                            cv2.line(frame,(item[0],item[1]),(item2[0],item2[1]),rgb,2)
                        except Exception as e: print(e)



        
        if len(self.dict['handPosition'])>3:
            cv2.circle(frame, self.dict['handPosition'][-1], 1 , [255,0,0], 2)
            cv2.line(frame,self.dict['handPosition'][-1],self.dict['handPosition'][-2],[255,0,0],2)
            cv2.circle(frame, self.dict['handPosition'][-2], 1 , [255,0,0], 2)
            cv2.line(frame,self.dict['handPosition'][-2],self.dict['handPosition'][-3],[255,0,0],2)
            cv2.circle(frame, self.dict['handPosition'][-3], 1 , [255,0,0], 2)
            cv2.line(frame,self.dict['handPosition'][-3],self.dict['handPosition'][-4],[255,0,0],2)

        self.dict['oldContours'] = copy.copy(self.dict['contours'])
        self.dict['contours']={'contours':[],'color':[],'type':[],'boundingBox':[],'minBoundingBox':[],'areas':[],'ROI':[],'center':[],'ROImovement':[],'ROIhand':[],'ROIindex':[]}
        

        return frame

    def movementDetection(self,bckSub):
        
        self.dict['ROI']['movement']=[]
        
        for idx,ROI in enumerate(self.dict['ROI']['box']): 
            imgROI = bckSub[ ROI[0][1]:ROI[2][1],ROI[0][0]:ROI[2][0]]                 
            count = cv2.countNonZero(imgROI)
            #if count>self.dict['ROI']['movementThresold']: self.dict['ROI']['movement'].append(True)
            if count>0: self.dict['ROI']['movement'].append(True)
            else: self.dict['ROI']['movement'].append(False)
        

    def handDetection(self,handPos,handCoordinates):
       
        self.dict['ROI']['hand']=[]
        
        self.dict['handPosition'].append(handCoordinates)

        for idx,ROI in enumerate(self.dict['ROI']['box']): 
            imgROI = handPos[ ROI[0][1]:ROI[2][1],ROI[0][0]:ROI[2][0]]                 
            count = cv2.countNonZero(imgROI)
            if count>0: self.dict['ROI']['hand'].append(True)
            else: self.dict['ROI']['hand'].append(False)
        

        

    def detectMinBoundingBoxes(self):

        for cnt in self.dict['contours']['contours']:
            self.dict['contours']['minBoundingBox'].append(cv2.minAreaRect(cnt))

    def detectType(self):
        
        for idx,area in enumerate(self.dict['contours']['areas']):
            if area < self.dict['AreaBottomBound']['value'] : self.dict['contours']['type'][idx]=('difficult to say')  
            elif area < self.dict['2x1']['value'] : self.dict['contours']['type'][idx]=('2x1')
            elif area < self.dict['2x2']['value'] : self.dict['contours']['type'][idx]=('2x2')
            elif area < self.dict['2x4']['value'] : self.dict['contours']['type'][idx]=('2x4')
            else: self.dict['contours']['type'].append('larger than 2x3')


    def handFiltering(self,handMask):
        
        pass

    def sizeFiltering(self):
        
        for idx,c in enumerate(self.dict['contours']['contours']):
            if ((self.dict['contours']['areas'][idx] > self.dict['AreaTopBound']['value']) or  
               (self.dict['contours']['areas'][idx] < self.dict['AreaBottomBound']['value'])): 
                self.setContoursToRemove(idx)  

        self.removeContours()  
    
    def setContoursToRemove(self,idx):

        self.dict['contours']['contours'][idx]='remove'
        self.dict['contours']['areas'][idx]='remove'
        self.dict['contours']['color'][idx]='remove'
        self.dict['contours']['center'][idx]='remove'
        self.dict['contours']['ROI'][idx]='remove'
        self.dict['contours']['ROIindex'][idx]='remove'
        self.dict['contours']['type'][idx]='remove'
    
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

    def center(self):
        #positionXY calculate centers from contours
        pass

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

            if not(block['ROI']=='undetected'):
                if not(block['ROIHistory'][-1:]==[block['ROI']]): 
                    block['ROIHistory'].append(block['ROI'])
                    block['checkProcedure'] = True
                else: block['checkProcedure'] = False
                if not(block['ROI']==block['lastDtcROI']): 
                    block['lastROI'] = block['lastDtcROI'] 
                block['lastDtcROI'] = block['ROI']
            if not(block['ROI']==block['lastDtcROI']): 
                block['movement']=True                
            else : 
                block['movement'] = False

            block['ROI'] = 'undetected'

    def twoPDistance(self,point1,point2):
        return abs(point1[0]-point2[0])+abs(point1[1]-point2[1])
    
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

    def PMassociateDetectedAndExpected(self):

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

                if (not(block['center']=='')):       
                    
                    distance = self.twoPDistance(block['center'],self.dict['contours']['center'][idx])

                    if distance < 4: 
                        block['ROI'] = block['ROIHistory'][-1]
                        if not(block['positionList'] == []):block['deleteList'] = True
                        break 


                if (sameType and not(cntRoiUndt) and not(cntHndMvmnt) and not(cntMvmnt)): 
                    
                    block['ROI'] = self.dict['contours']['ROI'][idx]
                    block['ROIindex'] = self.dict['contours']['ROIindex'][idx]
                    block['minBBox'] = self.dict['contours']['minBoundingBox'][idx]
                    block['center'] = self.dict['contours']['center'][idx]
                    self.calculateCoordinates(idx,blockName)
                    if not(block['positionList'] == []):block['deleteList'] = True
                    break 


                if (cntHndMvmnt or cntMvmnt) :
                     
                    if block['positionList']==[]: 
                        block['positionList'].append(block['center'])
                        block['timeList'].append(self.getStamp())
                    
                    distance = self.twoPDistance(block['positionList'][-1],self.dict['contours']['center'][idx])


                    if distance > 10 and distance < 100 :
                        block['positionList'].append(self.dict['contours']['center'][idx])
                        block['timeList'].append(self.getStamp())
                        continue 
                

                    if distance < 10 and (sameType ):
                        block['confidence1'] += 1
                        if block['confidence1'] > 10:
                            block['ROI'] = self.dict['contours']['ROI'][idx]
                            block['ROIindex'] = self.dict['contours']['ROIindex'][idx]
                            block['minBBox'] = self.dict['contours']['minBoundingBox'][idx]
                            block['center'] = self.dict['contours']['center'][idx]
                            self.calculateCoordinates(idx,blockName)
                            if not(block['positionList'] == []):block['deleteList'] = True
                            block['confidence1']=0
                            continue
                                                
                    elif (sameType ):
                        block['confidence3'] += 1
                        if block['confidence3'] > 50:
                            block['ROI'] = self.dict['contours']['ROI'][idx]
                            block['ROIindex'] = self.dict['contours']['ROIindex'][idx]
                            block['minBBox'] = self.dict['contours']['minBoundingBox'][idx]
                            block['center'] = self.dict['contours']['center'][idx]
                            self.calculateCoordinates(idx,blockName)
                            if not(block['positionList'] == []):block['deleteList'] = True
                            block['confidence3']=0
                            continue
                            

  
                

    def applyBlock(self,blockName,idx):

        block = self.dict['persistentModel'][blockName]
        block['ROI'] = self.dict['contours']['ROI'][idx]
        block['ROIindex'] = self.dict['contours']['ROIindex'][idx]
        block['minBBox'] = self.dict['contours']['minBoundingBox'][idx]
        block['center'] = self.dict['contours']['center'][idx]
        self.calculateCoordinates(idx,blockName)
        if not(block['positionList'] == []):block['deleteList'] = True
        block['confidence1']=0
        block['confidence2']=0
        block['confidence3']=0
           

  
    


    def calculateCoordinates(self,idx,blockName):

        block = self.dict['persistentModel'][blockName]

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
             block['confidence3']=0

    def getStamp(self): 
        
        timenow  = round(time.clock(),2)
        sec = int(timenow)
        milli = int(( timenow - sec ) *100) 
        minutes = int(sec/60)
        stringa = str(minutes) + ':' + str(sec%60)+':'+str(milli)
        return stringa

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
                        lunghezz = len(block['positionList'])
                        if block['deleteList']:                            
                            task['timestamp']=copy.copy(block['timeList'][lunghezz-1])
                            block['positionList'] = []
                            block['timeList'] = []
                            block['deleteList'] = False
                        else:
                            task['timestamp']=copy.copy(self.getStamp())

    def cleanPositionList(self):

        for blockName in self.dict['persistentModel']:
            block = self.dict['persistentModel'][blockName]       
            if block['deleteList']:                            
                block['positionList'] = []
                block['timeList'] = []
                block['deleteList'] = False

    def cleanProceduralTaskModel(self):
        
        for taskName in self.dict['proceduralTask']:
            task = self.dict['proceduralTask'][taskName]
            task['error'] = False
            task['completed']= False
            task['timestamp']=''
         
    def process(self):
        
        #self.sizeFiltering()
        self.detectMinBoundingBoxes()
        self.detectType()
        self.detectPosition()
        
        if self.dict['persistentModelToggle']['value']: 
            self.PMassociateDetectedAndExpected()
            self.PMcompute()
        else: self.cleanPersistentModel()
        
        if self.dict['procedureToggle']['value']:
            self.checkProcederualTask()
            self.cleanPositionList()
        else: self.cleanProceduralTaskModel()

        
    
