from cmu_graphics import * 
import Keybinds
import Sounds

app.stepsPerSecond = 120
app.background = 'gainsboro'

class GameState(object): 
    def __init__(self):
        self.mode = 'TITLE SCREEN'
        self.currentRoom = None 
        self.animations = AnimationManager()
        self.titleScreen = Group()

        self.worldList = ['tutorial']
        self.worldListIndex = 0 
        self.roomList = {'tutorial': ['???', 0,  ],  # worldName : [ Display Name, intended Progression ID, ]
                         } 
        self.roomListIndex = 2
        
        self.cover = Rect(0, 0, 400, 400, opacity = 0)

        self.animating = False
        self.startAnimationTimer = 0
        self.animationComplete = False
        self.cursor = Circle(0, 0, 10, border = 'red', fill = None) 

        self.cursorX = 200
        self.cursorY = 200

        Sounds.Titlescreen.set_volume(0.5)
        Sounds.Titlescreen.play(loop = True)

    def startGame(self): 
        self.animationComplete = False
        self.currentRoom = CurrentRoomState()
        game.currentRoom.thingsThatDamageNPCs.append([player.swing, 4, None])
        self.cover.opacity = 0
        self.mode = 'PLAYING'
        player.drawing.visible = True 
        Sounds.Titlescreen.pause()
        game.currentRoom.loadNewRoom(TutorialRoom1, 'TUTORIAL SPAWN')
        
    def beginStartingAnimation(self): 
        self.animating = True

    def animate(self): 
        self.startAnimationTimer += 1
        mValue = mapValue(1, 0, 480, 0, 100)
        if self.startAnimationTimer <= 480 : 
            if self.cover.opacity + mValue > 100: 
                self.cover.opacity = 100
            else: 
                self.cover.opacity += mValue
        else: 
            self.animating = False
            self.animationComplete = True

    def handleOnStep(self): 
        self.cursor.centerX = self.cursorX
        self.cursor.centerY = self.cursorY
        
        if self.animating == True : 
            self.animate()
        if self.animationComplete == True: 
            self.startGame()
        
    def handleMousePress(self): 
        self.beginStartingAnimation()
    def handleMouseMove(self, x, y): 
        self.cursorX = x 
        self.cursorY = y
        
class CurrentRoomState(object): 
    def __init__(self): 
        self.attributes = { 
            'lightLevel' : 0,
            'slippery' : False, 
            'hasBoss' : False, 
            'hasEnemies' : False, 
            'hasCollectibles' : False, 
            'checkpoint' : False, 
            'savepoint' : False, 
        } 
        self.walls = Group()
        self.thingsWithCollision = Group(self.walls)

                                    # [[thing to hit test, damageAmmount, class (used to clear thing)]]
        self.thingsThatDamagePlayer = []
        self.thingsThatDamageNPCs   = []
        
        self.world = game.roomList[game.worldList[game.worldListIndex]]
        self.room = TutorialRoom1()
        self.roomID = self.room.roomID

        self.items = [ ]

        self.allNPCs = []

    def handleOnStep(self): 
        self.loadingZoneLogic()

    def loadNewRoom(self, newRoom, entrance): # (class of the room to load, which direction its getting loaded from)
        if newRoom != None: 
            self.walls.clear()
            self.room = newRoom()
            for attr in self.attributes: 
                self.attributes[attr] = self.room.attributes[attr]
            self.room.load()
        
            player.moveTo(self.room.exits[entrance][0], self.room.exits[entrance][1])
            game.cover.opacity = 100 - self.attributes['lightLevel']*10

            game.cover.toFront()
            player.drawing.toFront()
            game.cursor.toFront

    def loadingZoneLogic(self): 
        if player.hitbox.centerX < -5 : 
            self.room.loadingZone('LEFT')
        if player.hitbox.centerX > 405 : 
            self.room.loadingZone('RIGHT')
        if player.hitbox.centerY < -5 : 
            self.room.loadingZone('TOP')
        if player.hitbox.centerY > 405 : 
            self.room.loadingZone('BOTTOM')
        else: 
            pass

