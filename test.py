import pygame
import random
import os
import time

# Инициализация Pygame
pygame.init()

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)
GRAY = (100, 100, 100)
SILVER = (192, 192, 192)

# Настройки экрана
WIDTH, HEIGHT = 600, 400
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Создание экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка - Собери мир!")

# Инициализация звуковой системы
pygame.mixer.init()

# Система уровней
LEVELS = [
    {
        "name": "Лес",
        "puzzles_needed": 6,  # Пазлов для открытия
        "background_file": "level1_forest.jpg",
        "unlocked": True,  # Первый уровень открыт сразу
        "completed": False,
        "color": (34, 139, 34)  # Зеленый для леса
    },
    {
        "name": "Горы",
        "puzzles_needed": 12,
        "background_file": "level2_mountains.jpg", 
        "unlocked": False,
        "completed": False,
        "color": (139, 137, 137)  # Серый для гор
    },
    {
        "name": "Океан",
        "puzzles_needed": 18,
        "background_file": "level3_ocean.jpg",
        "unlocked": False,
        "completed": False,
        "color": (30, 144, 255)  # Синий для океана
    },
    {
        "name": "Пустыня",
        "puzzles_needed": 24,
        "background_file": "level4_desert.jpg",
        "unlocked": False,
        "completed": False,
        "color": (238, 203, 173)  # Песочный для пустыни
    },
    {
        "name": "Космос",
        "puzzles_needed": 30,
        "background_file": "level5_space.jpg",
        "unlocked": False,
        "completed": False,
        "color": (25, 25, 112)  # Темно-синий для космоса
    }
]

# Глобальные переменные для сохранения прогресса
TOTAL_PUZZLES_COLLECTED = 0  # Общее количество собранных пазлов

def save_progress():
    """Сохранение прогресса в файл"""
    try:
        with open("game_progress.txt", "w") as f:
            f.write(f"total_puzzles={TOTAL_PUZZLES_COLLECTED}\n")
            for i, level in enumerate(LEVELS):
                f.write(f"level_{i}_unlocked={1 if level['unlocked'] else 0}\n")
                f.write(f"level_{i}_completed={1 if level['completed'] else 0}\n")
    except Exception as e:
        print(f"Ошибка сохранения прогресса: {e}")

def load_progress():
    """Загрузка прогресса из файла"""
    global TOTAL_PUZZLES_COLLECTED
    
    try:
        if os.path.exists("game_progress.txt"):
            with open("game_progress.txt", "r") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if "=" in line:
                        key, value = line.split("=")
                        if key == "total_puzzles":
                            TOTAL_PUZZLES_COLLECTED = int(value)
                        elif key.startswith("level_") and key.endswith("_unlocked"):
                            level_index = int(key.split("_")[1])
                            if level_index < len(LEVELS):
                                LEVELS[level_index]["unlocked"] = bool(int(value))
                        elif key.startswith("level_") and key.endswith("_completed"):
                            level_index = int(key.split("_")[1])
                            if level_index < len(LEVELS):
                                LEVELS[level_index]["completed"] = bool(int(value))
            print(f"Прогресс загружен: {TOTAL_PUZZLES_COLLECTED} пазлов")
            return True
    except Exception as e:
        print(f"Ошибка загрузки прогресса: {e}")
    
    return False

def load_sounds():
    """Загрузка звуковых эффектов"""
    sounds = {}
    
    try:
        # Фоновая музыка
        if os.path.exists("background_music.mp3"):
            pygame.mixer.music.load("background_music.mp3")
        else:
            print("Файл background_music.mp3 не найден")
        
        # Звук поедания еды
        if os.path.exists("eat_sound.wav"):
            sounds["eat"] = pygame.mixer.Sound("eat_sound.wav")
        else:
            print("Файл eat_sound.wav не найден")
            sounds["eat"] = None
            
        # Звук game over
        if os.path.exists("game_over.wav"):
            sounds["game_over"] = pygame.mixer.Sound("game_over.wav")
        else:
            print("Файл game_over.wav не найден")
            sounds["game_over"] = None
            
        # Звук открытия пазла
        if os.path.exists("puzzle_open.wav"):
            sounds["puzzle_open"] = pygame.mixer.Sound("puzzle_open.wav")
            sounds["puzzle_open"].set_volume(0.3)  # Громкость звука открытия пазла
        else:
            print("Файл puzzle_open.wav не найден")
            sounds["puzzle_open"] = None
            
        # Звук победы
        if os.path.exists("win_sound.wav"):
            sounds["win"] = pygame.mixer.Sound("win_sound.wav")
        else:
            print("Файл win_sound.wav не найден")
            sounds["win"] = None
            
        # Звук открытия уровня
        if os.path.exists("level_unlock.wav"):
            sounds["level_unlock"] = pygame.mixer.Sound("level_unlock.wav")
        else:
            print("Файл level_unlock.wav не найден")
            sounds["level_unlock"] = None
            
    except pygame.error as e:
        print(f"Ошибка загрузки звуков: {e}")
        sounds = {"eat": None, "game_over": None, "puzzle_open": None, "win": None, "level_unlock": None}
    
    return sounds

