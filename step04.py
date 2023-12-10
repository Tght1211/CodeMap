import pygame
import sys
import random

# 初始化Pygame
pygame.init()

# 游戏窗口设置
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("飞机大战游戏")

# 颜色定义
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# 飞机设置
player_size = 50
player_x = WIDTH // 2 - player_size // 2
player_y = HEIGHT - 2 * player_size
player_speed = 10

# 子弹设置
bullet_size = 10
bullet_speed = 10
bullets = []

# 敌人设置
enemy_size = 50
enemy_speed = 2
enemies = []

# 记录分数
score = 0

# 游戏主循环
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)  # 控制帧率

    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 移动飞机
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
        player_x += player_speed

    # 发射子弹
    if keys[pygame.K_SPACE]:
        bullets.append([player_x + player_size // 2 - bullet_size // 2, player_y - bullet_size])

    # 移动子弹
    bullets = [[bx, by - bullet_speed] for bx, by in bullets if by > 0]

    # 生成敌人
    if random.randint(1, 30) == 1:
        enemy_x = random.randint(0, WIDTH - enemy_size)
        enemies.append([enemy_x, 0])

    # 移动敌人
    enemies = [[ex, ey + enemy_speed] for ex, ey in enemies if ey < HEIGHT]

    # 检查碰撞
    for bullet in bullets:
        for enemy in enemies:
            if (
                enemy[0] < bullet[0] < enemy[0] + enemy_size
                and enemy[1] < bullet[1] < enemy[1] + enemy_size
            ):
                enemies.remove(enemy)
                bullets.remove(bullet)
                score += 1

    # 渲染画面
    win.fill(WHITE)
    pygame.draw.rect(win, RED, (player_x, player_y, player_size, player_size))  # 绘制飞机

    for bullet in bullets:
        pygame.draw.rect(win, RED, (bullet[0], bullet[1], bullet_size, bullet_size))  # 绘制子弹

    for enemy in enemies:
        pygame.draw.rect(win, RED, (enemy[0], enemy[1], enemy_size, enemy_size))  # 绘制敌人

    # 显示分数
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, RED)
    win.blit(text, (10, 10))

    pygame.display.update()

# 退出游戏
pygame.quit()
sys.exit()