###################################
###### START OF PLAYER CLASS ######
###################################

class Player (object): 
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
    
        self.maxHealth = 4 + level*4
        self.health = self.maxHealth

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
        self.swing
        
        self.hasShoot = False
        self.canShoot = True
        self.bullets = [ ]
        self.shootDelay = 180 - 30*self.shootMod
        self.shootCooldown = 0

        self.coolDownTimerList = [self.swingCooldown, self.shootCooldown]
    
    def draw(self, cx, cy, level): 
        self.sight = Arc(cx, cy, level*15 + 50, level*15 + 50, -45, 90, fill = 'white', opacity = 25)
        self.body = Circle(cx, cy, 7, fill = 'white', border = 'black')
        self.hitbox = Rect(cx, cy, 15, 15, fill = 'green', opacity = 0, align = 'center')
        self.swing = Arc(cx, cy, 30*level, 30*level, -55, 10, fill = 'saddleBrown', opacity = 0)
        self.drawing = Group(self.sight, self.body, self.swing, self.hitbox)
        self.drawing.visible = False 
        
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
                    if game.currentRoom.walls.hitsShape(self.hitbox) == True: 
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
        # Define the sides of the player as a list
        sides = [(self.hitbox.right, self.hitbox.centerY, -self.speed, 0), # Right side
                (self.hitbox.left, self.hitbox.centerY, self.speed, 0), # Left side
                (self.hitbox.centerX, self.hitbox.top, 0, self.speed), # Top side
                (self.hitbox.centerX, self.hitbox.bottom, 0, -self.speed)] # Bottom side
        # Loop through each side and check for collision with the walls
        for x, y, dx, dy in sides:
            if game.currentRoom.thingsWithCollision.hits(x, y):
                # Move the player away from the wall by the speed amount
                self.drawing.centerX += dx
                self.drawing.centerY += dy

    def takesDamage(self):
            for hurtyItem in [item for item in game.currentRoom.thingsThatDamagePlayer if item[0].opacity != 0]:
                if self.hitbox.hitsShape(hurtyItem[0]):
                    if self.justTookDamageLastCycle == False:
                        self.health -= hurtyItem[1]
                        print(self.health)
                        self.justTookDamageLastCycle = True
                        if hurtyItem[2] != None:
                            hurtyItem[2].clear()
                else:
                    self.justTookDamageLastCycle = False

    def swingAttack(self): 
        if self.canSwing == True and player.hasSwing == True:
            self.attacking = True 
            self.canSwing = False
            self.swingCooldown = self.swingDelay
    
    def swingAttackAnimation(self): 
        if self.attacking == True: 
            self.swing.opacity = 75
            finishAngle = self.sight.rotateAngle + 95
            self.swing.rotateAngle += (1.5 + .75*self.swingMod)
            
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
            game.currentRoom.thingsThatDamageNPCs.append([bullet.drawing, 2, bullet])
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
        if self.health <= 0:
            self.die()
        if self.shootCooldown == 0: 
            self.canShoot = True 
        if self.swingCooldown == 0: 
            self.canSwing = True
        if self.dashCooldown == 0: 
            self.canDash = True

    def collect(self): 
        for item in game.currentRoom.items: 
            if distance(self.hitbox.centerX, self.hitbox.centerY, item.hitbox.centerX, item.hitbox.centerY) < 30: 
                item.hasBeenCollected()

    def die(self):
        # Not sure what we want to happen when the player is dead
        print('player is dead')

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
        self.lookRotation(game.cursorX, game.cursorY)
        self.collision()
        self.takesDamage()
        self.swingAttackAnimation()
        self.shootPhysics()
        self.dash()
        self.updatePlayer()
        self.currentAction = self.actions[self.currentActionIndex]
        self.manageTimers()
    def handleMousePress(self, x, y): 
        if game.currentRoom.roomID != 0 : 
            if self.currentAction == 'swing': 
                self.swingAttack()
                
            if self.currentAction == 'shoot' : 
                self.shooting = False
                self.shoot()

            if self.currentAction == 'dash' and self.isDashing == False and self.canDash == True and self.hasDash == True:
                self.dashToX, self.dashToY = self.getDashDestination()
                self.isDashing = True
                self.dashRange = Group(Line(self.hitbox.centerX, self.hitbox.centerY, self.dashToX, self.dashToY, fill = 'blue', opacity = 25))

