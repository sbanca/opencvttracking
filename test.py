import cvWrapper as cvW
import interfaceWrapper as intWr
import cv2
from pipeline import Masks,Trims,bckSub,Thresh,Bins,wAreas,Blocks


def test5():

    cap0 = cv2.VideoCapture('videos/camera2.2.avi')

    Main = cvW.base('Main')
    Main.config(name='Main', saveButton = {'interface':True,'widget':'button','command':'saveobject'})

    newWindow = intWr.interface()

    newWindow.config(obj=Blocks,pipelines=['Trim'],media=[cap0])

    newWindow.initialise()

    newWindow.create()

#test5()



def test4():

    cap = cv2.VideoCapture('videos/camera2.2.avi')

    Main = cvW.base('Main')

    Main.config(name='Main', saveButton = {'interface':True,'widget':'button','command':'saveobject'})

    newWindow = intWr.interface()

    newWindow.config(obj=Main,pipelines=['Trim'],media=[cap])

    newWindow.initialise()

    newWindow.create()

#test4()

def test3():

    cap = cv2.VideoCapture('videos/camera2.2.avi')


    newWindow = intWr.interface()

    # newWindow.config(obj=Masks['Blue Mask'],pipelines=['pipelineBlue'],media=[cap])
    # newWindow.config(obj=Masks['Yellow Mask'],pipelines=['pipelineYellow'],media=[cap])
    # newWindow.config(obj=Masks['Red Mask'],pipelines=['pipelineRed'],media=[cap])
    # newWindow.config(obj=Masks['Green Mask'],pipelines=['pipelineGreen'],media=[cap])
    # newWindow.config(obj=Masks['Hand'],pipelines=['pipelineHand'],media=[cap])
    newWindow.config(obj=Trims['Trim'],pipelines=['TrimWarp'],media=[cap])
    # newWindow.config(obj=Trims['Trim2'],pipelines=['TrimWorkArea'],media=[cap])
    # newWindow.config(obj=bckSub['bckSub'],pipelines=['bckSub','BGR2RGB'],media=[cap,cap])
    # newWindow.config(obj=Thresh['one'],pipelines=['thresh'],media=[cap])
    # newWindow.config(obj=Bins['twelveth'],pipelines=['Bins'],media=[cap])

    newWindow.initialise()
    newWindow.create()

    #windows={}

    # for maskKey in Masks:
    #     windows[maskKey] = intWr.interface()
    #     windows[maskKey].config(obj=Masks[maskKey],pipelines=['Trim'],media=[cap])
    #     windows[maskKey].initialise()
    #     windows[maskKey].create()

    # for binname in Bins:
    #     windows[binname] = intWr.interface()
    #     windows[binname].config(obj=Bins[binname],pipelines=['Bins'],media=[cap])
    #     windows[binname].initialise()
    #     windows[binname].create()

    # for wArea in wAreas:
    #     windows[wArea] = intWr.interface()
    #     windows[wArea].config(obj=wAreas[wArea],pipelines=['wAreas'],media=[cap])
    #     windows[wArea].initialise()
    #     windows[wArea].create()


test3()

def test2():

    cap = cv2.VideoCapture('videos/video4.avi')
    #cap = cv2.imread('frame1.jpg')

    obj1 = cvW.OtherClass('obj1')

    obj1.config(name='obj3',
                par1={'value':[0,0,0],'interface':True,'widget':'sliderList','max':[179,255,255],'min':[0,0,0],'nameList':['H','S','V']},
                par2={'value':10,'interface':True,'widget':'slider','max':100,'min':10},
                par3={'value':'choiche1','interface':False,'widget':'dropdown','choiches':['choiche1','choice2','choihce3']},
                par4={'value':9999,'interface':True,'widget':'slider','max':150,'min':0},
                par5={'value':999999,'interface':True,'widget':'slider','max':200,'min':100})

    newWindow = intWr.interface('Interface Name', obj1.dict,'video','pipelineTest',cap)
    newWindow.initialise()
    #newWindow = intWr.interface('Interface Name', obj1.dict,'image',cap)
    newWindow.create()



def test1():
    obj1 = cvW.ContoursFD('obj1')

    obj1.config(par1=[(2,2),(5,5)],par2=1,par3='gaglioffo',par4=100,par5=1000)

    obj1.printAttributes()

    #create new class inheriting previous object
    obj2 = cvW.HSVMask('obj1', obj1)

    obj2.config(par1=(0,0,0),par2='corallo',par3=100,par4=1000,par5=10000)

    obj2.printAttributes()

    obj2.printInheritedAttributes()

    # #check if the contours changed in object var1 sticks to the referenced var
    obj1.config(par1=((1,2),(3,4)))

    obj2.printInheritedAttributes()

    # #save.json
    obj1.dictToJson('test.json',mode='save')
    obj2.dictToJson('test.json',mode='save')

    #change configuration
    obj1.config(name='obj3',
                par1={'value':[(9,9),(9,9)],'interface':True},
                par2={'value':10,'interface':True},
                par3={'value':'ciao','interface':False},
                par4={'value':9999,'interface':True},
                par5={'value':999999,'interface':True})
    obj1.dictToJson('test.json',mode='save')
    obj2.config(name='obj4',par1=(0,0,0),par2='corallo',par3=100,par4=1000,par5=10000)
    obj2.dictToJson('test.json',mode='save')
    obj1.config(name='obj1')
    obj2.config(name='obj2')

    # #reload from json
    obj1.dictToJson('test.json',mode='load')
    obj2.dictToJson('test.json',mode='load')

    obj1.printAttributes()
    obj2.printAttributes()