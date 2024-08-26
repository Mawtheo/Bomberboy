import pygame
import random
from pygame.locals import *

#-----Global-Variables------#
backgroundImage = None
animation = []
frame = 0
width_bloc = 72
height_bloc = 72
blocs = None
players = []

#-----Loaded Sprites-----#
blocpng = None
caisse = None
bomb = None
explosionpng = None
chemin = None
backgroundcolor = []

#-----Loaded Musics-----#
connection = None
ingame = None
sound_bomb = None

#-----Classes-----#
class Animation():
    def __init__(self, files, timeBySprite, stopOnEnd):
        self.sprites = [pygame.image.load(file) for file in files]
        self.time = float(timeBySprite * 0.06)
        self.stopOnEnd = stopOnEnd
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.timer = 0
        self.finished = False
        self.sprite_index = 0

    def place(self, x, y):
        self.x = x
        self.y = y

    def set_size(self, width, height):
        self.width = width
        self.height = height

    def play(self, screen):
        self.timer += 1
        if self.timer >= self.time:
            self.timer = 0
            if self.sprite_index == len(self.sprites) - 1:
                if not self.stopOnEnd:
                    self.sprite_index = 0
                else:
                    self.finished = True
            else:
                self.sprite_index += 1
        screen.blit(pygame.transform.scale(self.sprites[self.sprite_index], (self.width, self.height)), (self.x, self.y))

    def isFinished(self):
        return self.finished

    def reset(self):
        self.timer = 0
        self.sprite_index = 0

class Player():
    face = 0
    back = 1
    right = 2
    left = 3
    idle = 4

    def __init__(self, id):
        global bombs
        self.placeAtStart(id)
        folder = "data/players_animations/" + str(id)
        self.Animation = [
            Animation([folder + "/face/walk_1.png", folder + "/face/walk_2.png"], 300, False),
            Animation([folder + "/back/walk_1.png", folder + "/back/walk_2.png"], 300, False),
            Animation([folder + "/right/walk_1.png", folder + "/right/walk_2.png"], 300, False),
            Animation([folder + "/left/walk_1.png", folder + "/left/walk_2.png"], 300, False)
        ]
        self.height = 72
        self.width = 54
        for animation in self.Animation:
            animation.set_size(self.width, self.height)
        self.idles = [pygame.image.load(folder + "/face/idle.png"), pygame.image.load(folder + "/back/idle.png"), pygame.image.load(folder + "/right/idle.png"), pygame.image.load(folder + "/left/idle.png")]
        self.deathAnimation = Animation([folder + "/death/0.png", folder + "/death/1.png", folder + "/death/2.png", folder + "/death/3.png", folder + "/death/4.png", folder + "/death/5.png", folder + "/death/6.png"], 200, True)
        self.deathAnimation.set_size(79, 72)
        self.lastKnownDirection = self.face
        self.lastRegisteredDirection = self.idle
        bombs.playerbombs.append(3)
        self.dead = False

    def placeAtStart(self, id):
        if id == 0:
            self.x = 492
            self.y = 936
        elif id == 1:
            self.x = 1370
            self.y = 72
        elif id == 2:
            self.x = 492
            self.y = 72
        elif id == 3:
            self.x = 1370
            self.y = 936

    def move(self, screen):
        if self.dead:
            return
        direction = self.lastRegisteredDirection
        if direction == self.idle:
            screen.blit(pygame.transform.scale(self.idles[self.lastKnownDirection], (self.width, self.height)), (self.x, self.y))
            return
        else:
            if direction == self.face:
                if self.y < 1005:
                    if not collision(self.x, self.y + 4 + 36, self.width, self.height / 2):
                        self.y += 4
                self.Animation[0].place(self.x, self.y)
                self.Animation[0].play(screen)
            elif direction == self.back:
                if self.y >= 2:
                    if not collision(self.x, self.y - 4 + 36, self.width, self.height / 2):
                        self.y -= 4
                self.Animation[1].place(self.x, self.y)
                self.Animation[1].play(screen)
            elif direction == self.right:
                if self.x < 1450:
                    if not collision(self.x + 4, self.y + 36, self.width, self.height / 2):
                        self.x += 4
                self.Animation[2].place(self.x, self.y)
                self.Animation[2].play(screen)
            elif direction == self.left:
                if self.x >= 423:
                    if not collision(self.x - 4, self.y + 36, self.width, self.height / 2):
                        self.x -= 4
                self.Animation[3].place(self.x, self.y)
                self.Animation[3].play(screen)
            self.lastKnownDirection = direction

    def death(self, screen):
        self.deathAnimation.place(self.x, self.y)
        self.deathAnimation.play(screen)
        self.dead = True