################################
###### START OF NPC CLASS ######
################################
                
class NPC(object):
    
    def __init__(self, cx, cy, rotationAngle, level, sightDistance, colour):
        self.draw(cx, cy, rotationAngle, sightDistance, colour, level)
        
        self.dx = 0
        self.dy = 0
        self.dr = 1
        self.speed = 0.5 # Could change based on level
        self.followPlayer = True

        self.maxHealth = 4 + level*4
        self.health = self.maxHealth

        self.moveMod = 0 
        self.shootMod = 0 
        self.swingMod = 0
        self.dashMod = 0 

        self.justTookDamageLastCycle = False

        self.hasSwing = True
        self.canSwing = True 
        self.attacking = False
        self.swingDelay = 240 - 30*self.swingMod
        self.swingCooldown = 0
        game.currentRoom.thingsThatDamagePlayer.append([self.swing, 4, None])
        
    def draw(self, cx, cy, rotationAngle, sightDistance, colour, level):
        self.sight = Arc(cx, cy, sightDistance*10 + 50, sightDistance*10 + 50, -45, 90, fill = 'lightGrey', opacity = 50, rotateAngle = rotationAngle)
        self.body = Circle(cx, cy, 7, fill = colour, border = 'black')
        self.hitbox = Rect(cx, cy, 15, 15, fill = 'green', opacity = 25, align = 'center')
        self.swing = Arc(cx, cy, 40+10*level, 40+10*level, -55, 10, fill = 'saddleBrown')
        self.drawing = Group(self.sight, self.hitbox, self.swing, self.body)

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
        if rotationAngle < 6:
            # Stop rotating
            direction = 0
            angle = angleTo(self.drawing.centerX, self.drawing.centerY, player.body.centerX, player.body.centerY)
            dx, dy = getPointInDir(0, 0, angle, 1)
            self.dx = dx
            self.dy = dy
            self.move()

        # Update the rotation angle based on the rotation direction
        finalAngle = (self.sight.rotateAngle + direction * self.dr) % 360
        self.sight.rotateAngle = finalAngle
        self.swing.rotateAngle = finalAngle

    def attemptMove(self):
        if self.followPlayer and self.attacking == False:
            self.sightLine()

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
            if game.currentRoom.thingsWithCollision.hits(x, y):
                # Move the sprite away from the wall by the speed amount
                self.drawing.centerX += dx
                self.drawing.centerY += dy
            for NPC in game.currentRoom.allNPCs:
                if NPC != self:
                    if NPC.hitbox.hits(x,y):
                        self.drawing.centerX += dx
                        self.drawing.centerY += dy
            if player.hitbox.hits(x,y):
                self.drawing.centerX += dx
                self.drawing.centerY += dy

    def takesDamage(self):
        for hurtyItem in [item for item in game.currentRoom.thingsThatDamageNPCs if item[0].opacity != 0]:
            if self.hitbox.hitsShape(hurtyItem[0]):
                if self.justTookDamageLastCycle == False:
                    self.health -= hurtyItem[1]
                    print(self.health)
                    self.justTookDamageLastCycle = True
                    if hurtyItem[2] != None:
                        hurtyItem[2].clear()
            else:
                self.justTookDamageLastCycle = False

    def attackLogic(self):
        if self.sight.hitsShape(player.hitbox):
            self.swingAttack()

    def swingAttack(self): 
        if self.canSwing == True and self.hasSwing == True:
            self.attacking = True 
            self.canSwing = False
            self.swingCooldown = self.swingDelay
    
    def swingAttackAnimation(self): 
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

    def manageTimers(self): 
        if self.swingCooldown != 0:
           self.swingCooldown -= 1
        # if self.shootCooldown != 0: # Not implemented yet (or ever)
        #    self.shootCooldown -= 1
        # if self.dashCooldown != 0: 
        #     self.dashCooldown -= 1
    def updatePlayer(self): 
        if self.health <= 0:
            self.die()
        if self.swingCooldown == 0: 
            self.canSwing = True
        # if self.shootCooldown == 0: # Not implemented yet (or ever)
        #     self.canShoot = True 
        # if self.dashCooldown == 0: 
        #     self.canDash = True

    def die(self):
        # Can add a death sound ext here
        self.clear()

    def clear(self):
        game.currentRoom.allNPCs.remove(self)
        self.drawing.clear()

    def handleOnStep(self):
        self.attemptMove()
        self.collision()
        self.takesDamage()
        if self.attacking == True:
            self.swingAttackAnimation()
        else:
            self.swing.opacity = 0 
        self.updatePlayer()
        self.manageTimers()
        if self.sight.hitsShape(player.hitbox):
            self.swingAttack()

