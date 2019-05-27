#PROYECTO 3
#Esteban Cabrera Arevalo
#17781

import pygame
from math import pi, cos, sin, atan2
from time import sleep

#COLORES
menuIntrucciones = (0, 0, 0)
suelo = (118, 181, 0)
cielo = (153, 217, 234)

#MAPA
mapa = [] #La matriz se declara de forma global para poderla modificar en tiempo de ejecucion.

#SPRITES DE FONDO Y ENEMIGOS
fondo = pygame.image.load('./b128.png') 
fondoPato = pygame.image.load('./pato.png')

#TEXTURAS
textures = {
  "1": fondo,
  "2": fondoPato,
}


#SPRITE DE PISTOLA PARA PERSONAJE
pistola = pygame.image.load('./player.png')

#DIBUJO DE CIELO Y SUELO
def dibujarCieloSuelo():
  pygame.draw.rect(screen, cielo, (0, 0, 1000, 250))
  pygame.draw.rect(screen, suelo, (0, 250, 1000, 500))

#RAYCASTER
class Raycaster(object):
  def __init__(self, screen):
    _, _, self.width, self.height = screen.get_rect()
    self.screen = screen
    self.blocksize = 50
    self.player = {
      "x": self.blocksize + 20,
      "y": self.blocksize + 20,
      "a": pi/3,
      "fov": pi/3
    }
    self.map = []
    self.zbuffer = [-float('inf') for z in range(0, 500)]


  def clear(self):
    for x in range(self.width):
      for y in range(self.height):
        r = int((x/self.width)*255) if x/self.width < 1 else 1
        g = int((y/self.height)*255) if y/self.height < 1 else 1
        b = 0
        color = (r, g, b)
        self.point(x, y, color)

  def point(self, x, y, c = None):
    screen.set_at((x, y), c)

  def draw_rectangle(self, x, y, texture):
    for cx in range(x, x + 50):
      for cy in range(y, y + 50):
        tx = int((cx - x)*128 / 50)
        ty = int((cy - y)*128 / 50)
        c = texture.get_at((tx, ty))
        self.point(cx, cy, c)

  def load_map(self, filename):
    with open(filename) as f:
      for line in f.readlines():
        mapa.append(list(line))
        #mapa = self.map

  def cast_ray(self, a):
    d = 0
    while True:
      x = self.player["x"] + d*cos(a)
      y = self.player["y"] + d*sin(a)

      i = int(x/50)
      j = int(y/50)

      if mapa[j][i] != ' ':
        hitx = x - i*50
        hity = y - j*50

        if 1 < hitx < 49:
          maxhit = hitx
        else:
          maxhit = hity

        tx = int(maxhit * 128 / 50)

        return d, mapa[j][i], tx
     # print(self.map)



      d += 1

  def draw_stake(self, x, h, texture, tx):
    start = int(250 - h/2)
    end = int(250 + h/2)
    for y in range(start, end):
      ty = int(((y - start)*128)/(end - start))
      c = texture.get_at((tx, ty))
      self.point(x, y, c)

  def draw_sprite(self, sprite):
    sprite_a = atan2(sprite["y"] - self.player["y"], sprite["x"] - self.player["x"])   # why atan2? https://stackoverflow.com/a/12011762

    sprite_d = ((self.player["x"] - sprite["x"])**2 + (self.player["y"] - sprite["y"])**2)**0.5
    sprite_size = (500/sprite_d) * 70

    sprite_x = 250 + (sprite_a - self.player["a"])*500/self.player["fov"] + 250 - sprite_size/2
    sprite_y = 250 - sprite_size/2

    sprite_x = int(sprite_x)
    sprite_y = int(sprite_y)
    sprite_size = int(sprite_size)

    for x in range(sprite_x, sprite_x + sprite_size):
      for y in range(sprite_y, sprite_y + sprite_size):
        if 500 < x < 1000 and self.zbuffer[x - 500] >= sprite_d:
          tx = int((x - sprite_x) * 128/sprite_size)
          ty = int((y - sprite_y) * 128/sprite_size)
          c = sprite["texture"].get_at((tx, ty))
          if c != (152, 0, 136, 255):
            self.point(x, y, c)
            self.zbuffer[x - 500] = sprite_d

  def draw_player(self, xi, yi, w = 256, h = 256):
    xi = xi - 500
    for x in range(xi, xi + w):
      for y in range(yi, yi + h):
        tx = int((x - xi) * 32/w)
        ty = int((y - yi) * 32/h)
        c = pistola.get_at((tx, ty))
        if c != (152, 0, 136, 255):
          self.point(x, y, c)

  def render(self):
    
    dibujarCieloSuelo()
    
    for i in range(0, 500):
      self.point(500, i, (0, 0, 0))
      self.point(501, i, (0, 0, 0))
      self.point(499, i, (0, 0, 0))

    for i in range(0, 500):
      a =  self.player["a"] - self.player["fov"]/2 + self.player["fov"]*i/500
      d, c, tx = self.cast_ray(a)
      x = i
      h = (500/(d*cos(a-self.player["a"])) * 70 + 1)
      self.draw_stake(x, h, textures[c], tx)
      self.zbuffer[i] = d

    self.draw_player(1000 - 256 - 128, 500 - 256)


