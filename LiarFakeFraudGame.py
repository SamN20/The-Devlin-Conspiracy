from cmu_graphics import * 
import Keybinds

app.stepsPerSecond = 120

class GameState(object): 
    def __init__(self):
        self.mode = 'TEST ROOM'
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
        self.walls = Group(Rect(100, 100, 10, 100))
        self.thingsWithCollision = Group(self.walls)
        
        self.cursorX = 200
        self.cursorY = 200
        self.roomID = 1 # roomID of 0 is for menus, 1 for test map

        self.items = [Item(200, 100, 'dashItem'), Item(250, 100, 'swingItem'), Item(300, 100, 'shootItem')]

        self.cursor = Circle(0, 0, 10, border = 'red', fill = None)

        self.allNPCs = []

    def handleOnStep(self): 
        self.cursor.centerX = self.cursorX
        self.cursor.centerY = self.cursorY

class Player(object): 
    def __init__(self, cx, cy, level): 
        self.draw(cx, cy, level)
        
        self.moveMod = 0 
        self.shootMod = 0 
        self.swingMod = 0
        self.dashMod = 0 

        self.dx = 0
        self.dy = 0
        self.speed = 0.5 + 0.25*self.moveMod
        self.canMove = True
    
        self.actions = [None]
        self.currentActionIndex = 0
        self.currentAction = self.actions[self.currentActionIndex]
        
        self.hasDash = False
        self.canDash = True
        self.dashDistance = 75 + 25*self.dashMod
        self.dashSpeed = 1.5 + 0.5*self.dashMod
        self.isDashing = False
        self.dashDelay = 240 - 30*self.dashMod
        self.dashCooldown = 0
        
        self.hasSwing = False
        self.canSwing = True 
        self.attacking = False
        self.swingDelay = 240 - 30*self.swingMod
        self.swingCooldown = 0
        
        self.hasShoot = False
        self.canShoot = True
        self.bullets = [ ]
        self.shootDelay = 180 - 30*self.shootMod
        self.shootCooldown = 0

        self.coolDownTimerList = [self.swingCooldown, self.shootCooldown]
    
    def draw(self, cx, cy, level): 
        self.sight = Arc(cx, cy, level*15 + 50, level*15 + 50, -45, 90, fill = 'gainsboro', opacity = 50)
        self.body = Circle(cx, cy, 7, fill = 'white', border = 'black')
        self.hitbox = Rect(cx, cy, 15, 15, fill = 'green', opacity = 25, align = 'center')
        self.swing = Arc(cx, cy, 30*level, 30*level, -55, 10, fill = 'saddleBrown')
        self.drawing = Group(self.sight, self.body, self.swing, self.hitbox)
    
    def movement(self, key): 
        controls = {
            Keybinds.up : [0, -self.speed], 
            Keybinds.down : [0, self.speed], 
            Keybinds.left : [-self.speed, 0], 
            Keybinds.right : [self.speed, 0], 
            }
        if key in controls : 
            self.drawing.centerX += controls[key][0]
            self.drawing.centerY += controls[key][1]

    def moveTo(self, x, y):
        for drawingPiece in self.drawing:
            drawingPiece.centerX, drawingPiece.centerY = x, y

    def getDashDestination(self):
        return getPointInDir(self.hitbox.centerX, self.hitbox.centerY, self.sight.rotateAngle, self.dashDistance)

    def dash(self):
        if self.canDash == True and self.hasDash == True: 
            if self.isDashing == True: 
                dist = distance(self.dashToX, self.dashToY, self.hitbox.centerX, self.hitbox.centerY)
                if dist < self.dashSpeed:
                    self.moveTo(self.dashToX, self.dashToY)
                    self.isDashing = False
                    self.dashCooldown = self.dashDelay
                    self.canDash = False
                    self.dashRange.clear()
                else:
                    angle = angleTo(self.hitbox.centerX, self.hitbox.centerY, self.dashToX, self.dashToY)
                    x, y = getPointInDir(self.hitbox.centerX, self.hitbox.centerY, angle, self.dashSpeed)
                    if game.room.walls.hitsShape(self.hitbox) == True: 
                        self.isDashing = False
                        self.dashCooldown = self.dashDelay
                        self.canDash = False
                        self.dashRange.clear()
                    else:
                        self.moveTo(x, y)

    def lookRotation(self, x, y): 
        angle = angleTo(self.hitbox.centerX, self.hitbox.centerY, x, y)
        if self.attacking == False : 
            self.sight.rotateAngle = angle
            self.swing.rotateAngle = angle
    
    def collision(self): 
        # Define the sides of the sprite as a list of tuples
        sides = [(self.hitbox.right, self.hitbox.centerY, -self.speed, 0), # Right side
                (self.hitbox.left, self.hitbox.centerY, self.speed, 0), # Left side
                (self.hitbox.centerX, self.hitbox.top, 0, self.speed), # Top side
                (self.hitbox.centerX, self.hitbox.bottom, 0, -self.speed)] # Bottom side
        # Loop through each side and check for collision with the walls
        for x, y, dx, dy in sides:
            if game.room.walls.hits(x, y):
                # Move the sprite away from the wall by the speed amount
                self.drawing.centerX += dx
                self.drawing.centerY += dy

    def swingAttack(self): 
        if self.canSwing == True and player.hasSwing == True:
            self.attacking = True 
            self.canSwing = False
            self.swingCooldown = self.swingDelay
    
    def attackSwing(self): 
        if self.attacking == True: 
            self.swing.opacity = 75
            finishAngle = self.sight.rotateAngle + 95
            self.swing.rotateAngle += (3 + 1.5*self.swingMod)
            
            if self.swing.rotateAngle >= finishAngle:
                self.attacking = False
                self.swing.opacity = 0
                self.swing.rotateAngle = self.sight.rotateAngle
                
        else: 
            self.swing.opacity = 0 
        
    def shoot(self): 
        if self.canShoot == True: 
            bullet = Projectile(self.hitbox.centerX, self.hitbox.centerY, self.sight.rotateAngle, 'red')
            self.bullets.append(bullet)
            self.shootCooldown = self.shootDelay
            self.canShoot = False
            
    def shootPhysics(self): 
        for bullet in self.bullets : 
            bullet.move('basic', 0.5*self.shootMod)
            bullet.handleOnStep()
            if bullet.loaded == False : 
                self.bullets.remove(bullet)
    
    def manageTimers(self): 
        if self.swingCooldown != 0:
           self.swingCooldown -= 1
        if self.shootCooldown != 0:
           self.shootCooldown -= 1
        if self.dashCooldown != 0: 
            self.dashCooldown -= 1
    def updatePlayer(self): 
        if self.shootCooldown == 0: 
            self.canShoot = True 
        if self.swingCooldown == 0: 
            self.canSwing = True
        if self.dashCooldown == 0: 
            self.canDash = True

    def collect(self): 
        for item in game.room.items: 
            if distance(self.hitbox.centerX, self.hitbox.centerY, item.hitbox.centerX, item.hitbox.centerY) < 30: 
                item.hasBeenCollected()

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
            if self.canMove and self.isDashing == False:
                self.movement(key)
    def handleKeyPress(self, key): 
        self.handleActionIndex(key)
        if key == Keybinds.collect: 
            self.collect()
    def handleOnStep(self): 
        self.lookRotation(game.room.cursorX, game.room.cursorY)
        self.collision()
        self.attackSwing()
        self.shootPhysics()
        self.dash()
        self.updatePlayer()
        self.currentAction = self.actions[self.currentActionIndex]
        self.manageTimers()
    def handleMousePress(self, x, y): 
        if game.room.roomID != 0 : 
            if self.currentAction == 'swing': 
                self.swingAttack()
                
            if self.currentAction == 'shoot' : 
                self.shooting = False
                self.shoot()

            if self.currentAction == 'dash' and self.isDashing == False and self.canDash == True and self.hasDash == True:
                self.dashToX, self.dashToY = self.getDashDestination()
                self.isDashing = True
                self.dashRange = Group(Line(self.hitbox.centerX, self.hitbox.centerY, self.dashToX, self.dashToY, fill = 'blue', opacity = 25))