##########################
###### ITEM CLASSES ######
##########################

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
        if self.itemType == 'dashItem' and player.hasDash == False: 
            player.hasDash = True
            player.actions.append('dash')
        if self.itemType == 'swingItem' and player.hasSwing == False: 
            player.hasSwing = True
            player.actions.append('swing')
        if self.itemType == 'shootItem' and player.hasShoot == False: 
            player.hasShoot = True
            player.actions.append('shoot')
    
    
    def clear(self): 
        self.drawing.clear()

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
        tempList = []
        for sublist in game.currentRoom.thingsThatDamageNPCs:
            if self not in sublist:
                tempList.append(sublist)
        if self in [item for sublist in game.currentRoom.thingsThatDamageNPCs for item in sublist]:
            game.currentRoom.thingsThatDamageNPCs = tempList
        if self in [item for sublist in game.currentRoom.thingsThatDamagePlayer for item in sublist]:
            game.currentRoom.thingsThatDamagePlayer = tempList
    def handleOnStep(self): 
        if self.drawing.centerX > 810 or self.drawing.centerX < -10 or self.drawing.centerY > 610 or self.drawing.centerY < -10 : 
            self.clear()
        if self.drawing.hitsShape(game.currentRoom.thingsWithCollision) == True : 
            self.clear()

###########################
###### CMU FUNCTIONS ######
###########################

class AnimationManager (object): 
    def __init__(self): 
        pass 

class Room (object): 
    def __init__(self): 
        self.attributes = { 
            'lightLevel' : 10,
            'slippery' : False, 
            'hasBoss' : False, 
            'hasEnemies' : False, 
            'hasCollectibles' : False, 
            'checkpoint' : False, 
            'savepoint' : False, 
        } 
        self.walls = Group()
        self.roomID = ' '
        
        self.exitLabels = ['TOP', 'BOTTOM', 'LEFT', 'RIGHT']
        self.exits = { # Direction : spawnX, spawnY
            'TOP' : [200, 395, None], 
            'BOTTOM' : [200, 5, None], 
            'LEFT' : [395, 200, None], 
            'RIGHT' : [5, 200, None], 
            'TUTORIAL SPAWN' : [200, 350, None] 
            }
        self.wallList = [[0, 0, 125, 'h'], [275, 0, 150, 'h'], [0, 390, 125, 'h'], [275, 390, 150, 'h'], 
                         [390, 0, 125, 'v'], [390, 275, 125, 'v'], [0, 0, 125, 'v'], [0, 275, 125, 'v']]
        
        self.exitBlockers = {'TOP' : [0, 0, 400, 'h'], 
                             'BOTTOM' : [0, 390, 400, 'h'], 
                             'LEFT' : [0, 0, 400, 'v'], 
                             'RIGHT' : [390, 0, 400, 'v']} # [TOP, BOTTOM, LEFT, RIGHT]
    def loadWalls(self): 
        for label in self.exitLabels : 
            if self.exits[label][2] == None: 
                self.wallList.append(self.exitBlockers[label])
        for wall in self.wallList:
            self.walls.add(buildWall(wall[0], wall[1], wall[2], wall[3]))
                
        game.currentRoom.walls.clear() 
        game.currentRoom.walls = self.walls 
    
    def loadingZone(self, direction): 
        zone = self.exits[direction][2]
        game.currentRoom.loadNewRoom(zone, direction)
    
    def load(self): 
        self.loadWalls()

