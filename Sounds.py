from cmu_graphics import *

# Soundtrack 
Titlescreen = Sound('Sound_files\SoundTrack\David Baron-Burning Sun-Master--137.00bpm-Fm.wav')
breakStealth = Sound('Sound_files\SoundTrack\TheDGTL-Hustle Like Dat-Master--88.00bpm-Ebm.wav')
Tutorial = Sound('Sound_files\SoundTrack\ALIBI_Music-Catatumbo_Lightning-Master--130.00bpm-F.wav')
Sand = Sound('Sound_files\SoundTrack\Dune-middle-east-electronic-by-infraction-amp-alexi-action-112364.wav')
Sand.set_volume(0.3)
FireLevel = Sound('Sound_files\SoundTrack\Raz Mesinai-Variations Of Incitement-Master--121.00bpm-Gm.wav')

# Music Playing Variables
Titlescreen.isPlaying = False
Tutorial.isPlaying = False
FireLevel.isPlaying = False
Sand.isPlaying = False

# Sound Effects
saveGame = Sound('Sound_files\SoundEffects\saveRoomSound.wav')
saveGame.set_volume(0.5)
pauseMenu = Sound('Sound_files\SoundEffects\PauseMenu.wav')
pauseMenu.set_volume(0.2)
dash = Sound('Sound_files\SoundEffects\Dash.wav')
dash.set_volume(0.3)