# Gestion des bombes
class Bombes():
    def __init__(self):
        self.bombs = []
        self.playerbombs = []
        self.explosionarray = []

    def remove_bomb(self, player):
        self.playerbombs[int(player)] -= 1

    def add_bomb(self, player):
        self.playerbombs[int(player)] += 1

    def index_bomb(self, blocs, col, lig):
        for bloc in blocs:
            if bloc[3] == col and bloc[4] == lig:
                return bloc

    def check_timer(self, blocs, screen):
        if len(self.bombs) == 0:
            pass
        else:
            for bomb in self.bombs:
                if bomb[1] % 180 == 0:
                    self.explosion(blocs, bomb[0], screen)
                    self.bombs.remove(bomb)
                    self.add_bomb(bomb[2])
                else:
                    bomb[1] += 1

    def placer_bombe(self, grille_pos, blocs, playerid):
        if blocs[blocs.index(grille_pos)][2] == 0:
            blocs[blocs.index(grille_pos)][2] = 3
            self.bombs.append([blocs.index(grille_pos), 1, playerid])
            self.remove_bomb(playerid)

    def search_bloc(self, col, lig):
        if Bombes.index_bomb(self, blocs, col, lig)[2] == 0:
            Bombes.index_bomb(self, blocs, col, lig)[2] = 4
            self.explosionarray.append([Bombes.index_bomb(self, blocs, col, lig), 1])
        elif Bombes.index_bomb(self, blocs, col, lig)[2] == 2:
            Bombes.index_bomb(self, blocs, col, lig)[2] = 4
            self.explosionarray.append([Bombes.index_bomb(self, blocs, col, lig), 1])
        elif Bombes.index_bomb(self, blocs, col, lig)[2] == 4:
            check = []
            for emplacement in self.explosionarray:
                check.append(emplacement[0])
            self.explosionarray[check.index(Bombes.index_bomb(self, blocs, col, lig))][1] = 1
        elif Bombes.index_bomb(self, blocs, col, lig)[2] == 3:
            for position in self.bombs:
                if position[0] == blocs.index(Bombes.index_bomb(self, blocs, col, lig)):
                    position[1] = 180

    def explosion(self, blocs, indice, screen):
        global sound_bomb, players
        col = blocs[indice][3]
        lig = blocs[indice][4]
        blocs[indice][2] = 4
        self.explosionarray.append([blocs[indice], 1])
        sound_bomb.play()
        if col == 1:
            Bombes.search_bloc(self, col + 1, lig)
        elif col == 15:
            Bombes.search_bloc(self, col - 1, lig)
        else:
            Bombes.search_bloc(self, col - 1, lig)
            Bombes.search_bloc(self, col + 1, lig)
        if lig == 1:
            Bombes.search_bloc(self, col, lig + 1)
        elif lig == 15:
            Bombes.search_bloc(self, col, lig - 1)
        else:
            Bombes.search_bloc(self, col, lig - 1)
            Bombes.search_bloc(self, col, lig + 1)
        for deadBox in self.explosionarray:
            for player in players:
                grid_pos = position(player.x + 24, player.y + 50, player.width, player.height / 2)
                if deadBox[0][0] == grid_pos[0] and deadBox[0][1] == grid_pos[1]:
                    player.death(screen)

    def check_explosion(self, blocs):
        if len(self.explosionarray) == 0:
            pass
        else:
            for emplacement in self.explosionarray:
                if emplacement[1] % 60 == 0:
                    self.explosionarray.remove(emplacement)
                    emplacement[0][2] = 0
                else:
                    emplacement[1] += 1