def playMusic():
  pygame.mixer.music.load('soundtrack.mp3')
  pygame.mixer.music.play(-1)

pygame.init()
screen = pygame.display.set_mode((500, 500), pygame.DOUBLEBUF|pygame.HWACCEL|pygame.HWSURFACE)
screen.set_alpha(None)
r = Raycaster(screen)
r.load_map('map.txt')


pato1 = False

playMusic()

cont = 0
while True:

  if cont == 6:
    pistola = pygame.image.load('./player.png')
    cont = 0
  dibujarCieloSuelo()
  screen.fill((113, 113, 113))
  r.render()

  for e in pygame.event.get():
    if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
      exit(0)

    
    if e.type == pygame.KEYDOWN:
      if e.key == pygame.K_a:
        r.player["a"] -= pi/10
      elif e.key == pygame.K_d:
        r.player["a"] += pi/10

      elif e.key == pygame.K_RIGHT:
        r.player["x"] -= 10
      elif e.key == pygame.K_LEFT:
        r.player["x"] += 10
      elif e.key == pygame.K_UP:
        r.player["y"] += 10
      elif e.key == pygame.K_DOWN:
        r.player["y"] -= 10
      elif e.key == pygame.K_s: #SHOOT
        pistola = pygame.image.load('./shot.png')
        #pygame.mixer.music.load('disparo.mp3')
        #pygame.mixer.music.play(0)
        if ((r.player["y"] >= 70) and (r.player["y"] <= 150) and ((r.player["x"] >= 70) and (r.player["x"] <= 150))):
          mapa[0][2] = "1"
        if ((r.player["y"] >= 70) and (r.player["y"] <= 90) and ((r.player["x"] >= 230) and (r.player["x"] <= 300))):
          mapa[2][5] = "1"
        if ((r.player["y"] >= 70) and (r.player["y"] <= 100) and ((r.player["x"] >= 270) and (r.player["x"] <= 340))):
          mapa[0][6] = "1"
        if ((r.player["y"] >= 70) and (r.player["y"] <= 130) and ((r.player["x"] >= 360) and (r.player["x"] <= 410))):
          mapa[1][9] = "1"
        if ((r.player["y"] >= 70) and (r.player["y"] <= 130) and ((r.player["x"] >= 360) and (r.player["x"] <= 410))):
          mapa[1][9] = "1"
        if ((r.player["y"] >= 70) and (r.player["y"] <= 130) and ((r.player["x"] >= 360) and (r.player["x"] <= 410))):
          mapa[5][8] = "1"
        if ((r.player["y"] >= 70) and (r.player["y"] <= 130) and ((r.player["x"] >= 360) and (r.player["x"] <= 410))):
          mapa[5][4] = "1"

  print("x:",r.player["x"])
  print("y" , r.player["y"])
  cont = cont + 1

  pygame.display.flip()
