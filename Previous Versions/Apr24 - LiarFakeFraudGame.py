from cmu_graphics import * 

class GameState(object): 
    def __init__(self):
        self.mode = 'TITLE SCREEN'
        self.stage = None

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
        } 

cmu_graphics.run()