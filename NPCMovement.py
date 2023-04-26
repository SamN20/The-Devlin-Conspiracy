from cmu_graphics import * 
import math

class NPC(object):
    
    def __init__(self, cx, cy, rotationAngle, xpLevel, sightDistance, colour):
        self.dx = 0
        self.dy = 0
        self.dr = 1.5
        self.speed = 0.5 # Could change based on xpLevel
        self.followPlayer = True

        self.draw(cx, cy, rotationAngle, sightDistance, colour)
        
    def handleOnStep(self, player, allNPCs):
        self.attemptMove(player, allNPCs)

    def sightLine(self, player):
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
            dx = player.body.centerX - self.drawing.centerX
            dy = player.body.centerY - self.drawing.centerY
            length = math.sqrt(dx**2 + dy**2)
            if length != 0:
                dx /= length
                dy /= length
            self.dx = dx
            self.dy = dy
            # self.move()
            
        # Update the rotation angle based on the rotation direction
        self.sight.rotateAngle = (self.sight.rotateAngle + direction * self.dr) % 360

    def attemptMove(self, player, allNPCs):
        if self.followPlayer:
            self.sightLine(player)
            
            # Predict the next position of the NPC
            nextX = self.drawing.centerX + self.dx * self.speed
            nextY = self.drawing.centerY + self.dy * self.speed
            
            # Check for collisions with other NPCs
            # for npc in allNPCs:
            #     if npc != self:
            #         if npc.hitbox.hits(nextX, nextY):
            #             # There is a collision, do not move
            #             return
                
            # No collision, update velocity and move towards player
            dx = player.body.centerX - self.drawing.centerX
            dy = player.body.centerY - self.drawing.centerY
            length = math.sqrt(dx**2 + dy**2)
            if length != 0:
                self.dx = dx / length * self.speed
                self.dy = dy / length * self.speed
            else:
                self.dx = 0
                self.dy = 0
            
            # Move the NPC
            self.move()
            self.move_away_from_npcs(allNPCs, player)

    def move_away_from_npcs(self, allNPCs, player):
        for NPC in allNPCs:
            if NPC != self and self.hitbox.hitsShape(NPC.hitbox):
                # Calculate the overlap between the two rectangles
                dx = min(self.hitbox.right, NPC.hitbox.right) - max(self.hitbox.left, NPC.hitbox.left)
                dy = min(self.hitbox.bottom, NPC.hitbox.bottom) - max(self.hitbox.top, NPC.hitbox.top)
                if dx > 0 and dy > 0:
                    # There is an overlap, calculate the amount of overlap
                    overlapX = min(abs(dx), self.hitbox.width + NPC.hitbox.width - abs(dx))
                    overlapY = min(abs(dy), self.hitbox.height + NPC.hitbox.height - abs(dy))
                    overlap = min(overlapX, overlapY)
                    if overlap > 0:
                        # Calculate direction between NPCs
                        dx = self.drawing.centerX - NPC.drawing.centerX
                        dy = self.drawing.centerY - NPC.drawing.centerY
                        length = math.sqrt(dx**2 + dy**2)
                        if length != 0:
                            dx /= length
                            dy /= length
                                
                            # Move NPCs away from each other
                            self.drawing.centerX += dx * overlap / 2
                            self.drawing.centerY += dy * overlap / 2
                            NPC.drawing.centerX -= dx * overlap / 2
                            NPC.drawing.centerY -= dy * overlap / 2
                            
                            # Move player away from NPC if colliding
                            if self.hitbox.hitsShape(player.hitbox):
                                self.drawing.centerX -= dx * overlap / 2
                                self.drawing.centerY -= dy * overlap / 2

    def move(self):
        self.drawing.centerX += self.dx * self.speed
        self.drawing.centerY += self.dy * self.speed

    def draw(self, cx, cy, rotationAngle, sightDistance, colour):
        self.sight = Arc(cx, cy, sightDistance*10 + 50, sightDistance*10 + 50, -45, 90, fill = 'lightGrey', opacity = 50)
        self.body = Circle(cx, cy, 7, fill = colour, border = 'black')
        self.hitbox = Rect(cx, cy, 15, 15, fill = 'green', opacity = 25, align = 'center')
        self.drawing = Group(self.body, self.sight, self.hitbox)

# NPC(200, 300, 0, 5, 5, 'red')

# cmu_graphics.run()+


