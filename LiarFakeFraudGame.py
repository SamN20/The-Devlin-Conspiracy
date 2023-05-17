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
        self.drawTitleScreen()
        self.drawPauseMenu()

        self.worldList = ['tutorial']
        self.worldListIndex = 0 
        self.roomList = {'tutorial': ['???', 0],  # worldName : [ Display Name, intended Progression ID]
                         } 
        self.roomListIndex = 2
        
        self.globalItemList = { 
            'TutorialRoom4' : [True], 
            'TutorialRoom6' : [True]
        }

        self.globalNPCList = { 
            'TutorialRoom5' : [True, True], 
            'TutorialRoom7' : [True, True]
            }
        self.globalDoorList = { 
        }
        self.cover = Rect(0, 0, 400, 400, opacity = 0)

        self.animating = False
        self.startAnimationTimer = 0
        self.animationComplete = False
        self.cursor = Circle(0, 0, 10, border = 'red', fill = None) 

        self.cursorX = 200
        self.cursorY = 200

        Sounds.Titlescreen.set_volume(0.2)
        Sounds.Titlescreen.play(loop = True)

    def drawTitleScreen(self):
        backgroundImage = Image('Images/Title-Screen.png', 0, 0, width = 400, height = 400)
        backDrop = Rect(0, 18, 400, 62, fill = 'black', opacity = 30)
        TitleText = Label('The Devlin Conspiracy', 200, 35, size = 30, font = 'monospace', bold = True, fill = 'red', border = 'black', borderWidth = 1.5)
        SubText = Label('The Liar, The Fake, and The Fraud', 200, 65, size = 18, font = 'monospace', bold = True, fill = 'red', border = 'black', borderWidth = 1)
        backDrop2 = Rect(45, 367, 309, 16, fill = 'black', opacity = 30)
        ClickToStart = Label('Click Anywhere To Start Your Adventure', 200, 375, size = 13, font = 'monospace', bold = True, fill = 'red', border = 'black', borderWidth = 0.5)
        self.titleScreen.add(backgroundImage, backDrop, TitleText, SubText, backDrop2, ClickToStart)

    def startGame(self): 
        self.animationComplete = False
        self.currentRoom = CurrentRoomState()
        game.currentRoom.thingsThatDamageNPCs.append([player.swing, 4, None])
        self.cover.opacity = 0
        self.titleScreen.clear()
        self.mode = 'PLAYING'
        player.drawing.visible = True 
        game.currentRoom.loadNewRoom(TutorialRoom1, 'TUTORIAL SPAWN')
        Sounds.Tutorial.set_volume(0.2)
        Sounds.Tutorial.play(loop = True)

    def beginStartingAnimation(self): 
        Sounds.Titlescreen.fadeout(6000)
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

    def drawPauseMenu(self):
        self.pauseMenu = Group()
        self.pauseMenu.add(Rect(0, 0, 400, 400, fill = 'black', opacity = 50), 
                           Label('PAUSED', 200, 200, size = 30, font = 'monospace', bold = True, fill = 'red', border = 'black', borderWidth = 1.5))
        self.pauseMenu.visible = False

    def pause(self): 
        self.mode = 'PAUSED'
        self.pauseMenu.visible = True
        self.pauseMenu.toFront()

    def unpause(self): 
        self.mode = 'PLAYING'
        self.pauseMenu.visible = False

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
        self.thingsThatDamagePlayer = [ ]
        self.thingsThatDamageNPCs   = [ ]
        
        self.world = game.roomList[game.worldList[game.worldListIndex]]
        self.room = TutorialRoom1()
        self.roomID = self.room.roomID

        self.allItems = [ ]
        self.allNPCs = [ ]
        self.allDoors = [ ]

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
            player.isDashing = False
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

###################################
###### START OF PLAYER CLASS ######
###################################

