from cmu_graphics import * 

test = Sound("Sound_files\TestSounds\CantinaBand3.wav")

maxHealth = 100
app.health = 100

def mapValue(value, valueMin, valueMax, targetMin, targetMax):
    ratio = (value-valueMin) / (valueMax-valueMin)
    result = ratio * (targetMax-targetMin) + targetMin
    return result

def drawHealthBar(x,y):
    width=mapValue(app.health, 0, maxHealth, 0, 100)
    bar = Group(Rect(x, y-1, width, 10,  fill="green", align='bottom'), Rect(x, y, maxHealth+2, 12,  fill=None, border="black", borderWidth=1, align='bottom'))
    return bar

app.bar = drawHealthBar(200,200)

def updateHealthBar():
    app.bar.clear()
    app.bar = drawHealthBar(0,0)

def onMousePress(x,y):
    test.play(loop=True)
    app._app._width = 400
    app._app._height = 400
    app._app.updateScreen(True)

def onMouseDrag(x,y):
    test.pause()

# def onMouseMove(x,y):
#     bar.centerX = x
#     bar.centerY = y-10

Circle(200, 200, 1)

Circle(790, 790, 5)

# Image("Images/testimage.png", 0, 0, height=70, width=70)


# Line 540 is where you can change the w and h in the CMU file

cmu_graphics.run()


# class GUIManager (object):
#     def __init__(self):
#         pass

#     def updateHealthBar(self, health, maxHealth, character):
#         # character.healthBar.width = mapValue(health, 0, maxHealth, 0, 50)
#         character.healthBar.visible = character.drawing.visible


#         # character.healthBar.clear()
#         # bar = self.drawHealthBar(health, maxHealth, character)
#         # return bar

#     def drawHealthBar(self, health, maxHealth, character):
#         cx = character.hitbox.centerX
#         cy = character.hitbox.top
#         width=mapValue(health, 0, maxHealth, 0, 50) # 50 is the max width of the health bar
#         outline = Rect(cx, cy, width+2, 5,  fill=None, border="black", borderWidth=1, align='bottom')
#         middle = Rect(outline.left+1, cy, width, 3,  fill="green", align='left')
#         bar = Group(outline, middle)
#         # bar = Group(Rect(cx, cy-1, width, 3,  fill="green", align='bottom'), Rect(cx, cy, width+2, 5,  fill=None, border="black", borderWidth=1, align='bottom'))
#         # bar = Group(Rect(cx, cy-1, width, 4,  fill="green", align='bottom'))
#         bar.opacity = 50
#         bar.visible = character.drawing.visible
#         return bar