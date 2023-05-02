from cmu_graphics import * 

test = Sound("Sound_files\TestSounds\CantinaBand3.wav")

def onMousePress(x,y):
    test.play(loop=True)
    app._app._width = 1536
    app._app._height = 864
    app._app.updateScreen(True)

def onMouseDrag(x,y):
    test.pause()

Circle(400, 400, 5)

Circle(790, 790, 5)

Image("Images/testimage.png", 0, 0, height=70, width=70)


# Line 540 is where you can change the w and h in the CMU file

cmu_graphics.run()