class Player (object): 
    def __init__(self, cx, cy, level): 
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

        self.draw(cx, cy, level)

        self.actions = [None]
        self.currentActionIndex = 0
        self.currentAction = self.actions[self.currentActionIndex]
        self.showSelectedAction = False 
        self.currentActionIcon = None
        
        self.hasDash = False
        self.canDash = True
        self.dashDistance = 75 + 25*self.dashMod
        self.dashSpeed = 2 + 0.5*self.dashMod
        self.isDashing = False
        self.dashDelay = 240 - 30*self.dashMod
        self.dashCooldown = 0
        self.dashRange = Group()
        
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

        self.obtainedKeys = 0
        self.obtainedSpecialKeys = [ ]

    def draw(self, cx, cy, level): 
        self.sight = Arc(cx, cy, level*15 + 50, level*15 + 50, -45, 90, fill = 'white', opacity = 0)
        self.body = Circle(cx, cy, 7, fill = 'white', border = 'black')
        self.hitbox = Rect(cx, cy, 15, 15, fill = 'green', opacity = 0, align = 'center')
        self.swing = Arc(cx, cy, 30*level, 30*level, -55, 10, fill = 'saddleBrown', opacity = 0)
        self.drawing = Group(self.sight, self.body, self.swing, self.hitbox)
        self.drawing.visible = False 
        self.healthBar = HealthBar(self)
        
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
                    if game.currentRoom.thingsWithCollision.hitsShape(self.hitbox) == True: 
                        self.isDashing = False
                        self.dashCooldown = self.dashDelay
                        self.canDash = False
                        self.dashRange.clear()
                    else:
                        self.moveTo(x, y)
            else:
                self.dashRange.clear()

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
        if any([item[0].hitsShape(self.hitbox) for item in game.currentRoom.thingsThatDamagePlayer if item[0].opacity != 0]):
            self.justTookDamageLastCycle = True
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
    
    def showSelectedItem(self):
        if self.currentAction is not None and self.showSelectedAction:
            if self.currentActionIcon is not None:
                self.currentActionIcon.drawing.clear()
            self.showSelectedAction = False
            tempString = str(self.currentAction) + "Item"
            self.currentActionIcon = Item(self.hitbox.centerX, self.hitbox.centerY+20, tempString, None, None)
        if self.currentActionIcon != None:
            if self.currentActionIcon.model.opacity <= 0.5:
                self.currentActionIcon.drawing.clear()
                self.currentActionIcon = None
            else:
                self.currentActionIcon.model.centerX, self.currentActionIcon.model.centerY = self.hitbox.centerX, self.hitbox.centerY+20
                self.currentActionIcon.model.opacity -= 0.5

    def manageTimers(self): 
        if self.swingCooldown != 0:
           self.swingCooldown -= 1
        if self.shootCooldown != 0:
           self.shootCooldown -= 1
        if self.dashCooldown != 0: 
            self.dashCooldown -= 1
    def updatePlayer(self): 
        self.healthBar.updateHealthBar(self)
        if self.health <= 0:
            self.die()
        if self.shootCooldown == 0: 
            self.canShoot = True 
        if self.swingCooldown == 0: 
            self.canSwing = True
        if self.dashCooldown == 0: 
            self.canDash = True

    def collect(self): 
        for item in game.currentRoom.allItems: 
            if distance(self.hitbox.centerX, self.hitbox.centerY, item.hitbox.centerX, item.hitbox.centerY) < 30: 
                item.hasBeenCollected()

    def unlockDoor(self): 
        for door in game.currentRoom.allDoors : 
            if distance(self.hitbox.centerX, self.hitbox.centerY, door.drawing.centerX, door.drawing.centerY) < 30: 
                door.unlock()

    def die(self):
        # Not sure what we want to happen when the player is dead
        print('player is dead')

    def handleActionIndex(self, key): 
        if key == Keybinds.actionIndexDown : 
            self.currentActionIndex -= 1
            self.showSelectedAction = True
        if key == Keybinds.actionIndexUp : 
            self.currentActionIndex += 1
            self.showSelectedAction = True            
        
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
            self.unlockDoor()
    def handleOnStep(self): 
        self.lookRotation(game.cursorX, game.cursorY)
        self.collision()
        self.takesDamage()
        self.swingAttackAnimation()
        self.shootPhysics()
        self.dash()
        self.updatePlayer()
        self.currentAction = self.actions[self.currentActionIndex]
        self.showSelectedItem()
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
    
    def __init__(self, cx, cy, rotationAngle, level, sightDistance, colour, index):
       
        self.dx = 0
        self.dy = 0
        self.dr = 1
        self.speed = 0.5 # Could change based on level
        self.followPlayer = True
        
        self.index = index

        self.maxHealth = 4 + level*4
        self.health = self.maxHealth

        self.draw(cx, cy, rotationAngle, sightDistance, colour, level)

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
        self.healthBar = HealthBar(self)

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
        if any([item[0].hitsShape(self.hitbox) for item in game.currentRoom.thingsThatDamagePlayer if item[0].opacity != 0]):
            self.justTookDamageLastCycle = True
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
        self.healthBar.updateHealthBar(self)
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
        game.globalNPCList[game.currentRoom.roomID][self.index-1] = False
        
        self.clear()

    def clear(self):
        game.currentRoom.allNPCs.remove(self)
        self.drawing.clear()
        self.healthBar.clearHealthBar()

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
    def __init__(self, cx, cy, type, index, colour): 
        self.itemType = type
        self.index = index
        self.colour = colour
        self.playerUpgrades = ['dashItem', 'swingItem', 'shootItem']
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
        if self.itemType == 'flashlight': 
            self.model = Group(Line(cx, cy, cx, cy+10, lineWidth = 3, fill = 'dimGrey'), Line(cx, cy, cx, cy-2, lineWidth = 3, fill = 'yellow'), 
                               Arc(cx, cy, 20, 20, -45, 90, fill = 'yellow', opacity = 50))
        if self.itemType == 'keyItem' : 
            self.model = Group(Circle(cx, cy, 5, border = 'gold', fill = None, borderWidth = 2), Line(cx, cy-5, cx, cy-15, fill = 'gold'), 
                Line(cx, cy-15, cx+5, cy-15, fill = 'gold'), Line(cx, cy-10, cx+5, cy-10, fill = 'gold'))
        if self.itemType == 'specialKeyItem': 
            self.model = Group(Circle(cx, cy, 5, border = self.colour, fill = None, borderWidth = 2), Line(cx, cy-5, cx, cy-15, fill = self.colour), 
                Line(cx, cy-15, cx+5, cy-15, fill = self.colour), Line(cx, cy-10, cx+5, cy-10, fill = self.colour)) 
        
        self.drawing = Group(self.hitbox, self.model)

    def hasBeenCollected(self): 
        self.clear()
        game.globalItemList[game.currentRoom.roomID][self.index-1] = False
        if None in player.actions and self.itemType in self.playerUpgrades: 
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
        if self.itemType == 'flashlight': 
            player.sight.opacity = 25
        if self.itemType == 'keyItem' : 
            player.obtainedKeys += 1
        if self.itemType == 'specialKeyItem' : 
            player.obtainedSpecialKeys.append(self.colour)
    
    
    def clear(self): 
        self.drawing.clear()

