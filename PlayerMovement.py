from cmu_graphics import * 
import Keybinds

app.stepsPerSecond = 120

class Player(object): 
    def __init__(self, cx, cy, xpLevel, sight): 
        self.sight = Arc(cx, cy, sight*10 + 50, sight*10 + 50, -45, 90, fill = 'lightGrey', opacity = 50)
        self.drawing = Circle(cx, cy, 7, fill = 'white', border = 'black')
        self.hitbox = Rect(cx, cy, 15, 15, fill = 'green', opacity = 25, align = 'center')
        self.full = Group(self.drawing, self.sight, self.hitbox)
        self.dx = 0.75
        self.dy = 0.75
    
    def handleOnKeys(self, keys): 
        for key in keys: 
            self.movement(key)

    def movement(self, key): 
        controls = {
            Keybinds.movement['up'] : [0, -self.dy], 
            's' : [0, self.dy], 
            'a' : [-self.dx, 0], 
            'd' : [self.dx, 0], 
            }
        
        if key in controls : 
            self.full.centerX += controls[key][0]
            self.full.centerY += controls[key][1]

    def lookRotation(self, x, y): 
        angle = angleTo(self.hitbox.centerX, self.hitbox.centerY, x, y)
        self.sight.rotateAngle = angle
    
    def handleMouseMovement(self, x, y): 
        self.lookRotation(x, y)
            
player = Player(200, 200, 5, 5)

def onKeyHold(keys):     
    player.handleOnKeys(keys)

def onMouseMove(x, y): 
    player.handleMouseMovement(x, y)

cmu_graphics.run()