class NPC(object):
    
    def __init__(self, cx, cy, rotationAngle, xpLevel, sightDistance, colour):
        self.dx = 0
        self.dy = 0
        self.dr = 1
        self.speed = 0.5 # Could change based on xpLevel
        self.followPlayer = True

        self.draw(cx, cy, rotationAngle, sightDistance, colour)
        
    def handleOnStep(self):
        self.attemptMove()
        self.collision()

    def sightLine(self):
        targetAngle = angleTo(self.drawing.centerX, self.drawing.centerY, player.body.centerX, player.body.centerY)

        # Calculate the shortest rotation angle needed to reach the target angle
        rotationAngle = (targetAngle - self.sight.rotateAngle) % 360

        # Determine the direction of rotation needed to reach the target angle
        if rotationAngle > 180:
            # Rotate counterclockwise
            direction = -1
            rotationAngle = 360 - rotationAngle
        else:
            # Rotate clockwise
            direction = 1

        # Check if the rotation angle is within 3 degrees of the target angle
        if rotationAngle < 3:
            # Stop rotating
            direction = 0
            angle = angleTo(self.drawing.centerX, self.drawing.centerY, player.body.centerX, player.body.centerY)
            dx, dy = getPointInDir(0, 0, angle, 1)
            self.dx = dx
            self.dy = dy
            self.move()
            
        # Update the rotation angle based on the rotation direction
        self.sight.rotateAngle = (self.sight.rotateAngle + direction * self.dr) % 360

    def attemptMove(self):
        if self.followPlayer:
            self.sightLine()
            # self.move_away_from_npcs(allNPCs, player)

    def move_away_from_npcs(self):
    #     # Loop through all NPCs in the game
    #     for NPC in allNPCs:
    #         # Check if the NPC is not itself and if it's colliding with the current NPC
    #         if NPC != self and self.hitbox.hitsShape(NPC.hitbox):
    #             # Calculate the overlap between the two NPCs 
    #             dx = min(self.hitbox.right, NPC.hitbox.right) - max(self.hitbox.left, NPC.hitbox.left)
    #             dy = min(self.hitbox.bottom, NPC.hitbox.bottom) - max(self.hitbox.top, NPC.hitbox.top)
    #             if dx > 0 and dy > 0:
    #                 # There is an overlap, calculate the amount of overlap
    #                 overlapX = min(abs(dx), self.hitbox.width + NPC.hitbox.width - abs(dx))
    #                 overlapY = min(abs(dy), self.hitbox.height + NPC.hitbox.height - abs(dy))
    #                 overlap = min(overlapX, overlapY)
    #                 if overlap > 0:
    #                     # Calculate the direction between the two NPCs
    #                     dx = self.drawing.centerX - NPC.drawing.centerX
    #                     dy = self.drawing.centerY - NPC.drawing.centerY
    #                     length = math.sqrt(dx**2 + dy**2)
    #                     if length != 0:
    #                         dx /= length
    #                         dy /= length

    #                     # Move the two NPCs away from each other
    #                     # We divide by 2 to ensure that they both move away from each other equally
    #                     self.drawing.centerX += dx * overlap / 2
    #                     self.drawing.centerY += dy * overlap / 2
    #                     NPC.drawing.centerX -= dx * overlap / 2
                        # NPC.drawing.centerY -= dy * overlap / 2
        pass

    def move(self):
        self.drawing.centerX += self.dx * self.speed
        self.drawing.centerY += self.dy * self.speed

    def collision(self):
        # Define the sides of the sprite as a list of tuples
        sides = [(self.hitbox.right, self.hitbox.centerY, -self.speed, 0), # Right side
                (self.hitbox.left, self.hitbox.centerY, self.speed, 0), # Left side
                (self.hitbox.centerX, self.hitbox.top, 0, self.speed), # Top side
                (self.hitbox.centerX, self.hitbox.bottom, 0, -self.speed)] # Bottom side
        # Loop through each side and check for collision with the walls
        for x, y, dx, dy in sides:
            if game.room.walls.hits(x, y):
                # Move the sprite away from the wall by the speed amount
                self.drawing.centerX += dx
                self.drawing.centerY += dy
            for NPC in game.room.allNPCs:
                if NPC != self:
                    if NPC.hitbox.hits(x,y):
                        self.drawing.centerX += dx
                        self.drawing.centerY += dy

    def draw(self, cx, cy, rotationAngle, sightDistance, colour):
        self.sight = Arc(cx, cy, sightDistance*10 + 50, sightDistance*10 + 50, -45, 90, fill = 'lightGrey', opacity = 50, rotateAngle = rotationAngle)
        self.body = Circle(cx, cy, 7, fill = colour, border = 'black')
        self.hitbox = Rect(cx, cy, 15, 15, fill = 'green', opacity = 25, align = 'center')
        self.drawing = Group(self.body, self.sight, self.hitbox)

