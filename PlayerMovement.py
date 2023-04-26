from cmu_graphics import * 
import Keybinds
import NPCMovement

app.stepsPerSecond = 120

class Player(object): 
    def __init__(self, cx, cy, xpLevel, sight): 
        self.sight = Arc(cx, cy, sight*10 + 50, sight*10 + 50, -45, 90, fill = 'lightGrey', opacity = 50)
        self.body = Circle(cx, cy, 7, fill = 'white', border = 'black')
        self.hitbox = Rect(cx, cy, 15, 15, fill = 'green', opacity = 25, align = 'center')
        self.drawing = Group(self.body, self.sight, self.hitbox)
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
            self.drawing.centerX += controls[key][0]
            self.drawing.centerY += controls[key][1]

    def lookRotation(self, x, y): 
        angle = angleTo(self.hitbox.centerX, self.hitbox.centerY, x, y)
        self.sight.rotateAngle = angle
    
    def handleMouseMovement(self, x, y): 
        self.lookRotation(x, y)
            
player = Player(200, 200, 5, 5)
enemy = NPCMovement.NPC(200, 200, 0, 5, 5, 'red')
enemy1 = NPCMovement.NPC(100, 100, 0, 5, 5, 'red')
enemy2 = NPCMovement.NPC(300, 300, 0, 5, 5, 'red')

allNPCs = [enemy, enemy1, enemy2]

def onKeyHold(keys):     
    player.handleOnKeys(keys)

def onMouseMove(x, y): 
    player.handleMouseMovement(x, y)

def onStep():
    for enemy in allNPCs:
        enemy.handleOnStep(player, allNPCs)


cmu_graphics.run()