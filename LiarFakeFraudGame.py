from cmu_graphics import * 
import Keybinds
import Sounds

app.stepsPerSecond = 60
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
        
        self.globalItemList = { # room ID number : [item1, item2, item3, ...]
            'TutorialRoom2' : [True, True],
            'TutorialRoom4' : [True], 
            'TutorialRoom6' : [True],
            'TutorialRoom6A' : [True], 
            'TutorialRoom6B' : [True]
        }

        self.globalNPCList = { # room ID number : [npc1, npc2, npc3, ...]
            'TutorialRoom5' : [True, True], 
            'TutorialRoom6B' : [True, True], 
            'TutorialRoom7' : [True, True]
            }
        self.globalDoorList = { # room ID number : [door1, door2, door3, ...]
            'TutorialRoom6' : [True],
            'TutorialRoom6A' : [True]
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
        Sounds.Titlescreen.fadeout(3000)
        self.animating = True

    def animate(self): 
        self.startAnimationTimer += 1
        mValue = mapValue(1, 0, 240, 0, 100)
        if self.startAnimationTimer <= 240 : 
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
        Sounds.pauseMenu.play()
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

        self.drawing = Group()
        self.darkSpots = Group()

    def handleOnStep(self): 
        self.loadingZoneLogic()

    def loadNewRoom(self, newRoom, entrance): # (class of the room to load, which direction its getting loaded from)
        if newRoom != None:
            self.walls.clear()
            self.drawing.clear()
            self.darkSpots.clear()
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
        self.swingMod = 3
        self.dashMod = 0 

        self.dx = 0
        self.dy = 0
        self.speed = 0.75 + 0.25*self.moveMod
        self.canMove = True
    
        self.maxHealth = 4 + level*4
        self.health = self.maxHealth

        self.savePointRoom = None

        self.draw(cx, cy, level)

        self.actions = [None]
        self.currentActionIndex = 0
        self.currentAction = self.actions[self.currentActionIndex]
        self.showSelectedAction = False 
        self.currentActionIcon = None
        
        self.hasDash = False
        self.canDash = True
        self.dashDistance = 75 + 25*self.dashMod
        self.dashSpeed = 2.5 + 0.5*self.dashMod
        self.isDashing = False
        self.dashDelay = 120 - 30*self.dashMod
        self.dashCooldown = 0
        self.dashRange = Group()
        
        self.hasSwing = False
        self.canSwing = True 
        self.attacking = False
        self.swingDelay = 120 - 30*self.swingMod
        self.swingCooldown = 0
        self.swing
        
        self.hasShoot = False
        self.canShoot = True
        self.bullets = [ ]
        self.shootDelay = 90 - 30*self.shootMod
        self.shootCooldown = 0    

        self.obtainedKeys = 0
        self.obtainedSpecialKeys = [ ]

    def draw(self, cx, cy, level): 
        self.sight = Arc(cx, cy, 100, 100, -45, 90, fill = 'white', opacity = 0)
        self.body = Circle(cx, cy, 7, fill = 'white', border = 'black')
        self.hitbox = Rect(cx, cy, 15, 15, fill = 'green', opacity = 0, align = 'center')
        self.swing = Arc(cx, cy, 30+30*level, 30+30*level, -55, 10, fill = 'saddleBrown', opacity = 0)
        self.drawing = Group(self.sight, self.body, self.swing, self.hitbox)
        self.drawing.visible = False 
        self.healthBar = HealthBar(self)
        self.deathSubText = Label('Do better this time', 200, 150, size = 20, fill = 'red')
        self.deathText = Group(Rect(0, 0, 400, 400, fill='darkGray', opacity = 80) , Label('You Died Bruh', 200, 100, size = 30, fill = 'red'), self.deathSubText, Label('Click anywhere to continue', 200, 300, size = 15, fill = 'red'))
        self.deathText.visible = False
        
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
            self.swing.rotateAngle += (1.5 + 0.75*self.swingMod)
            
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
        # self.healthBar.updateHealthBar(self)
        # if self.health <= 0:
        #     self.die()
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
            if door.direction == 'h' : 
                if distance(self.hitbox.centerX, self.hitbox.centerY, self.hitbox.centerX, door.drawing.centerY) < 30: # checks to see if the player is close enough to the door
                    door.unlock()
            if door.direction == 'v' : 
                if distance(self.hitbox.centerX, self.hitbox.centerY, door.drawing.centerX, self.hitbox.centerY) < 30:  # checks to see if the player is close enough to the door
                    door.unlock()
        # code is more clunky, unlocking doors in game is less clunky

    def die(self):
        print('player is dead')
        game.mode = 'DEAD'
        if self.savePointRoom is not None:
            game.currentRoom.loadNewRoom(self.savePointRoom, 'SAVE POINT')
            self.deathSubText.value = 'Loading from last save point...'
        else:
            game.currentRoom.loadNewRoom(TutorialRoom1, 'TUTORIAL SPAWN')
            self.deathSubText.value = 'Do better this time!'
        self.deathText.visible = True
        self.health = self.maxHealth
        self.healthBar.drawing.visible = False

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
        if game.mode == 'DEAD':
            self.deathText.visible = False
            game.mode = 'PLAYING'
        elif game.currentRoom.roomID != 0 : 
            if self.currentAction == 'swing': 
                self.swingAttack()
                
            if self.currentAction == 'shoot' : 
                self.shooting = False
                self.shoot()

            if self.currentAction == 'dash' and self.isDashing == False and self.canDash == True and self.hasDash == True:
                self.dashToX, self.dashToY = self.getDashDestination()
                self.isDashing = True
                Sounds.dash.play()
                self.dashRange = Group(Line(self.hitbox.centerX, self.hitbox.centerY, self.dashToX, self.dashToY, fill = 'blue', opacity = 25))

################################
###### START OF NPC CLASS ######
################################
                
class NPC(object):
    
    def __init__(self, cx, cy, rotationAngle, level, sightDistance, colour, index):
       
        self.dx = 0
        self.dy = 0
        self.dr = 1.5
        self.speed = 0.75 # Could change based on level
        self.followPlayer = True
        
        self.index = index

        self.maxHealth = 4 + level*4
        self.health = self.maxHealth

        self.draw(cx, cy, rotationAngle, sightDistance, colour, level)

        self.moveMod = 0 
        self.shootMod = 0 
        self.swingMod = 0 + level
        self.dashMod = 0 

        self.justTookDamageLastCycle = False

        self.hasSwing = True
        self.canSwing = True 
        self.attacking = False
        self.swingDelay = 120 - 15*self.swingMod
        self.swingCooldown = 0
        game.currentRoom.thingsThatDamagePlayer.append([self.swing, 4, None])
        
    def draw(self, cx, cy, rotationAngle, sightDistance, colour, level):
        self.sight = Arc(cx, cy, sightDistance*10 + 50, sightDistance*10 + 50, -45, 90, fill = 'lightGrey', opacity = 50, rotateAngle = rotationAngle)
        self.body = Circle(cx, cy, 7, fill = colour, border = 'black')
        self.hitbox = Rect(cx, cy, 15, 15, fill = 'green', opacity = 0, align = 'center')
        self.swing = Arc(cx, cy, 60+10*level, 60+10*level, -55, 10, fill = 'saddleBrown')
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
        if any([item[0].hitsShape(self.hitbox) for item in game.currentRoom.thingsThatDamageNPCs if item[0].opacity != 0]):
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
            self.swing.rotateAngle += (2 + 0.5*self.swingMod)
            
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
    def draw(self, cx, cy): # Draws the item based on its type
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
        if self.itemType == 'healthItem':
            self.model = Group(Rect(cx-3, cy-7, 6, 14, fill='red'), Rect(cx-7, cy-3, 14, 6, fill='red'))
        if self.itemType == 'healItem':
            self.model = Group(Rect(cx, cy, 14, 14, fill='green'), Line(cx+2, cy+7, cx+12, cy+7, fill='white', lineWidth=4),
                       Line(cx+7, cy+2, cx+7, cy+12, fill='white', lineWidth=4))
        
        self.drawing = Group(self.hitbox, self.model)

    def hasBeenCollected(self): # Checks if the player has collected the item
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
        if self.itemType == 'healthItem':
            player.maxHealth += 4
        if self.itemType == 'healItem':
            player.health += 4
            if player.health > player.maxHealth:
                player.health = player.maxHealth   
    
    def clear(self): # Clears the item from the room
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
        self.direction = direction
        self.draw(cx, cy)
    def draw(self, cx, cy): 
        door = buildWall(0, 0, 150, self.direction)
        door.height -= 2
        if self.type == 'NORMAL':
            door.fill = 'peru'
        if self.type == 'LOCKED': 
            door.fill = 'grey'
        if self.type == 'SPECIAL': 
            door.fill = self.colour
            
        door.centerX, door.centerY = cx, cy
        self.drawing = Group(door)
    def unlock(self): 
        if self.type == 'NORMAL':
            game.globalDoorList[game.currentRoom.roomID][self.index-1] = False
            self.clear()
        if self.type == 'LOCKED': 
            if player.obtainedKeys > 0:
                player.obtainedKeys -= 1
                game.globalDoorList[game.currentRoom.roomID][self.index-1] = False
                self.clear()
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
        
        self.npcList = [ ] # cx, cy, rotationAngle, level, sightDistance, colour, index
        self.itemList = [ ] # cx, cy, type, index, colour
        self.doorList = [ ] # cx, cy, type, index, colour, direction

        self.allNPCs = [ ]
        self.allItems = [ ]
        self.allDoors = [ ]

        self.drawing = Group()
        self.darkSpots = Group()

        self.exitLabels = ['TOP', 'BOTTOM', 'LEFT', 'RIGHT']
        self.exits = { # Direction : spawnX, spawnY, RoomClass (dont set here)
            'TOP' : [200, 395, None], 
            'BOTTOM' : [200, 5, None], 
            'LEFT' : [395, 200, None], 
            'RIGHT' : [5, 200, None], 
            'TUTORIAL SPAWN' : [200, 350, None],
            'SAVE POINT' : [200, 200, None]
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
        for i in range(len(game.currentRoom.allNPCs)): 
            game.currentRoom.allNPCs[0].clear()
        
        game.currentRoom.thingsThatDamagePlayer = []

        for enemy in self.npcList : 
            if game.globalNPCList[game.currentRoom.roomID][enemy[6]-1] : 
                self.allNPCs.append(NPC(enemy[0], enemy[1], enemy[2], enemy[3], enemy[4], enemy[5], enemy[6]))

        game.currentRoom.allNPCs = self.allNPCs
    
    def loadItems(self):
        for item in self.itemList : 
            if game.globalItemList[game.currentRoom.roomID][item[3]-1] : 
                self.allItems.append(Item(item[0], item[1], item[2], item[3], item[4]))
        
        for item in game.currentRoom.allItems:
            item.clear()

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
        game.currentRoom.drawing = self.drawing
        self.loadWalls()
        self.loadNPCs()
        self.loadItems()
        self.loadDoors()
        game.currentRoom.darkSpots = self.darkSpots
    
    def loadingZone(self, direction): 
        zone = self.exits[direction][2]
        game.currentRoom.loadNewRoom(zone, direction)

    def handleOnStep(self):
        self.darkSpots.toFront()
        for spot in self.darkSpots:
            if player.hitbox.hitsShape(spot):
                spot.visible = False

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
        self.itemList.append([200, 100, 'healthItem', 1, None])
        self.itemList.append([200, 300, 'healItem', 2, None])
        label1 = Label("Collect the Max Health Boost By Pressing " + Keybinds.collect, 200, 80, size=15)
        label2 = Label("Collect the Heal Item in the same way", 200, 280, size=15)
        self.drawing = Group(label1, label2)
        
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
        self.drawing = Group(Label("Collect the Flashlight", 200, 120, size=15), 
                             Label("Your Flashlight will follow the mouse pointer", 200, 140, size=13))

class TutorialRoom5 (Room): 
    def __init__(self): 
        super().__init__()
        game.currentRoom.roomID = 'TutorialRoom5'
        self.exits['BOTTOM'][2] = TutorialRoom4
        self.exits['TOP'][2] = TutorialRoom6
        self.npcList.append([200, 200, 0, 0, 0, 'grey', 1])
        self.drawing = Group(Label("This is an enemy", 200, 120, size=15), 
                           Label("Enemies will attack you if you are in their sight", 200, 140, size=13),
                           Label("You will have to avoid him for now.. if only you had a weapon", 200, 160, size=13))

class TutorialRoom6 (Room): 
    def __init__(self): 
        super().__init__() 
        game.currentRoom.roomID = 'TutorialRoom6'
        self.exits['BOTTOM'][2] = TutorialRoom5
        self.exits['LEFT'][2] = TutorialRoom7
        self.exits['RIGHT'][2] = TutorialRoom6A
        self.itemList.append([200, 200, 'dashItem', 1, None])
        self.doorList.append([5, 200, 'SPECIAL', 1, 'red', 'v'])
        self.drawing = Group(Label("Collect the Dash Item", 200, 120, size=15), 
                             Label("You can use it to dash around enemies", 200, 140, size=13),
                             Label("Be aware that there is a cooldown", 200, 160, size=13))

class TutorialRoom6A (Room): 
    def __init__(self):
        super().__init__()
        game.currentRoom.roomID = 'TutorialRoom6A'
        self.exits['LEFT'][2] = TutorialRoom6
        self.exits['RIGHT'][2] = TutorialRoom6B
        self.itemList.append([300, 100, 'keyItem', 1, None])
        self.doorList.append([395, 200, 'LOCKED', 1, None, 'v'])
        self.drawing = Group(Label("Collect the Key Item", 200, 120, size=15), 
                             Label("You can use it to unlock 1 gray locked door", 200, 140, size=13))

class TutorialRoom6B (Room): 
    def __init__(self):
        super().__init__()
        game.currentRoom.roomID = 'TutorialRoom6B'
        self.exits['LEFT'][2] = TutorialRoom6A
        self.itemList.append([300, 200, 'specialKeyItem', 1, 'red'])
        self.npcList.append([200, 100, 270, 0, 0, 'red', 1])
        self.npcList.append([200, 300, 270, 0, 0, 'red', 2])
        self.drawing = Group(Label("Collect the Special Key Item", 200, 120, size=15), 
                             Label("You can use it to unlock 1 locked door of the same colour", 200, 140, size=13))

class TutorialRoom7 (Room): 
    def __init__(self): 
        super().__init__() 
        game.currentRoom.roomID = 'TutorialRoom7'
        self.exits['RIGHT'][2] = TutorialRoom6
        self.exits['LEFT'][2] = TutorialRoom8
        self.npcList.append([200, 100, 0, 0, 0, 'grey', 1])
        self.npcList.append([200, 300, 0, 0, 0, 'grey', 2])
        self.drawing = Group(Label("Try to avoid these guys", 200, 120, size=15))

class TutorialRoom8 (Room): 
    def __init__(self): 
        super().__init__() 
        game.currentRoom.roomID = 'TutorialRoom8'
        self.exits['RIGHT'][2] = TutorialRoom7
        self.exits['TOP'][2] = EndOfTutorialSaveRoom
        self.drawing = Group(Label("End of Tutorial", 200, 70, size=16, bold=True),
                            Label("Congratulations!", 200, 100, size=14, bold=True),
                            Label("You have completed the tutorial of", 200, 150, size=12),
                            Label("The Devlin Conspiracy: The Liar, The Fake, The Fraud.", 200, 175, size=12),
                            Label("You are now ready to uncover the secrets", 200, 225, size=12),
                            Label("and expose the truth behind the conspiracy.", 200, 250, size=12),
                            Label("Use your skills wisely, trust no one, and", 200, 300, size=12),
                            Label("unravel the mystery that awaits you above!", 200, 325, size=12))

class SaveRoom (Room):
    def __init__(self):
        super().__init__()
        self.savingMessage = [
            ["Saving progress... because real life doesn't", "come with a 'rewind' button. Cherish this privilege!"],
            ["Save Station: Unmask the secrets, but don't", "let your progress become another layer of deception!"],
            ["Save Room: A refuge from the tangled web of", "conspiracies. Trust no one, except the save button!"],
            ["Preserve your truth-seeking journey here.", "The lies may run deep, but your progress stays untainted!"],
            ["Saving... Shield your progress from the shadowy whispers", "of deception. Unravel the conspiracy with confidence!"],
            ["Save Point: Leave no stone unturned, no deceit unnoticed.", "Your progress is a beacon of truth amidst the lies!"],
            ["Save Zone: Where the conspiracies take a break and", "have a cup of tea. Just don't spill it on the evidence!"],
            ["Welcome to the Save Lair, where frauds and fakes", "take a timeout to practice their poker faces."],
            ["Saving... because in a world of lies and cheats, we've got", "your back! Your secret's safe with us... probably."],
            ["Save Zone: Where the truth lies...", "conveniently saved for your convenience!"],
            ["Saving progress: Because even conspiracies need a", "coffee break. Time to refold those tinfoil hats!"],
            ["Saving... because even the most elaborate deceptions", "need occasional backup plans. We've got you covered!"],
            ["Save your progress and remember,", "even heroes need bathroom breaks!"]
            ]
        self.draw()
        player.savePointRoom = self.__class__
        if game.mode == 'PLAYING':
            Sounds.saveGame.play()

    def draw(self):
        floor = Image('Images/Save-Room.png', 10, 5, width = 380, height = 380, opacity = 10)
        text = self.savingMessage[randrange(0, len(self.savingMessage))]
        text1 = text[0]
        text2 = text[1]
        self.savePointText = Group(Label(text1, 200, 190, size = 15, fill = 'slateGray', borderWidth = 0.5), Label(text2, 200, 210, size = 15, fill = 'slateGray'))
        self.savePointText.centerX, self.savePointText.centerY = 200, 200
        self.drawing = Group(floor, self.savePointText)
        
class EndOfTutorialSaveRoom (SaveRoom):
    def __init__(self):
        super().__init__()
        game.currentRoom.roomID = 'EOfTSR'
        self.exits['BOTTOM'][2] = TutorialRoom8
        self.exits['LEFT'][2] = SandTempleRoom1
        if 'EOfTSR' not in game.globalDoorList:
            game.globalDoorList['EOfTSR'] = [True, True]
        self.doorList.append([0, 200, 'NORMAL', 1, None, 'v'])
        # self.doorList.append([395, 200, 'NORMAL', 2, None, 'V'])
        Sounds.Tutorial.fadeout(3000)

## Sand Temple World ##
class SandTempleRoom1 (Room):
    def __init__(self):
        super().__init__()
        game.currentRoom.roomID = 'Sand1'
        self.exits['RIGHT'][2] = EndOfTutorialSaveRoom
        self.exits['LEFT'][2] = SandTempleRoom2
        if 'Sand1' not in game.globalDoorList:
            game.globalDoorList['Sand1'] = [True]
        if 'Sand1' not in game.globalNPCList:
            game.globalNPCList['Sand1'] = [True]

        self.draw()

    def draw(self):
        self.npcList.append([30, 50, 90, 1, 0, 'khaki', 1]) # cx, cy, rotationAngle, level, sightDistance, colour, index
        self.sandFloor = Image('Images/Sand.png', -205, 0, opacity = 40)
        self.enemyCover = Rect(10, 10, 185, 105, fill = 'dimGray', opacity = 95)
        self.darkSpots = Group(Rect(10, 115, 185, 400, fill = 'dimGray', opacity = 97),
                               self.enemyCover)
        tempWallList = [[195, 0, 125, 'v'], [195, 275, 125, 'v'], [145, 115, 50, 'h'], [145, 115, 250, 'v'], # cx, cy, length, direction
                        [0, 115, 120, 'h']
                        ]
        for wall in tempWallList:
            self.wallList.append(wall)
        self.doorList.append([200, 200, 'NORMAL', 1, None, 'v'])
        self.drawing = Group(self.sandFloor)

    def handleOnStep(self):
        for enemy in game.currentRoom.allNPCs:
            if self.enemyCover.visible == False:
                enemy.followPlayer = True
            else:
                enemy.followPlayer = False
        super().handleOnStep()

class SandTempleRoom2 (Room):
    def __init__(self):
        super().__init__()
        game.currentRoom.roomID = 'Sand2'
        self.exits['RIGHT'][2] = SandTempleRoom1
        self.exits['LEFT'][2] = SandTempleRoom3
        self.exits['BOTTOM'][2] = SandTempleRoom2A
        if 'Sand2' not in game.globalNPCList:
            game.globalNPCList['Sand2'] = [True]
        if 'Sand2' not in game.globalItemList:
            game.globalItemList['Sand2'] = [True, True]

        self.draw()

    def draw(self):
        sandFloor = Image('Images/Sand.png', 0, 0, opacity = 40)
        tempWallList = [
            [0, 100, 200, 'h'],
            [200, 30, 120, 'v'],
            [150, 150, 170, 'h'],
            [100, 250, 150, 'v'],
            [250, 250, 100, 'h'],
            [350, 125, 150, 'v'],  
            [350, 275, 100, 'h'],
            [450, 0, 150, 'v'],
            [275, 0, 50, 'h']
        ]
        for wall in tempWallList:
            self.wallList.append(wall)
        self.drawing = Group(sandFloor)
        self.itemList.append([30, 70, 'healthItem', 1, None]) # cx, cy, type, index, colour
        self.itemList.append([360, 340, 'healItem', 2, None]) # cx, cy, type, index, colour
        self.npcList.append([330, 340, 0, 2, 0, 'khaki', 1]) # cx, cy, rotationAngle, level, sightDistance, colour, index

        self.topLeftDarkSpot = Rect(10, 10, 190, 90, fill = 'dimGray', opacity = 97)
        self.bottomRightDarkSpot = Group(Rect(110, 260, 240, 150, fill = 'dimGray', opacity = 97), Rect(350, 285, 390-350, 400-285, fill = 'dimGray', opacity = 97))
        self.darkSpots = Group(self.topLeftDarkSpot, self.bottomRightDarkSpot)

    def handleOnStep(self):
        super().handleOnStep()
        for enemy in game.currentRoom.allNPCs:
            if self.bottomRightDarkSpot.visible == False:
                enemy.followPlayer = True
            else:
                enemy.followPlayer = False

class SandTempleRoom2A (Room):
    def __init__(self):
        super().__init__()
        game.currentRoom.roomID = 'Sand2A'
        self.exits['TOP'][2] = SandTempleRoom2
        self.exits['BOTTOM'][2] = SandTempleRoom2B
        if 'Sand2A' not in game.globalNPCList:
            game.globalNPCList['Sand2A'] = [True, True]
        if 'Sand2A' not in game.globalItemList:
            game.globalItemList['Sand2A'] = [True]

        self.draw()
    
    def draw(self):
        sandFloor = Image('Images/Sand.png', 0, 0, opacity = 40)
        tempWallList = [
            [0, 200, 100, 'h'],
            [100, 60, 90, 'v'],
            [200, 300, 110, 'h'],
            [300, 150, 150, 'v'],
            [100, 350, 150, 'h'],
            [400, 100, 150, 'v'],
            [350, 400, 100, 'h'],
            [450, 200, 100, 'v'],
            [500, 0, 100, 'h']
        ]
        for wall in tempWallList:
            self.wallList.append(wall)
        self.drawing = Group(sandFloor)
        self.itemList.append([60, 80, 'healItem', 1, None]) # cx, cy, type, index, colour
        self.npcList.append([60, 100, 0, 2, 0, 'khaki', 1]) # cx, cy, rotationAngle, level, sightDistance, colour, index
        self.npcList.append([350, 350, 0, 2, 0, 'khaki', 2]) # cx, cy, rotationAngle, level, sightDistance, colour, index

    def handleOnStep(self):
        super().handleOnStep()

class SandTempleRoom2B (Room):
    def __init__(self):
        super().__init__()
        game.currentRoom.roomID = 'Sand2B'
        self.exits['TOP'][2] = SandTempleRoom2A
        self.exits['LEFT'][2] = SandTempleRoom2C

        self.draw()
    
    def draw(self):
        sandFloor = Image('Images/Sand.png', 0, 0, opacity = 40)

        self.drawing = Group(sandFloor)

class SandTempleRoom2C (Room):
    def __init__(self):
        super().__init__()
        game.currentRoom.roomID = 'Sand2C'
        self.exits['RIGHT'][2] = SandTempleRoom2B
        self.exits['LEFT'][2] = SandTempleRoom2D
        self.exits['TOP'][2] = SandTempleRoom2Ca
        if 'Sand2C' not in game.globalDoorList:
            game.globalDoorList['Sand2C'] = [True]
        if 'Sand2C' not in game.globalNPCList:
            game.globalNPCList['Sand2C'] = [True, True]

        self.draw()

    def draw(self):
        sandFloor = Image('Images/Sand.png', 0, 0, opacity = 40)
        self.doorList.append([200, 5, 'SPECIAL', 1, 'blue', 'h'])
        self.npcList.append([100, 50, 90, 3, 0, 'blue', 1]) # cx, cy, rotationAngle, level, sightDistance, colour, index
        self.npcList.append([300, 50, 90, 3, 0, 'blue', 2]) # cx, cy, rotationAngle, level, sightDistance, colour, index

        self.drawing = Group(sandFloor)


class SandTempleRoom2Ca (Room):
    def __init__(self):
        super().__init__()
        game.currentRoom.roomID = 'Sand2Ca'
        self.exits['BOTTOM'][2] = SandTempleRoom2C
        if 'Sand2Ca' not in game.globalItemList:
            game.globalItemList['Sand2Ca'] = [True]

        self.draw()
    
    def draw(self):
        sandFloor = Image('Images/Sand.png', 0, 0, opacity = 40)
        self.itemList.append([200, 200, 'specialKeyItem', 1, 'tan']) # cx, cy, type, index, colour
        self.drawing = Group(sandFloor)

class SandTempleRoom2D (Room):
    def __init__(self):
        super().__init__()
        game.currentRoom.roomID = 'Sand2D'
        self.exits['RIGHT'][2] = SandTempleRoom2C
        self.exits['TOP'][2] = SandTempleRoom2E

        self.draw()
    
    def draw(self):
        sandFloor = Image('Images/Sand.png', 0, 0, opacity = 40)

        self.drawing = Group(sandFloor)

class SandTempleRoom2E (Room):
    def __init__(self):
        super().__init__()
        game.currentRoom.roomID = 'Sand2E'
        self.exits['BOTTOM'][2] = SandTempleRoom2D
        self.exits['TOP'][2] = SandTempleRoom4
        if 'Sand2E' not in game.globalItemList:
            game.globalItemList['Sand2E'] = [True]

        self.draw()
    
    def draw(self):
        sandFloor = Image('Images/Sand.png', 0, 0, opacity = 40)
        self.itemList.append([200, 200, 'specialKeyItem', 1, 'blue']) # cx, cy, type, index, colour
        self.drawing = Group(sandFloor)

class SandTempleRoom3 (Room):
    def __init__(self):
        super().__init__()
        game.currentRoom.roomID = 'Sand3'
        self.exits['RIGHT'][2] = SandTempleRoom2
        self.exits['LEFT'][2] = SandTempleRoom4
        if 'Sand3' not in game.globalNPCList:
            game.globalNPCList['Sand3'] = [True]
        if 'Sand3' not in game.globalItemList:
            game.globalItemList['Sand3'] = [True, True, True]
        self.draw()
    
    def draw(self):
        sandFloor = Image('Images/Sand.png', 0, 0, opacity = 40)
        tempWallList = [
            [0, 300, 200, 'h'],
            [200, 90, 120, 'v'],
            [230, 115, 170, 'h'],
            [200, 350, 150, 'v'],
            [300, 275, 100, 'h'],
        ]
        for wall in tempWallList:
            self.wallList.append(wall)
        self.drawing = Group(sandFloor)
        self.itemList.append([90, 100, 'healthItem', 1, None]) # cx, cy, type, index, colour
        self.itemList.append([370, 100, 'healItem', 2, None]) # cx, cy, type, index, colour
        self.itemList.append([50, 350, 'swingItem', 3, None]) # cx, cy, type, index, colour
        self.npcList.append([370, 360, 0, 2, 0, 'khaki', 1]) # cx, cy, rotationAngle, level, sightDistance, colour, index
        self.darkSpots = Group(Rect(10, 310, 190, 80, fill = 'dimGray', opacity = 97))

class SandTempleRoom4 (Room):
    def __init__(self):
        super().__init__()
        game.currentRoom.roomID = 'Sand4'
        self.exits['RIGHT'][2] = SandTempleRoom3
        self.exits['BOTTOM'][2] = SandTempleRoom2E

        self.draw()
    
    def draw(self):
        sandFloor = Image('Images/Sand.png', 0, 0, opacity = 40)

        self.drawing = Group(sandFloor)
    
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
    if (game.mode == 'PLAYING' or game.mode == 'DEAD')  and game.currentRoom != None :
        player.handleMousePress(x, y)
    if game.mode == 'TITLE SCREEN': 
        game.handleMousePress()
def onStep(): 
    if 'PLAYING' in game.mode and game.currentRoom != None : 
        player.handleOnStep() 
        game.currentRoom.handleOnStep() 
        for enemy in game.currentRoom.allNPCs:
            enemy.handleOnStep()
        game.currentRoom.room.handleOnStep()
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
player = Player(200, 300, 1)

cmu_graphics.run()