class TestRoom (object): 
    def __init__(self):
        self.attributes = { 
            'lightLevel' : 10,
            'slippery' : False, 
            'hasBoss' : False, 
            'hasEnemies' : True, 
            'hasCollectibles' : True, 
            'checkpoint' : False, 
            'savepoint' : False, 
        } 
        self.roomID = 'testRoom'
    def load(self): 
        for i in self.attributes : 
            game.currentRoom.attributes[i] = self.attributes[i]

class TutorialRoom1 (Room): 
    def __init__(self): 
        super().__init__()
        self.exits['TOP'][2] = TutorialRoom2
    
class TutorialRoom2 (Room): 
    def __init__(self): 
        super().__init__()
        self.exits['BOTTOM'][2] = TutorialRoom1
        self.exits['RIGHT'][2] = TutorialRoom3
        
class TutorialRoom3 (Room): 
    def __init__(self): 
        super().__init__()
        self.exits['LEFT'][2] = TutorialRoom2
        self.exits['RIGHT'][2] = TutorialRoom4

class TutorialRoom4 (Room): 
    def __init__(self): 
        super().__init__() 
        self.exits['LEFT'][2] = TutorialRoom3

###########################
###### CMU FUNCTIONS ######
###########################

def onKeyHold(keys):     
    if 'MENU' not in game.mode and game.currentRoom != None : 
        player.handleOnKeys(keys)
def onKeyPress(key): 
    if 'MENU' not in game.mode and game.currentRoom != None : 
        player.handleKeyPress(key)

### debug ###
    if key == 'left': 
        game.currentRoom.room.loadingZone('LEFT')
    if key == 'right':
        game.currentRoom.room.loadingZone('RIGHT')
    if key == 'up':
        game.currentRoom.room.loadingZone('TOP')
    if key == 'down':
        game.currentRoom.room.loadingZone('BOTTOM')

def onMouseMove(x, y): 
    game.handleMouseMove(x, y)
def onMouseDrag(x, y): 
    game.handleMouseMove(x, y)
def onMousePress(x, y): 
    if game.currentRoom != None : 
        player.handleMousePress(x, y)
    if game.mode == 'TITLE SCREEN': 
        game.handleMousePress()
def onStep(): 
    if 'MENU' not in game.mode and game.currentRoom != None : 
        player.handleOnStep() 
        game.currentRoom.handleOnStep() 
        for enemy in game.currentRoom.allNPCs:
            enemy.handleOnStep()
    game.handleOnStep()

def mapValue(value, valueMin, valueMax, targetMin, targetMax):
    ratio = (value-valueMin) / (valueMax-valueMin)
    result = ratio * (targetMax-targetMin) + targetMin
    return result

def orientation(x1, y1, x2, y2, type): # Not realy used... sorry Jonah
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

##########################
###### MAP BUILDING ######
##########################

def buildWall(x, y, size, type): # h for horizontal, v for vertical
    if type == 'h': 
        wall = Rect(x, y, size, 10)
    if type == 'v': 
        wall = Rect(x, y, 10, size)
    return wall

###########################
###### STARTING GAME ######
###########################

game = GameState()
player = Player(200, 300, 5)

# enemy1 = NPC(50, 50, 0, 0, 5, 'red')
# enemy2 = NPC(300, 300, 0, 1, 5, 'red')
# enemy2.hasSwing = True
# game.room.allNPCs.append(enemy1)
# game.room.allNPCs.append(enemy2)

# for i in range(1):
#     e = NPC(10+i*50, 10+i*50, 0, 0, 5, 'red')
#     game.currentRoom.allNPCs.append(e)

cmu_graphics.run()