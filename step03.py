import pygame
import random
import sys

# 初始化Pygame
pygame.init()

# 设置窗口大小和标题
width, height = 2560, 1440
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Meteor Shower Simulation")

# 定义颜色
black = (0, 0, 0)
blue = (0, 0, 255)
purple = (128, 0, 128)
orange = (255, 165, 0)

# 定义流星雨粒子类
class MeteorParticle:
    def __init__(self):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.speed = random.uniform(2, 3)
        self.length = random.randint(10, 30)
        self.color = random.choice([blue, purple, orange])

    def update(self):
        self.y += self.speed
        if self.y > height:
            self.y = 0
            self.x = random.randint(0, width)

    def draw(self):
        pygame.draw.line(screen, self.color, (self.x, self.y), (self.x, self.y + self.length), 2)

# 创建流星雨粒子列表
meteors = [MeteorParticle() for _ in range(100)]

# 游戏循环
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 清空屏幕
    screen.fill(black)

    # 更新和绘制流星雨粒子
    for meteor in meteors:
        meteor.update()
        meteor.draw()

    # 更新屏幕
    pygame.display.flip()

    # 控制帧率
    pygame.time.Clock().tick(60)
