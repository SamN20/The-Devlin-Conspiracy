from cmu_graphics import *

app.stepsPerSecond = 120
app.rngClock = 0 
walls = Group(Rect(100, 100, 200, 2))
thingsThatStopMovement = Group(walls)
whirlpool = Group()
whirlpool.timer = 0
bgDeco = Group()

class Player(object): 
    def __init__(self, cx, cy, xpLevel, sight): 
        self.sight = Arc(cx, cy, sight*10 + 50, sight*10 + 50, -45, 90, fill = 'lightGrey', opacity = 0)
        self.drawing = Circle(cx, cy, 7, fill = 'white', border = 'black')
        self.hitbox = Rect(self.drawing.centerX, self.drawing.centerY, (self.drawing.radius*2)+2, (self.drawing.radius*2)+2, fill = 'green', opacity = 25, align="center")
        self.full = Group(self.drawing, self.sight, self.hitbox)
        self.dx = 1
        self.dy = 1
        self.level = xpLevel
        self.canDash = True 
        self.contact = False
        self.sucked = False
    def wallCollision(self): 
        if walls.hits(self.hitbox.right, self.hitbox.centerY) or self.hitbox.right > 400: # left side of wall, going right 
            self.full.centerX -= self.dx
        if walls.hits(self.hitbox.left, self.hitbox.centerY) or self.hitbox.left < 0: # right side of wall, going left
            self.full.centerX += self.dx
        if walls.hits(self.hitbox.centerX, self.hitbox.top) or self.hitbox.top < 0: # top of wall, going down
            self.full.centerY += self.dy
        if walls.hits(self.hitbox.centerX, self.hitbox.bottom) or self.hitbox.bottom > 400: # bottom of wall, going up 
            self.full.centerY -= self.dy
    def dash(self): 
        if self.level == 0 : 
            self.canDash = False
        if self.canDash == True : 
            self.canDash = False 
            dashX, dashY = getPointInDir(self.hitbox.centerX, self.hitbox.centerY, self.sight.rotateAngle, self.level*25)
            dashHitbox = Line(self.hitbox.centerX, self.hitbox.centerY, dashX, dashY, lineWidth = 12, fill = 'red')
            for obj in thingsThatStopMovement: 
                if dashHitbox.hitsShape(obj): 
                    pass #unfinished 

    def unload(self): 
        self.loaded = False
        self.drawing.centerX = 0 
        self.drawing.centrY = 0 
        self.drawing.visible = False 
    
    def contactCheck(self): 
        if self.hitbox.hits(thingsThatStopMovement): 
            self.contact = True 
        else: 
            self.contact = False
    def rechargeRateCheck(self): 
        rate = 400 - (20*self.level)
        return rate 
    def rechargeCheck(self): 
        if self.level != 0 : 
            if app.rngClock > self.rechargeRateCheck(): 
                self.canDash = True
    def whirlpoolAngle(self):         
        suckAngle = rounded(angleTo(whirlpool.centerX, whirlpool.centerY, self.hitbox.centerX, self.hitbox.centerY))
        if suckAngle >= 0 and suckAngle < 90: 
            return 'upRight'
        if suckAngle >= 90 and suckAngle < 180: 
            return 'downRight'
        if suckAngle >= 180 and suckAngle < 270: 
            return 'downLeft'
        if suckAngle >= 270 and suckAngle < 360: 
            return 'upLeft'

    def whirlpoolSuck(self): 
        if self.whirlpoolAngle() == 'upRight': 
            self.full.centerX -= self.dx/2
            self.full.centerY += self.dy/2
        elif self.whirlpoolAngle() == 'downRight': 
            self.full.centerX -= self.dx/2
            self.full.centerY -= self.dy/2
        elif self.whirlpoolAngle() == 'upLeft': 
            self.full.centerX += self.dx/2
            self.full.centerY += self.dy/2
        elif self.whirlpoolAngle() == 'downLeft': 
            self.full.centerX += self.dx/2
            self.full.centerY -= self.dy/2
        if distance(self.hitbox.centerX, self.hitbox.centerY, whirlpool.centerX, whirlpool.centerY) < 1 : 
            self.sucked = True
        else : 
            self.sucked = False 

player = Player(200, 75, 2, 2)
debugLevel = Label(player.level, 20, 20)

def spawnWhirlpool(x, y, colScheme): 
    if colScheme == 'desert' : 
        col1 = 'khaki'
        col2 = 'paleGoldenrod'
    if colScheme == 'water' : 
        col1 = 'lightBlue'
        col2 = 'powderBlue'
    
    for i in range(12): 
        layer = Circle(x, y, 100 - (8*i), fill=col1)
        if i % 2 == 1 : 
            layer.fill = col2
        whirlpool.add(layer)
def whirlpoolPhysics(): 
    for layer in whirlpool : 
        if whirlpool.timer % 2 == 1: 
            layer.radius -= .5
            if layer.radius == 1: 
                layer.toBack()
                layer.radius = 100
    # Whirlpool Animation
    if whirlpool.contains(player.hitbox.centerX, player.hitbox.centerY): 
        player.whirlpoolSuck()
        # sucks player into center of whirlpool

def orientation(x1, y1, x2, y2): 
    angle = angleTo(x1, y1, x2, y2)
    if angle % 90 == 0: 
        if angle == 0: 
            pass # unfinished 

def onKeyHold(keys): 
    if 'w' in keys: 
        player.full.centerY -= player.dy
        player.sight.rotateAngle = 0
    if 's' in keys: 
        player.full.centerY += player.dy
        player.sight.rotateAngle = 180
    if 'a' in keys: 
        player.full.centerX -= player.dx
        player.sight.rotateAngle = 270
    if 'd' in keys: 
        player.full.centerX += player.dx
        player.sight.rotateAngle = 90
    if 'w' in keys and 'd' in keys: 
        player.sight.rotateAngle = 45
    if 's' in keys and 'd' in keys: 
        player.sight.rotateAngle = 135
    if 'w' in keys and 'a' in keys: 
        player.sight.rotateAngle = 315
    if 's' in keys and 'a' in keys: 
        player.sight.rotateAngle = 225
        
def onKeyPress(key): 
    if key == 'k': 
        player.dash()
    if key == 'l' : 
        player.level += 1
        debugLevel.value += 1 
    if key == 'p' : 
        print(player.sight.rotateAngle)
        
def onStep(): 
    app.rngClock += 1 
    if app.rngClock > 1000 : 
        app.rngClock = 0
    
    player.rechargeCheck()
    player.wallCollision()

    whirlpool.timer += 1 
    if whirlpool.timer > 30 : 
        whirlpool.timer = 1 
    whirlpoolPhysics()

spawnWhirlpool(200, 250, 'water')

cmu_graphics.run()