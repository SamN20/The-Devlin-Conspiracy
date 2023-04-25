from cmu_graphics import * 

class NPC(object):
    
    def __init__(self, cx, cy, rotationAngle, xpLevel, sightDistance, colour):
        self.draw(cx, cy, rotationAngle, sightDistance, colour)
        followPlayer = False

    def attemptMove():
        pass
    
    def move():
        pass
    
    def draw(self, cx, cy, rotationAngle, sightDistance, colour):
        self.sight = Arc(cx, cy, sightDistance*10 + 50, sightDistance*10 + 50, -45, 90, fill = 'lightGrey', opacity = 50)
        self.body = Circle(cx, cy, 7, fill = colour, border = 'black')
        self.hitbox = Rect(cx, cy, 15, 15, fill = 'green', opacity = 25, align = 'center')
        self.drawing = Group(self.body, self.sight, self.hitbox)
        self.dx = 0.75
        self.dy = 0.75

enemy = NPC(200, 200, 0, 5, 5, 'red')

cmu_graphics.run()