def setup():
    global backgroundImage, backgroundcolor
    global connection, ingame, sound_bomb

    pygame.init()
    pygame.joystick.init()
    screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
    pygame.display.set_caption("Bomberman")

    global blocpng, caisse, bomb, explosionpng, chemin, players
    blocpng = pygame.image.load("data/sprites_maps/bloc.png")
    caisse = pygame.image.load("data/sprites_maps/caisse.png")
    bomb = pygame.image.load("data/sprites_maps/bomb.png")
    chemin = pygame.image.load("data/sprites_maps/chemin.png")
    explosionpng = pygame.image.load("data/sprites_maps/explosion.png")
    backgroundImage = pygame.image.load("data/sprites_maps/player_connection_background.png")

    backgroundleft1 = pygame.image.load("data/sprites_maps/backgroundleft1.png")
    backgroundright1 = pygame.image.load("data/sprites_maps/backgroundright1.png")
    backgroundleft2 = pygame.image.load("data/sprites_maps/backgroundleft2.png")
    backgroundright2 = pygame.image.load("data/sprites_maps/backgroundright2.png")
    backgroundcolor.append(backgroundleft1)
    backgroundcolor.append(backgroundright1)
    backgroundcolor.append(backgroundleft2)
    backgroundcolor.append(backgroundright2)

    pygame.mixer.init()
    connection = pygame.mixer.Sound("data/musics/mainmenu.mp3")
    ingame = pygame.mixer.Sound("data/musics/ingame.mp3")
    sound_bomb = pygame.mixer.Sound("data/sounds/explosion.wav")

    connection.play(loops=-1)

    return screen

def map():
    blocs = []
    for y in range(0, 1080, 1008):
        for x in range(420, 1500, 72):
            blocs.append([x, y, 1])
    for y in range(72, 1008, 72):
        for x in range(420, 1500, 1008):
            blocs.append([x, y, 1])
    for y in range(288, 792, 144):
        for x in range(492, 1428, 144):
            if random.randint(0, 4) != 0:
                blocs.append([x, y, 2])
    for y in range(360, 720, 144):
        for x in range(492, 1428, 72):
            if random.randint(0, 4) != 0:
                blocs.append([x, y, 2])
    blocs.append([636, 72, 2])
    blocs.append([1212, 72, 2])
    for y in range(72, 144, 72):
        for x in range(708, 1212, 72):
            if random.randint(0, 3) != 0:
                blocs.append([x, y, 2])
    for y in range(144, 216, 72):
        for x in range(636, 1284, 144):
            if random.randint(0, 4) != 0:
                blocs.append([x, y, 2])
    blocs.append([492, 216, 2])
    blocs.append([1356, 216, 2])
    for y in range(216, 288, 72):
        for x in range(564, 1356, 72):
            if random.randint(0, 4) != 0:
                blocs.append([x, y, 2])
    blocs.append([492, 792, 2])
    blocs.append([1356, 792, 2])
    for y in range(792, 864, 72):
        for x in range(564, 1356, 72):
            if random.randint(0, 4) != 0:
                blocs.append([x, y, 2])
    for y in range(864, 936, 72):
        for x in range(636, 1284, 144):
            if random.randint(0, 4) != 0:
                blocs.append([x, y, 2])
    blocs.append([636, 936, 2])
    blocs.append([1212, 936, 2])
    for y in range(936, 1008, 72):
        for x in range(708, 1212, 72):
            if random.randint(0, 4) != 0:
                blocs.append([x, y, 2])
    for y in range(144, 936, 144):
        for x in range(564, 1356, 144):
            blocs.append([x, y, 1])
    chemin = []
    for y in range(72, 1008, 72):
        for x in range(492, 1428, 72):
            chemin.append([x, y, 0])
    for bloc1 in blocs:
        for bloc2 in chemin:
            if bloc1[0:2] == bloc2[0:2]:
                chemin.remove(bloc2)
    for bloc in chemin:
        blocs.append(bloc)
    blocs.sort()
    x = 1
    y = 1
    for bloc in blocs:
        bloc.append(y)
        bloc.append(x)
        if x < 15:
            x += 1
        else:
            x = 1
            y += 1
    return blocs