class Obstacle (object): 
    def __init__(self, index, colour): 
        self.index = index
        self.colour = colour
        self.drawing = Group()
    def clear(self): 
        self.drawing.clear()
        

class Door (Obstacle) : 
    def __init__(self, cx, cy, type, index, colour, direction):
        super().__init__(index, colour)
        self.type = type
        self.draw(cx, cy, direction)
    def draw(self, cx, cy, direction): 
        door = buildWall(0, 0, 150, direction)
        door.height -= 2
        if self.type == 'NORMAL': 
            door.fill = 'grey'
        if self.type == 'SPECIAL': 
            door.fill = self.colour
            
        door.centerX, door.centerY = cx, cy
        self.drawing = Group(door)
    def unlock(self): 
        if self.type == 'NORMAL': 
            player.obtainedKeys -= 1 
        if self.type == 'SPECIAL': 
            if self.colour in player.obtainedSpecialKeys: 
                player.obtainedSpecialKeys.remove(self.colour)
        
        game.globalDoorList[game.currentRoom.roomID][self.index-1] = False
        self.clear()

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
        game.currentRoom.thingsThatDamageNPCs = [sublist for sublist in game.currentRoom.thingsThatDamageNPCs if self not in sublist]
        game.currentRoom.thingsThatDamagePlayer = [sublist for sublist in game.currentRoom.thingsThatDamagePlayer if self not in sublist]

    def handleOnStep(self): 
        if self.drawing.centerX > 410 or self.drawing.centerX < -10 or self.drawing.centerY > 410 or self.drawing.centerY < -10 : 
            self.clear()
        if self.drawing.hitsShape(game.currentRoom.thingsWithCollision) == True : 
            self.clear()

##################################
###### START OF GUI CLASSES ######
##################################