class Projectile(object): 
    def __init__(self, cx, cy, angle, colour):
        self.drawing = Group(Circle(cx, cy, 3, fill = colour))
        self.moveX, self.moveY = getPointInDir(cx, cy, angle, 100)
        self.angle = angle
        self.loaded = True

    def move(self, type, modifier): 
        if type == 'basic' : 
            self.nextX, self.nextY = getPointInDir(self.drawing.centerX, self.drawing.centerY, self.angle, 3 + modifier)
            self.drawing.centerX = self.nextX
            self.drawing.centerY = self.nextY
    def clear(self): 
        self.loaded = False
        self.drawing.clear()
    def handleOnStep(self): 
        if self.drawing.centerX > 810 or self.drawing.centerX < -10 or self.drawing.centerY > 610 or self.drawing.centerY < -10 : 
            self.clear()
        if self.drawing.hitsShape(game.room.thingsWithCollision) == True : 
            self.clear()

class Item (object): 
    def __init__(self, cx, cy, type): 
        self.itemType = type
        self.draw(cx, cy)
    def draw(self, cx, cy): 
        self.hitbox = Circle(cx, cy, 5, opacity = 0)
        if self.itemType == 'dashItem': 
            self.model = Group(Rect(cx, cy, 6, 3, fill = 'saddleBrown'), Rect(cx+9, cy, 6, 3, fill = 'saddleBrown'), 
                               Rect(cx+3, cy-6, 3, 6, fill = 'maroon'), Rect(cx+9, cy-6, 3, 6, fill = 'maroon'))
            self.model.centerX, self.model.centerY = self.hitbox.centerX, self.hitbox.centerY
        if self.itemType == 'swingItem': 
            self.model = Group(Line(cx, cy, cx+5, cy-5, fill = 'saddleBrown'), Line(cx+2, cy-9, cx+9, cy-2), 
                            Line(cx+6, cy-6, cx+18, cy-18, fill = 'saddleBrown', lineWidth = 4))
            self.model.centerX, self.model.centerY = self.hitbox.centerX, self.hitbox.centerY
        if self.itemType == 'shootItem': 
            self.model = Group(Line(cx, cy, cx+13, cy-13), Circle(cx+13, cy-13, 4, fill = 'red'))
            self.model.centerX, self.model.centerY = self.hitbox.centerX, self.hitbox.centerY
        
        self.drawing = Group(self.hitbox, self.model)

    def hasBeenCollected(self): 
        self.clear()
        if None in player.actions: 
            player.actions.remove(None)
        if self.itemType == 'dashItem': 
            player.hasDash = True
            player.actions.append('dash')
        if self.itemType == 'swingItem': 
            player.hasSwing = True
            player.actions.append('swing')
        if self.itemType == 'shootItem': 
            player.hasShoot = True
            player.actions.append('shoot')
    
    
    def clear(self): 
        self.drawing.clear()

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
    for enemy in game.room.allNPCs:
        enemy.handleOnStep()

def mapValue(value, valueMin, valueMax, targetMin, targetMax):
    ratio = (value-valueMin) / (valueMax-valueMin)
    result = ratio * (targetMax-targetMin) + targetMin
    return result

def orientation(x1, y1, x2, y2, type): 
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
    if type == 'yAxis' : 
        if (angle >= 0 and angle < 180): 
            return 'right'
        if (angle >= 180 and angle < 360): 
            return 'left'
    if type == 'xAxis' : 
        if (angle >= 270 and angle < 360) or (angle >= 0 and angle < 90): 
            return 'above'
        if (angle >= 90 and angle < 180) or (angle >= 180 and angle < 270): 
            return 'below'

game = GameState()
player = Player(200, 300, 5)
enemy1 = NPC(50, 50, 0, 5, 5, 'red')
enemy2 = NPC(300, 300, 0, 5, 5, 'red')
game.room.allNPCs.append(enemy1)
game.room.allNPCs.append(enemy2)

cmu_graphics.run()