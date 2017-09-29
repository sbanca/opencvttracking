import cvWrapper as cvW
import interfaceWrapper as intWr
import cv2
from pipeline import Masks,Trims,bckSub,Thresh,Bins,wAreas,Blocks

path = 'videos/2017_09_28/001/'
namevideo0 = 'top'
namevideo1 = 'world'
formatvideo0 = '.avi'
formatvideo1 = '.mp4'
video0 = path + namevideo0 + formatvideo0
video1 = path + namevideo1 + formatvideo1
timestamps0 = path + namevideo0 + '_timestamps.npy'
timestamps1 = path + namevideo1 + '_timestamps.npy'
startStamp0 = 101
startStamp1 = 420

def main():
    
    cap0 = cv2.VideoCapture(video0)
    cap1 = cv2.VideoCapture(video1)
    

    Main = cvW.base('Main')
    Main.config(name='Main', saveButton = {'interface':True,'widget':'button','command':'saveobject'})

    newWindow = intWr.interface()

    newWindow.config(obj=Blocks,
                     pipelines=['TopCamera','eyetrack'],
                     media=[cap0,cap1],
                     timestamps=[timestamps0,timestamps1],
                     startStamps=[startStamp0,startStamp1])

    newWindow.initialise()

    newWindow.create()

main()

def configurationeyetracker():

    cap = cv2.VideoCapture(video1)


    newWindow = intWr.interface()

    newWindow.config(obj=Trims['Trim2'],pipelines=['eyetrack'],media=[cap])

    newWindow.initialise()
    newWindow.create()

#configurationeyetracker()

def configurationTopCamera():

    cap = cv2.VideoCapture(video0)


    # newWindow = intWr.interface()

    # newWindow.config(obj=Masks['Blue Mask'],pipelines=['pipelineBlue'],media=[cap])
    # newWindow.config(obj=Masks['Yellow Mask'],pipelines=['pipelineYellow'],media=[cap])
    # newWindow.config(obj=Masks['Red Mask'],pipelines=['pipelineRed'],media=[cap])
    # newWindow.config(obj=Masks['Green Mask'],pipelines=['pipelineGreen'],media=[cap])
    # newWindow.config(obj=Masks['Hand'],pipelines=['pipelineHand'],media=[cap])
    # newWindow.config(obj=Trims['Trim'],pipelines=['TrimWarp'],media=[cap])
    # newWindow.config(obj=bckSub['bckSub'],pipelines=['bckSub','BGR2RGB'],media=[cap,cap])
    # newWindow.config(obj=Thresh['one'],pipelines=['thresh'],media=[cap])
    # newWindow.config(obj=Bins['twelveth'],pipelines=['Bins'],media=[cap])

    # newWindow.initialise()
    # newWindow.create()

    windows={}

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

    for wArea in wAreas:
        windows[wArea] = intWr.interface()
        windows[wArea].config(obj=wAreas[wArea],pipelines=['wAreas'],media=[cap])
        windows[wArea].initialise()
        windows[wArea].create()


#configurationTopCamera()
