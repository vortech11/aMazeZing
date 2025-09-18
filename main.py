import pygame
from pygame import Vector2 as Vector2

import csv

screenSize = Vector2(800, 800)

pygame.init()

screen = pygame.display.set_mode(screenSize)

pygame.display.set_caption("A Maze Game")
clock = pygame.time.Clock()

running = True

def getRectPoints(center: Vector2, apothem: float) -> list[Vector2]:
    return [
            center - Vector2(apothem, apothem), 
            Vector2(center.x + apothem, center.y - apothem), 
            center + Vector2(apothem, apothem), 
            Vector2(center.x - apothem, center.y + apothem)
        ]

class Camera:
    def __init__(self):
        self.position: Vector2 = Vector2(0, 0)
        self.rotation: float = 0
        self.zoom: float = 0.5

    def transformPoint(self, point:Vector2):
        transformed: Vector2 = point - self.position
        transformed.rotate_rad_ip(self.rotation)
        transformed *= self.zoom
        transformed = transformed + Vector2(screenSize / 2)
        return transformed

class Geometry:
    def __init__(self):
        self.geometry = []
        self.cellSize = 50
        self.onColor = (55, 55, 55)
        self.offColor = (10, 10, 10)

    def loadGeometryFile(self, filePath):
        with open(filePath) as file:
            fileData = csv.reader(file, delimiter=",")
            for row in fileData:
                self.geometry.append([int(cell) for cell in row])

    def render(self, camera, screen):
        position = Vector2(0, 0)
        color = (0, 0, 0)
        for y, row in enumerate(self.geometry):
            for x, cell in enumerate(row):
                position = Vector2(x, y) * (self.cellSize * 2)
                if cell == 0:
                    color = self.offColor
                else:
                    color = self.onColor
                pygame.draw.polygon(screen, color, [camera.transformPoint(point) for point in getRectPoints((position), self.cellSize)])

    def isColliding(self, point: Vector2):
        index:Vector2 = Vector2(0, 0)
        index.x = round(point.x / (self.cellSize * 2))
        index.y = round(point.y / (self.cellSize* 2))

        if self.geometry[int(index.y)][int(index.x)] == 1:
            return True
        else:
            return False


class Player:
    def __init__(self):
        self.position: Vector2 = Vector2(100, 100)
        self.speed = 450
        self.size = 20
        self.color = (240, 24, 24)

    def isPlayerColliding(self, world):
        collidingPoints = [world.isColliding(point) for point in self.getPlayerWorldBB()]
        return any(collidingPoints)

    def movePlayerDirection(self, direction: Vector2, camera: Camera, world: Geometry):
        change = direction * self.speed * dt

        self.position.x += change.x
        if self.isPlayerColliding(world):
            self.position.x -= change.x
        
        self.position.y += change.y

        if self.isPlayerColliding(world):
            self.position.y -= change.y

        camera.position += (self.position - camera.position) * 0.2
        

    def getPlayerWorldBB(self):
        return [
            self.position - Vector2(self.size, self.size), 
            Vector2(self.position.x + self.size, self.position.y - self.size), 
            self.position + Vector2(self.size, self.size), 
            Vector2(self.position.x - self.size, self.position.y + self.size)
        ]

    def renderPlayer(self, screen, camera):
        pygame.draw.polygon(screen, self.color, [camera.transformPoint(point) for point in self.getPlayerWorldBB()])

camera = Camera()

player = Player()

world = Geometry()

world.loadGeometryFile("./maze-data.csv")

dt = 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    dt = clock.tick(60) / 1000.0
    
    keys = pygame.key.get_pressed()

    direction: Vector2 = Vector2(0, 0)
    direction.x = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
    direction.y = keys[pygame.K_DOWN] - keys[pygame.K_UP]
    if direction.magnitude_squared() > 0:
        direction.normalize_ip()
        direction.rotate_rad_ip(-camera.rotation)

    camera.rotation += (keys[pygame.K_a] - keys[pygame.K_d]) * 1 * dt
    camera.zoom += (keys[pygame.K_w] - keys[pygame.K_s]) * 2 * dt * camera.zoom

    if camera.zoom <= 0:
        camera.zoom = 0

    player.movePlayerDirection(direction, camera, world)

    screen.fill((0, 0, 0))

    world.render(camera, screen)

    player.renderPlayer(screen, camera)

    pygame.display.update()

pygame.quit()