class HealthBar (object):
    def __init__(self, character): # character is the player/NPC that the health bar is for
        self.drawHealthBar(character.health, character.maxHealth, character)

    def updateHealthBar(self, character):
        if character.health != character.maxHealth:
            self.drawing.visible = character.drawing.visible
        self.middle.width = mapValue(character.health, 0, character.maxHealth, 0.1, 50) # 0.1 is the min width of the health bar (to prevent a rectangle with no width)
        self.drawing.centerX = character.hitbox.centerX
        self.drawing.bottom = character.hitbox.top - 5
        self.drawing.toFront()

    def drawHealthBar(self, health, maxHealth, character):
        x = character.hitbox.centerX
        y = character.hitbox.top - 5
        width=mapValue(health, 0, maxHealth, 0, 50) # 50 is the max width of the health bar
        self.outline = Rect(x, y, width+2, 5,  fill=None, border="black", borderWidth=1, align='bottom')
        self.middle = Rect(self.outline.left+1, self.outline.centerY, width, 2,  fill="green", align='left')
        self.drawing = Group(self.outline, self.middle)
        self.drawing.opacity = 50
        self.drawing.visible = False

    def clearHealthBar(self):
        self.drawing.clear()

##########################
###### ROOM CLASSES ######
##########################

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
        
        self.npcList = [ ]
        self.itemList = [ ]
        self.doorList = [ ]

        self.allNPCs = [ ]
        self.allItems = [ ]
        self.allDoors = [ ]

        self.exitLabels = ['TOP', 'BOTTOM', 'LEFT', 'RIGHT']
        self.exits = { # Direction : spawnX, spawnY, 
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
                             'RIGHT' : [390, 0, 400, 'v']} 
        
    def loadWalls(self): 
        for label in self.exitLabels : 
            if self.exits[label][2] == None: 
                self.wallList.append(self.exitBlockers[label])
        for wall in self.wallList:
            self.walls.add(buildWall(wall[0], wall[1], wall[2], wall[3]))

                
        game.currentRoom.walls.clear() 
        game.currentRoom.thingsWithCollision.clear() 
        game.currentRoom.walls = self.walls 
        for wall in self.walls:
            game.currentRoom.thingsWithCollision.add(wall)
    
    def loadNPCs(self): 
        for enemy in self.npcList : 
            if game.globalNPCList[game.currentRoom.roomID][enemy[6]-1] : 
                self.allNPCs.append(NPC(enemy[0], enemy[1], enemy[2], enemy[3], enemy[4], enemy[5], enemy[6]))

        for i in range(len(game.currentRoom.allNPCs)): 
            game.currentRoom.allNPCs[0].clear()
        
        game.currentRoom.allNPCs = self.allNPCs
    
    def loadItems(self):
        for item in self.itemList : 
            if game.globalItemList[game.currentRoom.roomID][item[3]-1] : 
                self.allItems.append(Item(item[0], item[1], item[2], item[3], item[4]))
        
        for i in range(len(game.currentRoom.allItems)): 
            game.currentRoom.allItems[0].clear()
        
        game.currentRoom.allItems = self.allItems

    def loadDoors(self): 
        for door in self.doorList : 
            if game.globalDoorList[game.currentRoom.roomID][door[3]-1] : 
                self.allDoors.append(Door(door[0], door[1], door[2], door[3], door[4], door[5]))

        for i in range(len(game.currentRoom.allDoors)): 
            game.currentRoom.allDoors[0].clear()

        game.currentRoom.allDoors = self.allDoors
        for door in self.allDoors:
            game.currentRoom.thingsWithCollision.add(door.drawing)

    def load(self): 
        self.loadWalls()
        self.loadNPCs()
        self.loadItems()
        self.loadDoors()
    
    def loadingZone(self, direction): 
        zone = self.exits[direction][2]
        game.currentRoom.loadNewRoom(zone, direction)
    

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
        self.roomID = 'TutorialRoom1'
        self.exits['TOP'][2] = TutorialRoom2
    
class TutorialRoom2 (Room): 
    def __init__(self): 
        super().__init__()
        game.currentRoom.roomID = 'TutorialRoom2'
        self.exits['BOTTOM'][2] = TutorialRoom1
        self.exits['RIGHT'][2] = TutorialRoom3
        
class TutorialRoom3 (Room): 
    def __init__(self): 
        super().__init__()
        game.currentRoom.roomID = 'TutorialRoom3'
        self.exits['LEFT'][2] = TutorialRoom2
        self.exits['RIGHT'][2] = TutorialRoom4

