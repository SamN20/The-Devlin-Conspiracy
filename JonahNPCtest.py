from cmu_graphics import * 

app.stepsPerSecond = 120

class NPC(object): 
    def __init__(self, cx, cy, sightSize): 
        self.sight = Arc(cx, cy, sightSize*10 + 50, sightSize*10 + 50, -45, 90, fill = 'lightGrey', opacity = 50)
        self.drawing = Circle(cx, cy, 7, fill = 'white', border = 'black')
        self.hitbox = Rect(cx, cy, 15, 15, fill = 'green', opacity = 25, align = 'center')
        self.full = Group(self.hitbox, self.sight, self.drawing)
        self.steps = 0
        self.speed = 1

    def direction(self): 
        if self.sight.rotateAngle == 0: 
            return 'up'
        if self.sight.rotateAngle == 180: 
            return 'down'
        if self.sight.rotateAngle == 270: 
            return 'left'
        if self.sight.rotateAngle == 90: 
            return 'right'
    
    def move(self): 
        self.moveSteps = 0
        dir = self.direction()
        if dir == 'up': 
            self.full.centerY -= 1
        if dir == 'down': 
            self.full.centerY += 1
        if dir == 'left': 
            self.full.centerX -= 1
        if dir == 'right': 
            self.full.centerX += 1
        self.moveSteps += 1

    def behaviour(self): 
        if self.hitbox.centerY < 100: 
            self.sight.rotateAngle = 180
        if self.hitbox.centerY > 300: 
            self.sight.rotateAngle = 0

    def handleOnStep(self): 
        self.steps += 1
        if self.steps % 3 == 0 : 
            self.move()
        self.behaviour()

test = NPC(200, 200, 7)

def onStep(): 
    test.handleOnStep()

def onKeyPress(key): 
    if key == 'space': 
        print(test.sight.rotateAngle)
    if key == 'up': 
        test.sight.rotateAngle = 0
    if key == 'down': 
        test.sight.rotateAngle = 180
    if key == 'left': 
        test.sight.rotateAngle = 270
    if key == 'right': 
        test.sight.rotateAngle = 90
        
cmu_graphics.run()