def load_background_for_level(level_index):
    """Загрузка фонового изображения для уровня"""
    level = LEVELS[level_index]
    
    # Если файл не найден, создаем фон по умолчанию для уровня
    if not os.path.exists(level["background_file"]):
        print(f"Файл {level['background_file']} не найден, создаем фон по умолчанию")
        return create_level_background(level_index)
    
    try:
        background = pygame.image.load(level["background_file"])
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        return background
    except pygame.error as e:
        print(f"Ошибка загрузки фона для уровня {level_index}: {e}")
        return create_level_background(level_index)

def create_level_background(level_index):
    """Создание фона по умолчанию для уровня"""
    background = pygame.Surface((WIDTH, HEIGHT))
    level = LEVELS[level_index]
    
    # Создаем уникальный фон для каждого уровня
    if level_index == 0:  # Лес
        # Градиент от светло-зеленого к темно-зеленому
        for y in range(HEIGHT):
            green = 200 - int((y / HEIGHT) * 100)
            color = (50, green, 50)
            pygame.draw.line(background, color, (0, y), (WIDTH, y))
        
        # Добавляем деревья
        for _ in range(30):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            tree_color = (0, random.randint(100, 150), 0)
            pygame.draw.rect(background, tree_color, (x, y, 15, 30))
            pygame.draw.circle(background, tree_color, (x + 7, y - 10), 20)
            
    elif level_index == 1:  # Горы
        # Градиент от светло-серого к темно-серому
        for y in range(HEIGHT):
            gray = 200 - int((y / HEIGHT) * 100)
            color = (gray, gray, gray)
            pygame.draw.line(background, color, (0, y), (WIDTH, y))
        
        # Добавляем горные пики
        for i in range(5):
            x = i * (WIDTH // 5)
            points = [
                (x, HEIGHT),
                (x + 50, HEIGHT - 150),
                (x + 100, HEIGHT)
            ]
            mountain_color = (random.randint(150, 200), random.randint(150, 200), random.randint(150, 200))
            pygame.draw.polygon(background, mountain_color, points)
            
    elif level_index == 2:  # Океан
        # Градиент от светло-голубого к темно-синему
        for y in range(HEIGHT):
            blue = 255 - int((y / HEIGHT) * 155)
            color = (0, 100, blue)
            pygame.draw.line(background, color, (0, y), (WIDTH, y))
        
        # Добавляем волны
        for i in range(10):
            y = HEIGHT - 50 + random.randint(-10, 10)
            pygame.draw.arc(background, (0, 50, 200), 
                           (i * 60, y, 60, 30), 0, 3.14, 3)
            
    elif level_index == 3:  # Пустыня
        # Песочный градиент
        for y in range(HEIGHT):
            sand = 240 - int((y / HEIGHT) * 40)
            color = (sand, sand - 40, sand - 80)
            pygame.draw.line(background, color, (0, y), (WIDTH, y))
        
        # Добавляем кактусы
        for _ in range(20):
            x = random.randint(0, WIDTH)
            y = random.randint(HEIGHT - 100, HEIGHT - 30)
            cactus_color = (0, random.randint(150, 200), 0)
            pygame.draw.rect(background, cactus_color, (x, y, 10, 40))
            pygame.draw.rect(background, cactus_color, (x - 10, y + 10, 10, 20))
            pygame.draw.rect(background, cactus_color, (x + 10, y + 15, 10, 15))
            
    elif level_index == 4:  # Космос
        # Темный фон с звездами
        background.fill((10, 10, 40))
        
        # Звезды
        for _ in range(100):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size = random.randint(1, 3)
            brightness = random.randint(200, 255)
            pygame.draw.circle(background, (brightness, brightness, brightness), (x, y), size)
        
        # Планеты
        for i in range(3):
            x = random.randint(100, WIDTH - 100)
            y = random.randint(50, HEIGHT - 50)
            radius = random.randint(30, 60)
            planet_color = (
                random.randint(100, 200),
                random.randint(100, 200),
                random.randint(100, 200)
            )
            pygame.draw.circle(background, planet_color, (x, y), radius)
    
    return background

def load_puzzle_cover():
    """Загрузка картинки для закрытых пазлов"""
    try:
        if os.path.exists("puzzle_cover.jpg"):
            cover = pygame.image.load("puzzle_cover.jpg")
            return cover
        elif os.path.exists("puzzle_cover.png"):
            cover = pygame.image.load("puzzle_cover.png")
            return cover
        else:
            print("Файлы puzzle_cover.jpg или puzzle_cover.png не найдены")
            return create_default_puzzle_cover()
    except pygame.error as e:
        print(f"Ошибка загрузки картинки пазла: {e}")
        return create_default_puzzle_cover()

def create_default_puzzle_cover():
    """Создание картинки для пазлов по умолчанию"""
    cover = pygame.Surface((200, 150))
    cover.fill((50, 50, 80))
    
    # Рисуем текстуру пазла
    for i in range(0, 200, 10):
        pygame.draw.line(cover, (70, 70, 100), (i, 0), (i, 150), 1)
    for i in range(0, 150, 10):
        pygame.draw.line(cover, (70, 70, 100), (0, i), (200, i), 1)
    
    # Рисуем значок вопроса
    font = pygame.font.SysFont('arial', 80)
    text = font.render("?", True, (150, 150, 180))
    text_rect = text.get_rect(center=(100, 75))
    cover.blit(text, text_rect)
    
    # Добавляем рамку
    pygame.draw.rect(cover, (100, 100, 150), cover.get_rect(), 3)
    
    return cover

def get_puzzle_regions():
    """Определяем регионы для 6 пазлов (2x3)"""
    regions = []
    puzzle_width = WIDTH // 3
    puzzle_height = HEIGHT // 2
    
    for row in range(2):
        for col in range(3):
            x = col * puzzle_width
            y = row * puzzle_height
            regions.append(pygame.Rect(x, y, puzzle_width, puzzle_height))
    
    return regions

def draw_puzzle_overlay(surface, revealed_regions, background, puzzle_cover, available_puzzles, game_won=False):
    """Отрисовка пазлов с картинкой для закрытых регионов"""
    if background is None:
        surface.fill((30, 30, 60))
    else:
        surface.blit(background, (0, 0))
    
    if game_won:
        return
    
    regions = get_puzzle_regions()
    
    for i, region in enumerate(regions):
        if i not in revealed_regions:
            scaled_cover = pygame.transform.scale(puzzle_cover, (region.width, region.height))
            surface.blit(scaled_cover, (region.x, region.y))
            
            if i in available_puzzles:
                font = pygame.font.SysFont('arial', 20)
                text = font.render(str(i + 1), True, (200, 200, 200))
                text_rect = text.get_rect(center=region.center)
                
                text_bg = pygame.Surface((text.get_width() + 10, text.get_height() + 5), pygame.SRCALPHA)
                text_bg.fill((0, 0, 0, 200))
                surface.blit(text_bg, (text_rect.x - 5, text_rect.y - 2))
                surface.blit(text, text_rect)
        else:
            pygame.draw.rect(surface, WHITE, region, 3)
            
            font = pygame.font.SysFont('arial', 20)
            text = font.render(str(i + 1), True, WHITE)
            text_rect = text.get_rect(center=region.center)
            
            text_bg = pygame.Surface((text.get_width() + 10, text.get_height() + 5), pygame.SRCALPHA)
            text_bg.fill((0, 0, 0, 150))
            surface.blit(text_bg, (text_rect.x - 5, text_rect.y - 2))
            surface.blit(text, text_rect)

def play_background_music():
    """Воспроизведение фоновой музыки"""
    try:
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)
    except pygame.error as e:
        print(f"Ошибка воспроизведения музыки: {e}")

