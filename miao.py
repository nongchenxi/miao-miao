import pgzrun
import pygame
import random

# 定义游戏相关属性
TITLE = '喵了个喵'
WIDTH = 542
HEIGHT = 720

# 自定义游戏常量
T_WIDTH = 50
T_HEIGHT = 66

# 下方牌堆的位置
DOCK = Rect((90, 564), (T_WIDTH * 7, T_HEIGHT))

# 上方的所有牌
tiles = []
# 牌堆里的牌
docks = []
game_state = 'menu'  # 初始状态为主菜单
start_time = 0
time_limit = 0  # 游戏时间限制
difficulty = ''  # 当前选择的难度
score = 0  # 添加积分变量

# 加载字体
font = pygame.font.Font(None, 36)  # 使用默认字体，大小36
large_font = pygame.font.Font(None, 72)

# 创建主菜单按钮
easy_button = Actor('easy_button', pos=(WIDTH // 2 + 25, 400))
medium_button = Actor('medium_button', pos=(WIDTH // 2 + 25, 500))
hard_button = Actor('hard_button', pos=(WIDTH // 2 + 25, 600))

# 创建结束界面的按钮
menu_button = Actor('menu_button', pos=(WIDTH // 2, 450))
retry_button = Actor('retry_button', pos=(WIDTH // 2, 450))

# 创建“延长时间”和“打乱卡牌”按钮
extend_time_button = Actor('extend_time_button', pos=(WIDTH // 4, HEIGHT - 50))
shuffle_tiles_button = Actor('shuffle_tiles_button', pos=(3 * WIDTH // 4, HEIGHT - 50))

# 初始化牌堆
def initialize_tiles():
    global tiles, docks
    tiles = []
    docks = []
    ts = list(range(1, 9)) * 9  # 8种牌，每种9张，总计81张
    random.shuffle(ts)
    n = 0

    # 定义卡牌随机摆放的区域
    area_x_start = 50
    area_x_end = WIDTH - T_WIDTH - 50
    area_y_start = 100
    area_y_end = HEIGHT - T_HEIGHT - 250

    # 随机摆放卡牌，允许重叠
    while n < len(ts):
        t = ts[n]
        n += 1
        tile = Actor(f'tile{t}')
        x = random.randint(area_x_start, area_x_end)
        y = random.randint(area_y_start, area_y_end)
        tile.pos = (x, y)
        tile.tag = t
        tile.status = 0  # 初始状态为不可点击
        tile.z_index = n  # 使用n作为卡牌的层级，后生成的卡牌层级更高
        tiles.append(tile)

    # 放置下方额外的5张牌
    for i in range(5):
        if n >= len(ts):
            break
        t = ts[n]
        n += 1
        tile = Actor(f'tile{t}')
        tile.pos = 160 + i * tile.width, 516  # 设置下方5张牌的位置
        tile.tag = t
        tile.status = 1  # 可点
        tile.z_index = n
        tiles.append(tile)

    # 根据z_index排序，确保绘制顺序正确
    tiles.sort(key=lambda t: t.z_index)

    # 更新所有卡牌的可点击状态
    update_tile_clickable_status()

# 计算两张卡牌的重叠面积百分比
def get_overlap_percentage(tile, higher_tile):
    # 计算重叠矩形
    overlap_rect = tile.colliderect(higher_tile)
    if overlap_rect:
        # 计算重叠区域
        x_overlap = max(0, min(tile.right, higher_tile.right) - max(tile.left, higher_tile.left))
        y_overlap = max(0, min(tile.bottom, higher_tile.bottom) - max(tile.top, higher_tile.top))
        overlap_area = x_overlap * y_overlap
        tile_area = T_WIDTH * T_HEIGHT
        # 返回重叠面积的百分比
        return overlap_area / tile_area
    return 0

# 更新卡牌的可点击状态
def update_tile_clickable_status():
    # 先假设所有卡牌可点击
    for tile in tiles:
        tile.status = 1

    # 检测每张卡牌是否被更高层级的卡牌遮挡，并计算重叠面积
    for i, tile in enumerate(tiles):
        for higher_tile in tiles[i+1:]:
            overlap_percentage = get_overlap_percentage(tile, higher_tile)
            if overlap_percentage > 0.15:
                tile.status = 0  # 设置为不可点击
                break  # 一旦找到遮挡的卡牌，就无需继续检查

# 游戏帧绘制函数
def draw():
    screen.clear()

    if game_state == 'menu':
        draw_menu()
    elif game_state == 'playing':
        draw_game()
    elif game_state == 'win':
        draw_win()
    elif game_state == 'lose':
        draw_lose()

# 绘制主菜单
def draw_menu():
    screen.blit('back8', (0, 0))
    easy_button.draw()
    medium_button.draw()
    hard_button.draw()

# 游戏帧绘制函数
def draw_game():
    screen.blit('back5', (0, 0))
    # 按照z_index顺序绘制卡牌
    for tile in tiles:
        tile.draw()
        if tile.status == 0:
            screen.blit('mask', tile.topleft)
    for i, tile in enumerate(docks):
        tile.left = (DOCK.x + i * T_WIDTH)
        tile.top = DOCK.y
        tile.draw()

    # 显示倒计时
    elapsed_time = pygame.time.get_ticks() - start_time
    remaining_time = (time_limit - elapsed_time) // 1000
    if remaining_time < 0:
        remaining_time = 0
    text = font.render(f"Time Left: {remaining_time}s", True, (255, 255, 255))  # 渲染文本
    screen.blit(text, (50, 10))  # 绘制文本到屏幕上

    # 显示积分
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))  # 渲染积分
    screen.blit(score_text, (WIDTH - 150, 10))  # 绘制积分文本到屏幕上

    # 绘制“延长时间”和“打乱卡牌”按钮
    extend_time_button.draw()
    shuffle_tiles_button.draw()

# 绘制胜利界面
def draw_win():
    screen.blit('back6', (0, 0))
    win_text = large_font.render(f"You Win! ", True, (255, 255, 255))
    screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - win_text.get_height() // 2 - 150))
    menu_button.draw()

# 绘制失败界面
def draw_lose():
    screen.blit('back4', (0, 0))
    lose_text = large_font.render(f"Game Over. Score: {score}", True, (255, 255, 255))
    screen.blit(lose_text, (WIDTH // 2 - lose_text.get_width() // 2, HEIGHT // 2 - lose_text.get_height() // 2 + 120))
    retry_button.draw()

# 游戏循环更新函数
def update():
    global game_state

    if game_state == 'playing':
        elapsed_time = pygame.time.get_ticks() - start_time
        if elapsed_time > time_limit:
            game_state = 'lose'

        if len(tiles) == 0:
            game_state = 'win'
        # 超过7张，失败
        if len(docks) >= 7:
            game_state = 'lose'

# 游戏开始
def start_game(selected_difficulty):
    global start_time, time_limit, game_state, difficulty, score

    difficulty = selected_difficulty
    initialize_tiles()
    score = 0  # 重置积分

    if difficulty == 'easy':
        time_limit = 180000  # 3分钟
    elif difficulty == 'medium':
        time_limit = 150000  # 2分30秒
    elif difficulty == 'hard':
        time_limit = 60000  # 1分钟

    start_time = pygame.time.get_ticks()
    game_state = 'playing'

# 延长时间的处理函数
def extend_time():
    global time_limit
    time_limit += 30000  # 延长30秒

# 打乱卡牌的处理函数
def shuffle_tiles():
    remaining_tiles = [tile for tile in tiles if tile.status == 1]  # 获取未消除的卡牌
    random.shuffle(remaining_tiles)  # 打乱卡牌顺序

    # 定义卡牌随机摆放的区域
    area_x_start = 50
    area_x_end = WIDTH - T_WIDTH - 50
    area_y_start = 100
    area_y_end = HEIGHT - T_HEIGHT - 250

    for tile in remaining_tiles:
        x = random.randint(area_x_start, area_x_end)
        y = random.randint(area_y_start, area_y_end)
        tile.pos = (x, y)

    update_tile_clickable_status()

# 鼠标点击响应
def on_mouse_down(pos):
    global game_state

    if game_state == 'menu':
        if easy_button.collidepoint(pos):
            start_game('easy')
        elif medium_button.collidepoint(pos):
            start_game('medium')
        elif hard_button.collidepoint(pos):
            start_game('hard')

    elif game_state == 'win':
        if menu_button.collidepoint(pos):
            game_state = 'menu'

    elif game_state == 'lose':
        if retry_button.collidepoint(pos):
            start_game(difficulty)

    elif game_state == 'playing':
        if extend_time_button.collidepoint(pos):
            extend_time()  # 点击“延长时间”按钮
        elif shuffle_tiles_button.collidepoint(pos):
            shuffle_tiles()  # 点击“打乱卡牌”按钮
        else:
            handle_tile_click(pos)

# 处理牌点击逻辑
def handle_tile_click(pos):
    global docks, score

    if len(docks) >= 7 or len(tiles) == 0:
        return
    # 按照z_index逆序遍历，先检查最上层的卡牌
    for tile in reversed(tiles):
        if tile.status == 1 and tile.collidepoint(pos):
            tile.status = 2  # 标记为已点击
            tiles.remove(tile)
            diff = [t for t in docks if t.tag != tile.tag]
            if len(docks) - len(diff) < 2:
                docks.append(tile)
            else:
                score += 10
                docks = diff
            update_tile_clickable_status()  # 更新所有牌的状态
            
            
            return

pgzrun.go()
