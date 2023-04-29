from cmu_graphics import * 

test = Sound("CantinaBand3.wav")

def onMousePress(x,y):
    test.play(loop=True)

def onMouseDrag(x,y):
    test.pause()

cmu_graphics.run()