def draw_grid(surface):
    """Отрисовка полупрозрачной сетки"""
    for y in range(0, HEIGHT, GRID_SIZE):
        for x in range(0, WIDTH, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            grid_surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
            grid_surface.fill((255, 255, 255, 30))
            surface.blit(grid_surface, (x, y))

def show_score(surface, score, revealed_puzzles_set, current_level, game_won=False):
    """Отображение счета и прогресса"""
    font = pygame.font.SysFont('arial', 20)
    
    current_level_data = LEVELS[current_level]
    
    if game_won:
        score_text = font.render(f'ФИНАЛЬНЫЙ СЧЕТ: {score}', True, GOLD)
        level_text = font.render(f'УРОВЕНЬ: {current_level_data["name"]}', True, GOLD)
        puzzle_text = font.render('ВСЕ ПАЗЛЫ СОБРАНЫ!', True, GOLD)
    else:
        score_text = font.render(f'Счет: {score}', True, WHITE)
        level_text = font.render(f'Уровень: {current_level_data["name"]}', True, WHITE)
        
        # Получаем количество открытых пазлов из множества
        puzzles_opened_in_level = len(revealed_puzzles_set)
        puzzles_in_level = 6
        
        puzzle_text = font.render(f'Пазлов в уровне: {puzzles_opened_in_level}/{puzzles_in_level}', True, WHITE)
        
        # Показываем прогресс до следующего уровня
        next_level_index = current_level + 1
        if next_level_index < len(LEVELS):
            next_level_data = LEVELS[next_level_index]
            puzzles_for_next_level = next_level_data["puzzles_needed"] - TOTAL_PUZZLES_COLLECTED
            if puzzles_for_next_level > 0:
                next_level_text = font.render(f'До уровня "{next_level_data["name"]}": {puzzles_for_next_level} пазлов', True, YELLOW)
            else:
                next_level_text = font.render('Новый уровень доступен!', True, GOLD)
        else:
            next_level_text = font.render('Последний уровень!', True, GOLD)
    
    # Фон для текста
    texts_to_display = [score_text, level_text, puzzle_text]
    if not game_won:
        texts_to_display.append(next_level_text)
    
    max_width = max(text.get_width() for text in texts_to_display)
    text_bg = pygame.Surface((max_width + 10, 
                             score_text.get_height() * len(texts_to_display) + 15), pygame.SRCALPHA)
    bg_color = (0, 0, 0, 200) if game_won else (0, 0, 0, 150)
    text_bg.fill(bg_color)
    surface.blit(text_bg, (5, 5))
    
    # Отображаем текст
    y_offset = 8
    for text in texts_to_display:
        surface.blit(text, (10, y_offset))
        y_offset += 27

def show_level_unlocked(surface, level_index):
    """Показ уведомления об открытии уровня"""
    level = LEVELS[level_index]
    
    # Полупрозрачный фон
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    font_large = pygame.font.SysFont('arial', 50)
    font_medium = pygame.font.SysFont('arial', 30)
    font_small = pygame.font.SysFont('arial', 24)
    
    unlocked_text = font_large.render('НОВЫЙ УРОВЕНЬ!', True, GOLD)
    level_name_text = font_medium.render(f'"{level["name"]}"', True, level["color"])
    info_text = font_small.render('Доступен для игры', True, WHITE)
    continue_text = font_small.render('Нажмите любую клавишу для продолжения', True, WHITE)
    
    # Фон для текста
    text_area = pygame.Surface((WIDTH - 100, 200), pygame.SRCALPHA)
    text_area.fill((0, 0, 0, 200))
    surface.blit(text_area, (50, HEIGHT//2 - 100))
    
    # Иконка уровня
    level_icon = pygame.Surface((80, 80))
    level_icon.fill(level["color"])
    pygame.draw.rect(level_icon, WHITE, level_icon.get_rect(), 3)
    
    # Номер уровня
    font_icon = pygame.font.SysFont('arial', 40)
    icon_text = font_icon.render(str(level_index + 1), True, WHITE)
    icon_rect = icon_text.get_rect(center=(40, 40))
    level_icon.blit(icon_text, icon_rect)
    
    surface.blit(level_icon, (WIDTH//2 - 40, HEIGHT//2 - 140))
    surface.blit(unlocked_text, (WIDTH//2 - unlocked_text.get_width()//2, HEIGHT//2 - 40))
    surface.blit(level_name_text, (WIDTH//2 - level_name_text.get_width()//2, HEIGHT//2 + 10))
    surface.blit(info_text, (WIDTH//2 - info_text.get_width()//2, HEIGHT//2 + 50))
    surface.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 90))
    
    pygame.display.update()
    
    # Ждем нажатия клавиши
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                waiting = False
    return True

def show_level_completed(surface, score, current_level_index, next_level_available):
    """Показ экрана завершения уровня"""
    current_level = LEVELS[current_level_index]
    
    # Полупрозрачный фон
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    font_large = pygame.font.SysFont('arial', 60)
    font_medium = pygame.font.SysFont('arial', 35)
    font_small = pygame.font.SysFont('arial', 28)
    
    completed_text = font_large.render('УРОВЕНЬ ПРОЙДЕН!', True, GOLD)
    level_text = font_medium.render(f'"{current_level["name"]}"', True, current_level["color"])
    score_text = font_medium.render(f'Счет на уровне: {score}', True, WHITE)
    
    if next_level_available:
        next_text = font_medium.render('Следующий уровень разблокирован!', True, YELLOW)
        continue_text = font_small.render('Нажмите ПРОБЕЛ для следующего уровня', True, WHITE)
        menu_text = font_small.render('Или ESC для выбора уровня', True, WHITE)
    else:
        next_text = font_medium.render('Это последний уровень!', True, YELLOW)
        continue_text = font_small.render('Нажмите ESC для выбора уровня', True, WHITE)
        menu_text = font_small.render('', True, WHITE)
    
    # Фон для текста
    text_area = pygame.Surface((WIDTH - 100, 250), pygame.SRCALPHA)
    text_area.fill((0, 0, 0, 200))
    surface.blit(text_area, (50, HEIGHT//2 - 125))
    
    surface.blit(completed_text, (WIDTH//2 - completed_text.get_width()//2, HEIGHT//2 - 100))
    surface.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 - 30))
    surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 10))
    surface.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 50))
    surface.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 100))
    surface.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, HEIGHT//2 + 130))
    
    pygame.display.update()
    
    # Ждем нажатия клавиши
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and next_level_available:
                    return "next_level"
                elif event.key == pygame.K_ESCAPE:
                    return "menu"
                elif event.key == pygame.K_r:
                    return "restart"
    return None

def show_game_over(surface, score, revealed_puzzles_set, background, puzzle_cover, available_puzzles, level_index):
    """Показ экрана проигрыша"""
    puzzles_in_current_level = len(revealed_puzzles_set)
        
    draw_puzzle_overlay(surface, set(range(puzzles_in_current_level)), background, puzzle_cover, available_puzzles)
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    font_large = pygame.font.SysFont('arial', 50)
    font_medium = pygame.font.SysFont('arial', 30)
    font_small = pygame.font.SysFont('arial', 24)
    
    level = LEVELS[level_index]
    
    game_over_text = font_large.render('ИГРА ОКОНЧЕНА!', True, RED)
    level_text = font_medium.render(f'Уровень: {level["name"]}', True, level["color"])
    score_text = font_medium.render(f'Счет: {score}', True, WHITE)
    puzzle_text = font_medium.render(f'Всего собрано пазлов: {TOTAL_PUZZLES_COLLECTED}', True, WHITE)
    restart_text = font_small.render('Нажмите R для перезапуска уровня', True, WHITE)
    menu_text = font_small.render('Нажмите ESC для выбора уровня', True, WHITE)
    
    surface.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
    surface.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 - 40))
    surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    surface.blit(puzzle_text, (WIDTH//2 - puzzle_text.get_width()//2, HEIGHT//2 + 40))
    surface.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 80))
    surface.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, HEIGHT//2 + 110))
    
    pygame.display.update()

class Snake:
    def __init__(self, sound_manager, current_level_index):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.length = 1
        self.score = 0
        self.sound_manager = sound_manager
        self.revealed_puzzles = set()
        self.available_puzzles = list(range(6))
        random.shuffle(self.available_puzzles)
        self.current_level_index = current_level_index
        self.game_won = False
        self.new_level_unlocked = False
        self.unlocked_level_index = None
        
    def get_head_position(self):
        return self.positions[0]
    
    def move(self):
        if self.game_won:
            return False
            
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_x = (head_x + dir_x) % GRID_WIDTH
        new_y = (head_y + dir_y) % GRID_HEIGHT
        
        if (new_x, new_y) in self.positions[1:]:
            return True
            
        self.positions.insert(0, (new_x, new_y))
        if len(self.positions) > self.length:
            self.positions.pop()
        return False
    
    def grow(self, points):
        self.length += 1
        self.score += points
        
        # Открываем новый пазл каждые 100 очков
        if not self.game_won and self.score // 100 > len(self.revealed_puzzles):
            if self.available_puzzles:
                new_puzzle = self.available_puzzles.pop(0)
                self.revealed_puzzles.add(new_puzzle)
                global TOTAL_PUZZLES_COLLECTED
                TOTAL_PUZZLES_COLLECTED += 1
                
                if self.sound_manager["puzzle_open"]:
                    self.sound_manager["puzzle_open"].play()
                print(f"Открыт пазл {new_puzzle + 1}! Всего: {TOTAL_PUZZLES_COLLECTED}")
                
                # Сохраняем прогресс
                save_progress()
                
                # Проверяем, собраны ли все пазлы уровня
                if len(self.revealed_puzzles) == 6:
                    self.game_won = True
                    if self.sound_manager["win"]:
                        self.sound_manager["win"].play()
                    print(f"Уровень пройден! Всего пазлов: {TOTAL_PUZZLES_COLLECTED}")
                    
                    # Отмечаем текущий уровень как пройденный
                    LEVELS[self.current_level_index]["completed"] = True
                    
                    # Проверяем и открываем следующий уровень
                    next_level_index = self.current_level_index + 1
                    if next_level_index < len(LEVELS):
                        if TOTAL_PUZZLES_COLLECTED >= LEVELS[next_level_index]["puzzles_needed"]:
                            if not LEVELS[next_level_index]["unlocked"]:
                                LEVELS[next_level_index]["unlocked"] = True
                                self.new_level_unlocked = True
                                self.unlocked_level_index = next_level_index
                                if self.sound_manager["level_unlock"]:
                                    self.sound_manager["level_unlock"].play()
                                print(f"Открыт новый уровень: {LEVELS[next_level_index]['name']}!")
                    save_progress()
                
                # Проверяем, открылся ли новый уровень по количеству пазлов
                for i, level in enumerate(LEVELS):
                    if not level["unlocked"] and TOTAL_PUZZLES_COLLECTED >= level["puzzles_needed"]:
                        level["unlocked"] = True
                        self.new_level_unlocked = True
                        self.unlocked_level_index = i
                        if self.sound_manager["level_unlock"]:
                            self.sound_manager["level_unlock"].play()
                        print(f"Открыт новый уровень: {level['name']}!")
                        save_progress()
        
        if self.sound_manager["eat"]:
            self.sound_manager["eat"].play()
    
    def change_direction(self, new_direction):
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction
    
    def draw(self, surface):
        for i, position in enumerate(self.positions):
            rect = pygame.Rect(position[0] * GRID_SIZE, position[1] * GRID_SIZE, 
                             GRID_SIZE, GRID_SIZE)
            if i == 0:
                pygame.draw.rect(surface, (0, 200, 0), rect)
            else:
                color = (0, 180, 0) if i % 2 == 0 else (0, 160, 0)
                pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.points = 10
        self.color = RED
        self.type = "normal"
        self.randomize_position()
        self.randomize_type()
    
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), 
                        random.randint(0, GRID_HEIGHT - 1))
    
    def randomize_type(self):
        food_types = [
            {"points": 10, "color": RED, "name": "normal", "rarity": 50},
            {"points": 20, "color": ORANGE, "name": "good", "rarity": 30},
            {"points": 30, "color": YELLOW, "name": "great", "rarity": 15},
            {"points": 40, "color": BLUE, "name": "excellent", "rarity": 4},
            {"points": 50, "color": PURPLE, "name": "amazing", "rarity": 1}
        ]
        
        total_rarity = sum(food["rarity"] for food in food_types)
        roll = random.randint(1, total_rarity)
        
        current_rarity = 0
        for food_type in food_types:
            current_rarity += food_type["rarity"]
            if roll <= current_rarity:
                self.points = food_type["points"]
                self.color = food_type["color"]
                self.type = food_type["name"]
                break
    
    def draw(self, surface):
        rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE,
                         GRID_SIZE, GRID_SIZE)
        
        pygame.draw.rect(surface, self.color, rect)
        
        if self.points == 20:
            inner_rect = pygame.Rect(rect.x + 5, rect.y + 5, GRID_SIZE - 10, GRID_SIZE - 10)
            pygame.draw.rect(surface, YELLOW, inner_rect)
        elif self.points == 30:
            pygame.draw.circle(surface, ORANGE, rect.center, GRID_SIZE // 3)
        elif self.points == 40:
            points = [
                (rect.centerx, rect.y + 3),
                (rect.x + GRID_SIZE - 3, rect.centery),
                (rect.centerx, rect.y + GRID_SIZE - 3),
                (rect.x + 3, rect.centery)
            ]
            pygame.draw.polygon(surface, WHITE, points)
        elif self.points == 50:
            pygame.draw.circle(surface, WHITE, rect.center, GRID_SIZE // 4)
        
        pygame.draw.rect(surface, BLACK, rect, 1)

def show_level_selection(surface, sounds):
    """Экран выбора уровня"""
    selected_level = 0
    
    while True:
        surface.fill((20, 20, 40))
        
        font_large = pygame.font.SysFont('arial', 60)
        font_medium = pygame.font.SysFont('arial', 30)
        font_small = pygame.font.SysFont('arial', 24)
        
        title = font_large.render('ВЫБЕРИ УРОВЕНЬ', True, GOLD)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        
        total_puzzles_text = font_medium.render(f'Всего собрано пазлов: {TOTAL_PUZZLES_COLLECTED}', True, WHITE)
        surface.blit(total_puzzles_text, (WIDTH//2 - total_puzzles_text.get_width()//2, 100))
        
        instructions = font_small.render('Используйте стрелки для выбора, ENTER для старта', True, WHITE)
        surface.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT - 40))
        
        # Отображаем уровни
        for i, level in enumerate(LEVELS):
            x = WIDTH//2 - 200 + (i % 3) * 140
            y = 150 + (i // 3) * 120
            
            # Фон для уровня
            level_bg = pygame.Surface((120, 100), pygame.SRCALPHA)
            
            if level["unlocked"]:
                if i == selected_level:
                    level_bg.fill((*level["color"], 200))  # Выбранный открытый
                    border_color = GOLD
                else:
                    level_bg.fill((*level["color"], 150))  # Открытый
                    border_color = WHITE
                
                # Иконка замка открыт
                lock_text = "✓" if level["completed"] else str(i + 1)
                lock_color = GOLD if level["completed"] else WHITE
            else:
                level_bg.fill((50, 50, 50, 200))  # Заблокированный
                border_color = GRAY
                lock_text = "🔒"
                lock_color = GRAY
            
            pygame.draw.rect(level_bg, border_color, level_bg.get_rect(), 3)
            surface.blit(level_bg, (x, y))
            
            # Название уровня
            name_font = pygame.font.SysFont('arial', 18)
            name_text = name_font.render(level["name"], True, WHITE if level["unlocked"] else GRAY)
            surface.blit(name_text, (x + 60 - name_text.get_width()//2, y + 70))
            
            # Номер/замок
            lock_font = pygame.font.SysFont('arial', 40)
            lock_render = lock_font.render(lock_text, True, lock_color)
            surface.blit(lock_render, (x + 60 - lock_render.get_width()//2, y + 20))
            
            # Требования для закрытых уровней
            if not level["unlocked"]:
                req_font = pygame.font.SysFont('arial', 14)
                req_text = req_font.render(f"Нужно {level['puzzles_needed']} пазлов", True, YELLOW)
                surface.blit(req_text, (x + 60 - req_text.get_width()//2, y + 85))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and selected_level >= 3:
                    selected_level -= 3
                elif event.key == pygame.K_DOWN and selected_level + 3 < len(LEVELS):
                    selected_level += 3
                elif event.key == pygame.K_LEFT and selected_level > 0:
                    selected_level -= 1
                elif event.key == pygame.K_RIGHT and selected_level < len(LEVELS) - 1:
                    selected_level += 1
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if LEVELS[selected_level]["unlocked"]:
                        return selected_level
                elif event.key == pygame.K_ESCAPE:
                    return None
    
    return 0

def main():
    global TOTAL_PUZZLES_COLLECTED
    
    clock = pygame.time.Clock()
    
    # Загружаем прогресс
    load_progress()
    
    # Загружаем звуки и картинку для пазлов
    sounds = load_sounds()
    puzzle_cover = load_puzzle_cover()
    
    # Показываем меню выбора уровня
    current_level_index = show_level_selection(screen, sounds)
    if current_level_index is None:
        pygame.quit()
        return
    
    # Загружаем фон для выбранного уровня
    background = load_background_for_level(current_level_index)
    
    # Запускаем музыку
    play_background_music()
    
    snake = Snake(sounds, current_level_index)
    food = Food()
    game_over = False
    game_won = False
    game_over_sound_played = False
    win_sound_played = False
    FPS = 10
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
                
            if event.type == pygame.KEYDOWN:
                if game_over or game_won:
                    # Обработка на экране завершения уровня
                    pass
                else:
                    if event.key == pygame.K_UP:
                        snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction((1, 0))
                    elif event.key == pygame.K_SPACE:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
                    elif event.key == pygame.K_ESCAPE:
                        # Возврат к выбору уровня
                        current_level_index = show_level_selection(screen, sounds)
                        if current_level_index is None:
                            pygame.quit()
                            return
                        background = load_background_for_level(current_level_index)
                        snake = Snake(sounds, current_level_index)
                        food = Food()
                        game_over = False
                        game_won = False
                        game_over_sound_played = False
                        win_sound_played = False
                        play_background_music()
        
        if not game_over and not game_won:
            game_over = snake.move()
            game_won = snake.game_won
            
            # Проверяем, открылся ли новый уровень
            if snake.new_level_unlocked:
                if show_level_unlocked(screen, snake.unlocked_level_index):
                    snake.new_level_unlocked = False
                else:
                    pygame.quit()
                    return
            
            if game_won and not win_sound_played:
                pygame.mixer.music.stop()
                if sounds.get("win"):
                    sounds["win"].play()
                win_sound_played = True
            
            if not game_won and snake.get_head_position() == food.position:
                snake.grow(food.points)
                food = Food()
                while food.position in snake.positions:
                    food.randomize_position()
            
            # Отрисовка
            draw_puzzle_overlay(screen, snake.revealed_puzzles, background, puzzle_cover, 
                              snake.available_puzzles, game_won)
            draw_grid(screen)
            snake.draw(screen)
            food.draw(screen)
            show_score(screen, snake.score, snake.revealed_puzzles, current_level_index, game_won)
            pygame.display.update()
            
            clock.tick(FPS)
        elif game_won:
            # Показываем экран завершения уровня
            next_level_available = (current_level_index + 1 < len(LEVELS) and 
                                  LEVELS[current_level_index + 1]["unlocked"])
            action = show_level_completed(screen, snake.score, current_level_index, next_level_available)
            
            if action == "next_level":
                # Переходим на следующий уровень
                current_level_index += 1
                background = load_background_for_level(current_level_index)
                snake = Snake(sounds, current_level_index)
                food = Food()
                game_over = False
                game_won = False
                game_over_sound_played = False
                win_sound_played = False
                play_background_music()
            elif action == "menu":
                # Возвращаемся к выбору уровня
                current_level_index = show_level_selection(screen, sounds)
                if current_level_index is None:
                    pygame.quit()
                    return
                background = load_background_for_level(current_level_index)
                snake = Snake(sounds, current_level_index)
                food = Food()
                game_over = False
                game_won = False
                game_over_sound_played = False
                win_sound_played = False
                play_background_music()
            elif action == "restart":
                # Перезапускаем текущий уровень
                snake = Snake(sounds, current_level_index)
                food = Food()
                game_over = False
                game_won = False
                game_over_sound_played = False
                win_sound_played = False
                play_background_music()
            elif action is None:
                pygame.quit()
                return
        else:
            pygame.mixer.music.stop()
            
            if not game_over_sound_played and sounds.get("game_over"):
                sounds["game_over"].play()
                game_over_sound_played = True
            
            # Обработка нажатий на экране game over
            show_game_over(screen, snake.score, snake.revealed_puzzles, background, 
                         puzzle_cover, snake.available_puzzles, current_level_index)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Перезапуск уровня
                        snake = Snake(sounds, current_level_index)
                        food = Food()
                        game_over = False
                        game_won = False
                        game_over_sound_played = False
                        win_sound_played = False
                        play_background_music()
                    elif event.key == pygame.K_ESCAPE:
                        # Возврат к выбору уровня
                        current_level_index = show_level_selection(screen, sounds)
                        if current_level_index is None:
                            pygame.quit()
                            return
                        background = load_background_for_level(current_level_index)
                        snake = Snake(sounds, current_level_index)
                        food = Food()
                        game_over = False
                        game_won = False
                        game_over_sound_played = False
                        win_sound_played = False
                        play_background_music()

if __name__ == "__main__":
    main()