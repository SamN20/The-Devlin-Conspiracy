from cmu_graphics import * 
import Keybinds

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
    def __init__(self, cx, cy, level): 
        self.draw(cx, cy, level)
        self.dx = 0.5
        self.dy = 0.5
        self.actions = ['dash', 'swing', 'shoot']
        self.currentActionIndex = 0
        self.currentAction = self.actions[self.currentActionIndex]
        self.attacking = False
        self.canShoot = True
        self.projectiles = [ ]
    
    def draw(self, cx, cy, level): 
        self.sight = Arc(cx, cy, level*15 + 50, level*15 + 50, -45, 90, fill = 'gainsboro', opacity = 75)
        self.body = Circle(cx, cy, 7, fill = 'white', border = 'black')
        self.hitbox = Rect(cx, cy, 15, 15, fill = 'green', opacity = 25, align = 'center')
        self.swing = Arc(cx, cy, 30*level, 30*level, -55, 10, fill = 'red')
        self.drawing = Group(self.body, self.sight, self.swing, self.hitbox)
    
    def movement(self, key): 
        controls = {
            Keybinds.up : [0, -self.dy], 
            Keybinds.down : [0, self.dy], 
            Keybinds.left : [-self.dx, 0], 
            Keybinds.right : [self.dx, 0], 
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
        if game.room.walls.hits(self.hitbox.right, self.hitbox.centerY) or self.hitbox.right > 400:      
            self.drawing.centerX -= self.dx
        if game.room.walls.hits(self.hitbox.left, self.hitbox.centerY) or self.hitbox.left < 0:         
            self.drawing.centerX += self.dx
        if game.room.walls.hits(self.hitbox.centerX, self.hitbox.top) or self.hitbox.top < 0:           
            self.drawing.centerY += self.dy
        if game.room.walls.hits(self.hitbox.centerX, self.hitbox.bottom) or self.hitbox.bottom > 400:   
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
    def shoot(self): 
        if self.canShoot == True: 
            bullet = Projectile(self.hitbox.centerX, self.hitbox.centerY, self.sight.rotateAngle-45, 'red', 'basic')
            self.projectiles.append(bullet)
            print(bullet.hDis, bullet.vDis, bullet.hDir, bullet.vDir)
    def bulletPhysics(self): 
        for bullet in self.projectiles : 
            if bullet.drawing.centerX > 410 or bullet.drawing.centerX < -10 : 
                self.projectiles.remove(bullet)
            if bullet.drawing.centerY > 410 or bullet.drawing.centerY < -10 : 
                self.projectiles.remove(bullet)
            bullet.move()

    def handleActionIndex(self, key): 
        if key == Keybinds.actionIndexDown : 
            self.currentActionIndex -= 1
        if key == Keybinds.actionIndexUp : 
            self.currentActionIndex += 1
        if self.currentActionIndex > len(self.actions) - 1 : 
            self.currentActionIndex = 0
        if self.currentActionIndex < 0 : 
            self.currentActionIndex = len(self.actions) - 1

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
        self.bulletPhysics()
        self.currentAction = self.actions[self.currentActionIndex]
    def handleMousePress(self, x, y): 
        if game.room.roomID != 0 : 
            if self.currentAction == 'swing' : 
                self.attacking = True 
            if self.currentAction == 'shoot' : 
                self.shoot()

class Projectile(object): # making Projectiles a Class so the player can shoot multiple bullets and make enemies that shoot
    def __init__(self, cx, cy, angle, colour, type):
        self.drawing = Circle(cx, cy, 3, fill = colour)
        self.moveX, self.moveY = getPointInDir(cx, cy, angle, 400)
        self.debug = Circle(self.moveX/2, self.moveY/2, 3, fill = 'blue')
        self.hDis = rounded(distance(cx, cy, self.moveX, cy))
        self.vDis = rounded(distance(cx, cy, cx, self.moveY))
        self.hDir = orientation(cx, cy, self.moveX, cy, 'horizontal')
        self.vDir = orientation(cx, cy, cx, self.moveY, 'vertical')

    def move(self): 
        pass

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
    player.handleMousePress(x, y)

def onStep(): 
    player.handleOnStep() 
    game.room.handleOnStep() 

def mapValue(value, valueMin, valueMax, targetMin, targetMax):
    ratio = (value-valueMin) / (valueMax-valueMin)
    result = ratio * (targetMax-targetMin) + targetMin
    return result

def orientation(x1, y1, x2, y2, type): # I know this function made weirdly Sam, it's fine
    angle = rounded(angleTo(x1, y1, x2, y2))
    if type == 'diagonal' : 
        if angle >= 0 and angle < 90: 
            return 'topRight'
        if angle >= 90 and angle < 180: 
            return 'bottomRight'
        if angle >= 180 and angle < 270: 
            return 'bottomLeft'
        if angle >= 270 and angle < 360: 
            return 'topLeft'
    if type == 'vertical' : 
        if (angle >= 0 and angle < 180): 
            return 'right'
        if (angle >= 180 and angle < 360): 
            return 'left'
    if type == 'horizontal' : 
        if (angle >= 270 and angle < 360) or (angle >= 0 and angle < 90): 
            return 'above'
        if (angle >= 90 and angle < 270): 
            return 'below'

game = GameState()
player = Player(200, 200, 5)

cmu_graphics.run()