def draw_blocs(blocs, screen):
    global blocpng, caisse, bomb, explosionpng, chemin
    for bloc in blocs:
        if bloc[2] == 4:
            screen.blit(explosionpng, (bloc[0], bloc[1]))
        if bloc[2] == 3:
            screen.blit(bomb, (bloc[0], bloc[1]))
        if bloc[2] == 2:
            screen.blit(caisse, (bloc[0], bloc[1]))
        elif bloc[2] == 1:
            screen.blit(blocpng, (bloc[0], bloc[1]))
        elif bloc[2] == 0:
            screen.blit(chemin, (bloc[0], bloc[1]))

def collision(x, y, w, h):
    for bloc in blocs:
        if bloc[2] == 1 or bloc[2] == 2:
            if x + w > bloc[0] and x < bloc[0] + width_bloc and y + h > bloc[1] and y < bloc[1] + height_bloc:
                return True
    return False

def position(x, y, w, h):
    for bloc in blocs:
        if x + w > bloc[0] and x < bloc[0] + width_bloc and y + h > bloc[1] and y < bloc[1] + height_bloc:
            return bloc

def newRound():
    global players, blocs
    for i, player in enumerate(players):
        player.dead = False
        player.placeAtStart(i)
        player.deathAnimation.reset()
    blocs = map()

class Stages():
    def __init__(self):
        self.map = 0
        self.frame = 0

stage = Stages()
bombs = Bombes()

def main():
    global backgroundImage, backgroundcolor
    global stage, animation
    global width_bloc, height_bloc, blocs, bombs, frame, players
    global blocpng, caisse, bomb, explosionpng
    global connection, ingame

    screen = setup()
    clock = pygame.time.Clock()

    while stage.map == 0:
        screen.blit(backgroundImage, (0, 0))
        pygame.display.flip()

        # Calibrage manette(s)
        joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

        # Sortir de la boucle de calibrage 
        for event in pygame.event.get():
            if event.type == JOYBUTTONDOWN:
                stage.map = 1
                blocs = map()
                # Ajouts des joueurs en fonctions des mannettes (max 4)
                for i in range(0, len(joysticks)):
                    if i < 4:
                        players.append(Player(i))


    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            elif event.type == JOYBUTTONDOWN:
                player_id = event.joy
                if 0 <= player_id < len(players):
                    if event.button == 0:  # A button
                        grid_pos = position(players[player_id].x + 24, players[player_id].y + 50, players[player_id].width, players[player_id].height / 2)
                        if bombs.playerbombs[player_id] > 0 and not players[player_id].dead:
                            bombs.placer_bombe(grid_pos, blocs, player_id)
            elif event.type == JOYAXISMOTION:
                player_id = event.joy
                if 0 <= player_id < len(players):
                    if event.axis == 0:  # Gauche/Droite
                        print(event.value)
                        if event.value < -0.3:
                            players[player_id].lastRegisteredDirection = Player.left
                        elif event.value > 0.3:
                            players[player_id].lastRegisteredDirection = Player.right
                        else:
                            players[player_id].lastRegisteredDirection = Player.idle
                    elif event.axis == 1:  # Haut/Bas
                        if event.value < -0.3:
                            players[player_id].lastRegisteredDirection = Player.back
                        elif event.value > 0.3:
                            players[player_id].lastRegisteredDirection = Player.face
                        else:
                            players[player_id].lastRegisteredDirection = Player.idle

        if stage.map == 1:
            bombs.check_timer(blocs, screen)
            if stage.frame < 60:
                screen.blit(backgroundcolor[0], (0, 0))
                screen.blit(backgroundcolor[1], (1500, 0))
            elif stage.frame >= 60 and stage.frame <= 120:
                screen.blit(backgroundcolor[2], (0, 0))
                screen.blit(backgroundcolor[3], (1500, 0))
            if stage.frame == 120:
                stage.frame = 0
            stage.frame += 1
            draw_blocs(blocs, screen)
            bombs.check_explosion(blocs)
            deadPlayers = 0
            isAllPlayerDeathFinished = True
            for player in players:
                if not player.dead:
                    player.move(screen)
                else:
                    deadPlayers += 1
                    player.death(screen)
                    if not player.deathAnimation.isFinished():
                        isAllPlayerDeathFinished = False
            if deadPlayers >= len(players) - 1 and isAllPlayerDeathFinished:
                if frame == 180:
                    newRound()
                    frame = 0
                else:
                    frame += 1
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()