from cmu_graphics import * 

test = Sound("Sound_files\TestSounds\CantinaBand3.wav")

def onMousePress(x,y):
    test.play(loop=True)

def onMouseDrag(x,y):
    test.pause()

Image("Images/testimage.png", 0, 0, height=70, width=70)

cmu_graphics.run()