class TutorialRoom4 (Room): 
    def __init__(self): 
        super().__init__() 
        game.currentRoom.roomID = 'TutorialRoom4'
        self.exits['LEFT'][2] = TutorialRoom3
        self.exits['TOP'][2] = TutorialRoom5
        self.itemList.append([100, 200, 'flashlight', 1, None])

class TutorialRoom5 (Room): 
    def __init__(self): 
        super().__init__()
        game.currentRoom.roomID = 'TutorialRoom5'
        self.exits['BOTTOM'][2] = TutorialRoom4
        self.exits['TOP'][2] = TutorialRoom6
        self.npcList.append([200, 200, 0, 0, 0, 'grey', 1])

class TutorialRoom6 (Room): 
    def __init__(self): 
        super().__init__() 
        game.currentRoom.roomID = 'TutorialRoom6'
        self.exits['BOTTOM'][2] = TutorialRoom5
        self.exits['LEFT'][2] = TutorialRoom7
        self.itemList.append([200, 200, 'dashItem', 1, None])

class TutorialRoom7 (Room): 
    def __init__(self): 
        super().__init__() 
        game.currentRoom.roomID = 'TutorialRoom7'
        self.exits['RIGHT'][2] = TutorialRoom6
        self.exits['LEFT'][2] = TutorialRoom8
        self.npcList.append([200, 100, 0, 0, 0, 'grey', 1])
        self.npcList.append([200, 300, 0, 0, 0, 'grey', 2])

class TutorialRoom8 (Room): 
    def __init__(self): 
        super().__init__() 
        game.currentRoom.roomID = 'TutorialRoom8'
        self.exits['RIGHT'][2] = TutorialRoom7

###########################
###### CMU FUNCTIONS ######
###########################

def onKeyHold(keys):     
    if 'PLAYING' in game.mode and game.currentRoom != None : 
        player.handleOnKeys(keys)
def onKeyPress(key): 
    if 'PLAYING' in game.mode and game.currentRoom != None : 
        player.handleKeyPress(key)
        if key == Keybinds.pause: 
            game.pause()
    elif game.mode == 'PAUSED' and key == Keybinds.pause: 
        game.unpause()
    
### debug ###
    if game.mode != 'TITLE SCREEN': 
        if key == 'left': 
            game.currentRoom.room.loadingZone('LEFT')
        if key == 'right':
            game.currentRoom.room.loadingZone('RIGHT')
        if key == 'up':
            game.currentRoom.room.loadingZone('TOP')
        if key == 'down':
            game.currentRoom.room.loadingZone('BOTTOM')
        if key == 'p': 
            print(player.obtainedKeys, player.obtainedSpecialKeys)

def onMouseMove(x, y): 
    game.handleMouseMove(x, y)
def onMouseDrag(x, y): 
    game.handleMouseMove(x, y)
def onMousePress(x, y): 
    if game.mode == 'PLAYING' and game.currentRoom != None :
        player.handleMousePress(x, y)
    if game.mode == 'TITLE SCREEN': 
        game.handleMousePress()
def onStep(): 
    if 'PLAYING' in game.mode and game.currentRoom != None : 
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

def roundedRect(x, y, width, height, colour, outlineColour, outlineWidth):
    RRect = Group()
    if outlineColour != None:
        g.outline = Group()
        width -= 14
        height -= 14
        r1 = Rect(x, y, width+20, height, fill=outlineColour, align='center')
        r2 = Rect(x, y, width, height+20, fill=outlineColour, align='center')
        RRect.outline.add(
        Circle(r2.left, r1.top, 10, fill=outlineColour),
        Circle(r2.right, r1.top, 10, fill=outlineColour),
        Circle(r2.left, r1.bottom, 10, fill=outlineColour),
        Circle(r2.right, r1.bottom, 10, fill=outlineColour),
        r1, r2
        )
        RRect.add(RRect.outline)
        width += 13
        height += 13

    width -= 15
    height -= 15
    r1 = Rect(x, y, width+20, height, fill=colour, align='center')
    r2 = Rect(x, y, width, height+20, fill=colour, align='center')
    RRect.add(
    Circle(r2.left, r1.top, 10, fill=colour),
    Circle(r2.right, r1.top, 10, fill=colour),
    Circle(r2.left, r1.bottom, 10, fill=colour),
    Circle(r2.right, r1.bottom, 10, fill=colour),
    r1, r2
    )
    return RRect

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