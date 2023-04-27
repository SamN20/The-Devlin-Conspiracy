from cmu_graphics import * 

app.stepsPerSecond = 120

class GameState(object): 
    def __init__(self):
        self.mode = 'TITLE SCREEN'
        self.room = RoomState()

        self.roomList = { }
        self.soundtrack = { }
        self.soundEffects = { }

class RoomState(object): 
    def __init__(self): 
        self.attributes = { 
            'difficulty' : 0, 
            'lightLevel' : 0,
            'slippery' : False, 
            'hasBoss' : False, 
            'hasEnemies' : False, 
            'hasCollectibles' : False, 
            'checkpoint' : False, 
            'savepoint' : False, 
        } 
        self.walls = Group()
        
        self.cursorX = 0
        self.cursorY = 0
        self.roomID = 1 # roomID of 0 is for menus, 1 for test map

        self.cursor = Circle(0, 0, 10, border = 'red', fill = None) 
    def handleOnStep(self): 
        self.cursor.centerX = self.cursorX
        self.cursor.centerY = self.cursorY

class Player(object): 
    def __init__(self, cx, cy, xpLevel, sight): 
        self.draw(cx, cy, xpLevel, sight)
        self.dx = 0.5
        self.dy = 0.5
        self.actions = ['dash', 'swing', 'shoot']
        self.currentActionIndex = 0
        self.currentAction = self.actions[self.currentActionIndex]
        self.attacking = False
    
    def draw(self, cx, cy, xpLevel, sight): 
        self.sight = Arc(cx, cy, sight*15 + 50, sight*15 + 50, -45, 90, fill = 'gainsboro', opacity = 75)
        self.model = Circle(cx, cy, 7, fill = 'white', border = 'black')
        self.hitbox = Rect(cx, cy, 15, 15, fill = 'green', opacity = 25, align = 'center')
        self.swing = Arc(cx, cy, 30*xpLevel, 30*xpLevel, -55, 10, fill = 'red')
        self.drawing = Group(self.model, self.sight, self.swing, self.hitbox)
    
    def movement(self, key): 
        controls = {
            'w' : [0, -self.dy], 
            's' : [0, self.dy], 
            'a' : [-self.dx, 0], 
            'd' : [self.dx, 0], 
            }
        if key in controls : 
            self.drawing.centerX += controls[key][0]
            self.drawing.centerY += controls[key][1]
    def lookRotation(self, x, y): 
        angle = angleTo(self.hitbox.centerX, self.hitbox.centerY, x, y)
        if self.attacking == False : 
            self.sight.rotateAngle = angle
            self.swing.rotateAngle = angle
    def collision(self): 
        if game.room.walls.hits(self.hitbox.right, self.hitbox.centerY) or self.hitbox.right > 400:     # left side of wall, going right 
            self.drawing.centerX -= self.dx
        if game.room.walls.hits(self.hitbox.left, self.hitbox.centerY) or self.hitbox.left < 0:         # right side of wall, going left
            self.drawing.centerX += self.dx
        if game.room.walls.hits(self.hitbox.centerX, self.hitbox.top) or self.hitbox.top < 0:           # top of wall, going down
            self.drawing.centerY += self.dy
        if game.room.walls.hits(self.hitbox.centerX, self.hitbox.bottom) or self.hitbox.bottom > 400:   # bottom of wall, going up 
            self.drawing.centerY -= self.dy
    def attackSwing(self): 
        if self.attacking == True: 
            self.swing.opacity = 100
            finishAngle = self.sight.rotateAngle + 95
            self.swing.rotateAngle += 1.5
            if self.swing.rotateAngle >= finishAngle: 
                self.attacking = False
                self.swing.opacity = 0
                self.swing.rotateAngle = self.sight.rotateAngle
        else: 
            self.swing.opacity = 0
    def handleActionIndex(self, key): 
        if key == 'q': 
            self.currentActionIndex -= 1
        if key == 'e': 
            self.currentActionIndex += 1
        if self.currentActionIndex > 2 : 
            self.currentActionIndex = 0
        if self.currentActionIndex < 0 : 
            self.currentActionIndex = 2

    def handleOnKeys(self, keys): 
        for key in keys: 
            self.movement(key)
    def handleKeyPress(self, key): 
        self.handleActionIndex(key)
        print(self.currentActionIndex, self.currentAction)
    def handleOnStep(self): 
        self.lookRotation(game.room.cursorX, game.room.cursorY)
        self.collision()
        self.attackSwing()

        self.currentAction = self.actions[self.currentActionIndex]

    def handleMousePress(self): 
        if game.room.roomID != 0 : 
            if self.currentAction == 'swing' : 
                self.attacking = True 

def onKeyHold(keys):     
    player.handleOnKeys(keys)
def onKeyPress(key): 
    player.handleKeyPress(key)
def onMouseMove(x, y): 
    game.room.cursorX = x
    game.room.cursorY = y
def onMouseDrag(x, y): 
    game.room.cursorX = x
    game.room.cursorY = y
def onMousePress(x, y): 
    player.handleMousePress()

def onStep(): 
    player.handleOnStep()
    game.room.handleOnStep()

game = GameState()
player = Player(200, 200, 5, 5)

cmu_graphics.run()