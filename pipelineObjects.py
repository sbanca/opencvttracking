from pipeline import pipeline

# Initialise pipeline object
######################

pipelinesList = {}


## Main pipelines

pipelinesList['eyetrack'] = pipeline()
pipelinesList['eyetrack'].config(prepearEyeGaze=True,undistortCamera=True,Trim2=True,perspective=True,perspeRender=True,drawEyeGaze=True,BGR2RGB=True,)

pipelinesList['TopCamera'] = pipeline()
pipelinesList['TopCamera'].config(flip=True,Trim=True,blur=True,hsv=True,bckSub=False,hand=True,blueMask=True,redMask=True,greenMask=True,yellowMask=True,blocksRepres=True,renderROIs=True,renderTrsfGaze=True,BGR2RGB=True)


## Masks configuration pipelines

pipelinesList['pipelineYellow'] = pipeline()
pipelinesList['pipelineYellow'].config(flip=True,Trim=True,blur=True,hsv=True,yellowMask=True,BGR2RGB=True)

pipelinesList['pipelineBlue'] = pipeline()
pipelinesList['pipelineBlue'].config(flip=True,Trim=True,blur=True,hsv=True,blueMask=True,BGR2RGB=True,gray=True,thresh=True)

pipelinesList['pipelineRed'] = pipeline()
pipelinesList['pipelineRed'].config(flip=True,Trim=True,blur=True,hsv=True,redMask=True,BGR2RGB=True)

pipelinesList['pipelineGreen'] = pipeline()
pipelinesList['pipelineGreen'].config(flip=True,Trim=True,blur=True,hsv=True,greenMask=True,BGR2RGB=True)

pipelinesList['pipelineHand'] = pipeline()
pipelinesList['pipelineHand'].config(flip=True,Trim=True,blur=True,gray=True,hsv=True,hand=True,BGR2RGB=True)


## Areas configuration pipelines

pipelinesList['Bins'] = pipeline()
pipelinesList['Bins'].config(flip=True,Trim=True,renderBins=True,BGR2RGB=True)

pipelinesList['OrgRect'] = pipeline()
pipelinesList['OrgRect'].config(flip=True,Trim=True,renderOrgRect=True,BGR2RGB=True)

pipelinesList['wAreas'] = pipeline()
pipelinesList['wAreas'].config(flip=True,Trim=True,renderWAreas=True,BGR2RGB=True)


## Misc configuration pipelines

pipelinesList['TrimWarp'] = pipeline()
pipelinesList['TrimWarp'].config(flip=True,Trim=True,BGR2RGB=True)

pipelinesList['BGR2RGB'] = pipeline()
pipelinesList['BGR2RGB'].config(Trim=True,BGR2RGB=True)

pipelinesList['pipelineTest'] = pipeline()
pipelinesList['pipelineTest'].config(BGR2RGB=True)

pipelinesList['pipelineTestFlip'] = pipeline()
pipelinesList['pipelineTestFlip'].config(BGR2RGB=True,flip=True)

pipelinesList['thresh'] = pipeline()
pipelinesList['thresh'].config(Trim2=True,gray=True,thresh=True)

pipelinesList['bckSub'] = pipeline()
pipelinesList['bckSub'].config(Trim=True,bckSub=True)

pipelinesList['syncEyetrack'] = pipeline()
pipelinesList['syncEyetrack'].config(prepearEyeGaze=True,undistortCamera=True,Trim2=True,drawEyeGaze=True,BGR2RGB=True,)

pipelinesList['syncTopCamera'] = pipeline()
pipelinesList['syncTopCamera'].config(flip=True,BGR2RGB=True)

pipelinesList['eyetrackConfig'] = pipeline()
pipelinesList['eyetrackConfig'].config(prepearEyeGaze=True,undistortCamera=True,Trim2=True,perspective=True,perspeRender=False,drawEyeGaze=True,BGR2RGB=True,)

pipelinesList['Eyetrack2'] = pipeline()
pipelinesList['Eyetrack2'].config(prepearEyeGaze=True,drawEyeGaze=True,BGR2RGB=True,)