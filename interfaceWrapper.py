import cv2
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from pipeline import pipelinesList, Blocks
import copy
import time
import datetime

ready = True

class interface:

    def __init__(self):
        self.dict = {}
        self.dict['kind'] = 'interface'


    def config(self, cnf=None, **kw):

        if not (kw == None): 
            for attr in kw.keys():
                self.dict[attr] = kw[attr]
        if not (cnf == None): 
            for attr in cnf.keys(): 
                self.dict[attr] = cnf[attr]   

    def initialise(self):
        global ready

        if not self.dict.get('obj'):
            print('please configure obj')
        elif not self.dict.get('pipelines'):
            print('please configure pipeline')
        elif not self.dict.get('media'):
            print('please configure media')

        self.widgets = {}
        self.frames = {}
        self.labels = {}
        self.performance = {} 
        self.cap = {}
        self.frame = {}
        self.frameOriginal = {}
        self.pipelines = {}
        self.originalframe = {}
        self.readyforupdate ={}
        self.blocchiUpdateBool = False
        self.taskUpdateBool = False
        self.timeUpdateBool = False

        self.dict['obj'].dict['speed'] = 1
        self.posWidgets = ['button','slider','dropdown']
        
        for idx,pipeline in enumerate(self.dict['pipelines']):
            self.pipelines['video'+str(idx)]=self.dict['pipelines'][idx]

        for idx,cap in enumerate(self.dict['media']):
            self.cap['video'+str(idx)]=self.dict['media'][idx]

        self.makeWindow()
        self.createFrame('leftFrame',self.window,'LEFT')
        self.createFrame('rightFrame',self.window,'RIGHT')

        for idx,cap in enumerate(self.cap):
            self.graphicsFrame('video'+str(idx))

        self.speedControll()
        self.controlFrame()
        self.createWidgets()
        
        self.show_frame()

        

    def addWidgets(self, cnf=None, **kw):

        for idx,attr in enumerate(self.posWidgets):
            if attr in kw.keys(): 
                self.dict['obj'].dict[attr] = kw[attr]
            if not (cnf == None): 
                if attr in cnf.keys(): 
                    self.dict['obj'].dict[attr] = cnf[attr]   

    def makeWindow(self):
        self.window = Toplevel()
        self.window.wm_title(self.dict['obj'].dict['name'])

    def graphicsFrame(self,name):
        self.createLabelFrame(name,self.frames['leftFrame'],'TOP') 
        self.createLabel(name,self.frames[name]) 
        self.performance[name+'Text'] = StringVar()
        self.performance[name+'Text'].set('performance')
        self.performance[name+'Label'] = ttk.Label(self.frames[name],textvariable=self.performance[name+'Text'])
        self.performance[name+'Label'].pack(side=TOP,padx=10,pady=10)
        
    def speedControll(self):
        self.createLabelFrame('FrameRate',self.frames['leftFrame'],'BOTTOM') 
        self.sliderInterface = Scale(self.frames['FrameRate'],length=300, label='Change speed',showvalue=True,from_=1, to=2000, orient=HORIZONTAL, command=lambda value : self.manage_speed(value)).pack(side=TOP,padx=10,pady=10)   


    def controlFrame(self):
        self.createLabelFrame(self.dict['obj'].dict['name'],self.frames['rightFrame'],'TOP')
        self.createLabelFrame('sliderFrame',self.frames[self.dict['obj'].dict['name']],'LEFT')
        self.createLabelFrame('buttonFrame',self.frames[self.dict['obj'].dict['name']],'LEFT')

        self.widgets['quit'] = ttk.Button(self.frames['buttonFrame'],text='quit')
        self.widgets['quit'].config(command=self.destroy) 
        self.widgets['quit'].pack(side=TOP,padx=10,pady=10)

    def changeVideo(self):
        self.cap.release()
        name = self.widgets['SourceList'].get()
        print('video change to: '+name)
        if name == '0': name =0
        if name == '1': name =1
        self.cap = cv2.VideoCapture(name)

    def createWidgets(self):
        for key in self.dict['obj'].dict.keys():
            if type(self.dict['obj'].dict[key])is dict:
                if 'interface' in self.dict['obj'].dict[key].keys():
                    if self.dict['obj'].dict[key]['interface']:
                        if 'widget' in self.dict['obj'].dict[key].keys():
                            if self.dict['obj'].dict[key]['widget'] == 'slider': self.createSlider(key)
                            elif self.dict['obj'].dict[key]['widget'] == 'sliderList': self.createSliderFromList(key)
                            elif self.dict['obj'].dict[key]['widget'] == 'dropdown': self.createDropdown(key)
                            elif self.dict['obj'].dict[key]['widget'] == 'button': self.createButton(key)
                            elif self.dict['obj'].dict[key]['widget'] == 'entryList': self.createEntryFromList(key)
                            elif self.dict['obj'].dict[key]['widget'] == 'entry': self.createEntry(key)
                            elif self.dict['obj'].dict[key]['widget'] == 'multibutton': self.createMultiButton(key)
                            elif self.dict['obj'].dict[key]['widget'] == 'text':self.createText(key)

    
    def createText(self,key):

        self.widgets[key + 'Text'] = StringVar()
        self.widgets[key + 'Text'].set('text')
        self.widgets[key + 'Label'] = ttk.Label(self.frames['sliderFrame'],textvariable=self.widgets[key+'Text'])
        self.widgets[key + 'Label'].pack(side=TOP,padx=10,pady=10)

        if 'blocchi' in key: self.blocchiUpdateBool = True
        if 'task' in key: self.taskUpdateBool = True
        if 'time' in key: self.timeUpdateBool = True

    def createEntry(self,key):
        
        self.widgets[key] = ttk.Entry(self.frames['sliderFrame'], width=300)
        self.widgets[key].pack(padx=0,pady=0)

        #todo

    def createEntryFromList(self,key):

        self.createLabelFrame(key,self.frames['sliderFrame'],'TOP')
        
        def setValue(idx,value):
            self.dict['obj'].dict[key]['value'][idx] = int(value)

        for idx,name in enumerate(self.dict['obj'].dict[key]['nameList']):
                    self.widgets[key] = ttk.Entry(self.frames['sliderFrame'], width=300)       
                    self.widgets[key].set(self.dict['obj'].dict[key]['value'][idx])
                    self.widgets[key].pack(padx=0,pady=0)       
        #todo

    def toggleBoolean(self,key): 
            if self.dict['obj'].dict[key]['value'] == True: self.dict['obj'].dict[key]['value'] = False
            else: self.dict['obj'].dict[key]['value'] = True

    def changeValue(self,key,value):  
        self.dict['obj'].dict[key]['value'] = value

    def createButton(self,key):

        self.widgets[key] = ttk.Button(self.frames['buttonFrame'],text=key)

        if self.dict['obj'].dict[key]['command'] == 'saveobject': self.widgets[key].config(command= lambda : self.dict['obj'].dictToJson('file.json',mode='save'))
        if self.dict['obj'].dict[key]['command'] == 'toggleBoolean': self.widgets[key].config(command= lambda : self.toggleBoolean(key)) 

        self.widgets[key].pack(side=TOP,padx=10,pady=10)

    def createMultiButton(self,key):

        for idx,button in enumerate(self.dict['obj'].dict[key]['buttonsNames']):
            self.widgets[button] = ttk.Button(self.frames['buttonFrame'],text=button)
            self.widgets[button].config(command= lambda  value = self.dict['obj'].dict[key]['buttonsValues'][idx] : self.changeValue(key,value)) 
            self.widgets[button].pack(side=TOP,padx=10,pady=10)

    def createSlider(self,key):
        
        def setValue(value):
            self.dict['obj'].dict[key]['value'] = int(value)

        self.widgets[key] = Scale(self.frames['sliderFrame'],length=500,label=key,showvalue=True, orient=HORIZONTAL,
                                  from_=self.dict['obj'].dict[key]['min'],
                                  to=self.dict['obj'].dict[key]['max'],
                                  command = lambda value : setValue(value) )
        
        self.widgets[key].set(self.dict['obj'].dict[key]['value'])
        self.widgets[key].pack(padx=0,pady=0)

    def createSliderFromList(self,key):

        self.createLabelFrame(key,self.frames['sliderFrame'],'TOP')

        def setValue(idx,value):
            self.dict['obj'].dict[key]['value'][idx] = int(value)

        for idx,name in enumerate(self.dict['obj'].dict[key]['nameList']):
                    self.widgets[key] = Scale(self.frames[key],length=500,label=name,showvalue=True, orient=HORIZONTAL,
                                  from_=self.dict['obj'].dict[key]['min'][idx],
                                  to=self.dict['obj'].dict[key]['max'][idx],
                                  command = lambda value, index = idx : setValue(index,value) )
        
                    self.widgets[key].set(self.dict['obj'].dict[key]['value'][idx])
                    self.widgets[key].pack(padx=0,pady=0)

    def createLabelFrame(self,name,hostingElement,side):
        self.frames[name] = ttk.LabelFrame(hostingElement,text=name, relief='groove')
        if side=='TOP':self.frames[name].pack(padx=10,pady=10,side=TOP)
        if side=='LEFT':self.frames[name].pack(padx=10,pady=10,side=LEFT)
        if side=='RIGHT':self.frames[name].pack(padx=10,pady=10,side=RIGHT)
        if side=='BOTTOM':self.frames[name].pack(padx=10,pady=10,side=BOTTOM)
    
    def createFrame(self,name,hostingElement,side):
        self.frames[name] = ttk.LabelFrame(hostingElement)
        if side=='TOP':self.frames[name].pack(side=TOP)
        if side=='LEFT':self.frames[name].pack(side=LEFT)
        if side=='RIGHT':self.frames[name].pack(side=RIGHT)
        if side=='BOTTOM':self.frames[name].pack(side=BOTTOM)

    def createLabel(self,name,hostingElement):   
        self.labels[name] = ttk.Label(hostingElement)
        self.labels[name].pack(padx=10,pady=10)        

    def createDropdown(self,key):      
        self.widgets[key] = ttk.Combobox(self.controlFrame,width=12,values=self.dict['obj'].dict[key]['choiches']) 
        self.widgets[key].set(self.dict['obj'].dict[key]['choiches'][0])
        self.widgets[key].pack(padx=10,pady=10)

    def updateBoolTrue(self,key):
        self.readyforupdate[key] = True
        self.waitForUpdate()

    def show_frame(self):
        
        for key in self.cap:

            if self.dict['obj'].dict['speed']>1000:
                self.frame[key]=copy.copy(self.frameOriginal[key]) 
                speed = self.dict['obj'].dict['speed'] -1000
            else:    
                if self.cap[key].isOpened() :
                    _, self.frame[key] = self.cap[key].read()
                    self.frameOriginal[key] = copy.copy(self.frame[key])
                    self.readyforupdate[key] = False
                    speed = self.dict['obj'].dict['speed'] 
                else: return 

            self.process(key)
            self.labels[key].after(speed,lambda key=key:self.updateBoolTrue(key))

    def waitForUpdate(self):
        go = True
        for key in self.readyforupdate:  go = go & self.readyforupdate[key]
        if go:  self.show_frame()

    def process(self,key):

        result = pipelinesList[self.pipelines[key]].process(self.frame[key])
        self.pipelinePerformance(key)
        
        if self.blocchiUpdateBool: self.blocchiUpdate(key)
        if self.taskUpdateBool: self.taskUpdate(key)
        if self.timeUpdateBool: self.timeUpdate(key)

        img = Image.fromarray(result)
        imgtk = ImageTk.PhotoImage(image=img)
        self.labels[key].imgtk = imgtk
        self.labels[key].configure(image=imgtk)

    def pipelinePerformance(self,key):
        
        performanceList = []
        performanceSummary = ' '

        for timer in pipelinesList[self.pipelines[key]].stageTimers:
            if timer in pipelinesList[self.pipelines[key]].stageTimers.keys():
                if pipelinesList[self.pipelines[key]].dict[timer]:
                    performanceList.append( pipelinesList[self.pipelines[key]].stageTimers[timer].label + ' ' +  str(pipelinesList[self.pipelines[key]].stageTimers[timer].timer)[:6] + '  ')

        self.performance[key+'Text'].set(performanceSummary.join(performanceList))

    def blocchiUpdate(self,key):
        blocchiList = []
        blocchiSummary = ' '

        for idx,blockName in enumerate(Blocks.dict['persistentModel']):
            block = Blocks.dict['persistentModel'][blockName]
            blocco = ''
            blocco = blocco + blockName
            for item in block['ROIHistory']:
                if not(item==''):blocco = blocco + ' --> '+ item 
            blocco = blocco + '\n'
            blocchiList.append(blocco)
       
        blocchiSummary = blocchiSummary.join(blocchiList)         
        self.textUpdate('blocchi',blocchiSummary)    
    

    
    def taskUpdate(self,key):
        taskList = []
        taskSummary = ' '

        for idx,taskName in enumerate(Blocks.dict['proceduralTask']):
            task = Blocks.dict['proceduralTask'][taskName]
            string = 'Step'+str(taskName)+': '+ task['block']+'-->'+task['targetROI']
            if task['completed']: string = string + ' --> completed @ ' + task['timestamp']
            if task['error']: string = string + ' --> error'
            string = string + '\n'
            taskList.append(string)
       
        taskSummary = taskSummary.join(taskList)         
        self.textUpdate('task',taskSummary)    

    def timeUpdate(self,key):
        timenow = Blocks.getStamp()
        self.textUpdate('time',timenow)


    def textUpdate(self,name,text):
        self.widgets[name+'Text'].set(text)

    def create(self):
        self.window.mainloop()  

    def destroy(self):
        self.window.quit()  

    def manage_speed(self,newspeed):
        self.dict['obj'].dict['speed'] = int(newspeed)
    
