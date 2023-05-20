from cmu_graphics import *

app.stepsPerSecond = 120
app.rngClock = 0 
walls = Group(Rect(50, 200, 300, 10))
thingsThatStopMovement = Group(walls)
whirlpool = Group()
whirlpool.timer = 0
slippery = False
bgDeco = Group()

class Player(object): 
    def __init__(self, cx, cy, xpLevel, sight): 
        self.sight = Arc(cx, cy, sight*10 + 50, sight*10 + 50, -45, 90, fill = 'lightGrey', opacity = 50)
        self.drawing = Circle(cx, cy, 7, fill = 'white', border = 'black')
        self.hitbox = Rect(cx, cy, 15, 15, fill = 'green', opacity = 25, align = 'center')
        self.swing = Arc(cx, cy, 100, 100, -55, 10, fill = 'red')
        self.full = Group(self.swing, self.drawing, self.sight, self.hitbox)
        self.dx = 0.75
        self.dy = 0.75
        self.level = xpLevel
        self.canDash = True 
        self.contact = False
        self.sucked = False
        self.attacking = False
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
            app.rngClock = 0
            dashX, dashY = getPointInDir(self.hitbox.centerX, self.hitbox.centerY, self.sight.rotateAngle, self.level*25)
            dashHitbox = Line(self.hitbox.centerX, self.hitbox.centerY, dashX, dashY, lineWidth = 12, fill = 'red', opacity = 10)
            for obj in thingsThatStopMovement: 
                if dashHitbox.hitsShape(obj): 
                    position1 = orientation(obj.centerX, obj.centerY, self.hitbox.centerX, self.hitbox.centerY, 'vertical')
                    if position1 == 'below': 
                        # dashing from below
                        if self.sight.rotateAngle == 45 or self.sight.rotateAngle == 315 : 
                            dashDistanceB = distance(self.hitbox.centerX, self.hitbox.centerY, self.hitbox.centerX, obj.bottom)
                            position2B = orientation(obj.centerX, obj.centerY, self.hitbox.centerX, self.hitbox.centerY, 'diagonal')
                            self.full.centerY -= dashDistanceB
                            if position2B == 'bottomRight': 
                                self.full.centerX -= dashDistanceB
                            if position2B == 'bottomLeft': 
                                self.full.centerX += dashDistanceB
                        else: 
                            pass
                        player.full.centerY = obj.bottom
                    # dashing from above
                    if position1 == 'above': 
                        if self.sight.rotateAngle == 135 or self.sight.rotateAngle == 225 : 
                            dashDistanceA = distance(self.hitbox.centerX, self.hitbox.centerY, self.hitbox.centerX, obj.top)
                            position2A = orientation(obj.centerX, obj.centerY, self.hitbox.centerX, self.hitbox.centerY, 'diagonal')
                            self.full.centerY += dashDistanceA
                            if position2A == 'bottomRight': 
                                self.full.centerX -= dashDistanceA
                            if position2A == 'bottomLeft': 
                                self.full.centerX += dashDistanceA
                        else: 
                            pass
                        player.full.centerY = obj.top
                else : 
                    self.full.centerX = dashX
                    self.full.centerY = dashY
                    self.canDash = False 
    def attack(self): 
        self.attacking = True
        
        
    
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
        if self.level != 0 and self.canDash == False: 
            if app.rngClock > self.rechargeRateCheck(): 
                self.canDash = True

    def whirlpoolSuck(self): 
        suckAngle = orientation(whirlpool.centerX, whirlpool.centerY, self.hitbox.centerX, self.hitbox.centerY, 'diagonal') 
        if suckAngle == 'topRight': 
            self.full.centerX -= self.dx/2
            self.full.centerY += self.dy/2
        elif suckAngle == 'bottomRight': 
            self.full.centerX -= self.dx/2
            self.full.centerY -= self.dy/2
        elif suckAngle == 'topLeft': 
            self.full.centerX += self.dx/2
            self.full.centerY += self.dy/2
        elif suckAngle == 'bottomLeft': 
            self.full.centerX += self.dx/2
            self.full.centerY -= self.dy/2
        if distance(self.hitbox.centerX, self.hitbox.centerY, whirlpool.centerX, whirlpool.centerY) < 1 : 
            self.sucked = True
        else : 
            self.sucked = False 
    def icePhysics(self): 
        if slippery == True: 
            pass

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
        if (angle >= 315 and angle < 45): 
            return 'above'
        if (angle >= 135 and angle < 225): 
            return 'below'
        if (angle >= 45 and angle < 135): 
            return 'right'
        if (angle >= 225 and angle < 315): 
            return 'left'

def onKeyHold(keys): 
    
    if 'w' in keys: 
        player.full.centerY -= player.dy
        player.sight.rotateAngle = 0
        player.swing.rotateAngle = 0
        player.attacking = False
    if 's' in keys: 
        player.full.centerY += player.dy
        player.sight.rotateAngle = 180
        player.swing.rotateAngle = 180
        player.attacking = False
    if 'a' in keys: 
        player.full.centerX -= player.dx
        player.sight.rotateAngle = 270
        player.swing.rotateAngle = 270
        player.attacking = False
    if 'd' in keys: 
        player.full.centerX += player.dx
        player.sight.rotateAngle = 90
        player.swing.rotateAngle = 90
        player.attacking = False
    if 'w' in keys and 'd' in keys: 
        player.sight.rotateAngle = 45
        player.swing.rotateAngle = 45
    if 's' in keys and 'd' in keys: 
        player.sight.rotateAngle = 135
        player.swing.rotateAngle = 135
    if 'w' in keys and 'a' in keys: 
        player.sight.rotateAngle = 315
        player.swing.rotateAngle = 315
    if 's' in keys and 'a' in keys: 
        player.sight.rotateAngle = 225
        player.swing.rotateAngle = 225
        
def onKeyPress(key): 
    if key == 'k': 
        player.dash()
    if key == 'o': 
        player.attack()
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
    player.attackSwing()

    whirlpool.timer += 1 
    if whirlpool.timer > 30 : 
        whirlpool.timer = 1 
    whirlpoolPhysics()

#spawnWhirlpool(200, 250, 'water')

cmu_graphics.run()