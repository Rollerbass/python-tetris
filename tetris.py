import pygame
import random

pygame.init()

# Screen settings
width, height = 300, 600
cols, rows = 10, 20
cell_size = width // cols
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tetris")

# Colors
colors = [
    (0, 0, 0),    # Black
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 255, 0),# Yellow
    (0, 255, 255),# Cyan
    (255, 0, 255) # Magenta
]

# Fonts
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 36)

# Tetris shapes
shapes = [
    [[1, 1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]]
]

class Piece:
    def __init__(self, shape):
        self.shape = shape
        self.color = colors[random.randint(1, len(colors)-1)]
        self.x = cols // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

def create_grid(locked_positions):
    grid = [[colors[0] for _ in range(cols)] for _ in range(rows)]
    for (x, y), color in locked_positions.items():
        if y >= 0:
            grid[y][x] = color
    return grid

def check_collision(piece, grid):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = piece.x + x
                new_y = piece.y + y
                if new_x < 0 or new_x >= cols or new_y >= rows or grid[new_y][new_x] != colors[0]:
                    return True
    return False

def add_piece_to_grid(piece, locked_positions):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                locked_positions[(piece.x + x, piece.y + y)] = piece.color

def clear_rows(locked_positions):
    rows_to_clear = []
    for y in range(rows):
        if all((x, y) in locked_positions for x in range(cols)):
            rows_to_clear.append(y)

    if rows_to_clear:
        for y in rows_to_clear:
            for x in range(cols):
                del locked_positions[(x, y)]
        # Shift above rows down
        for y in sorted(rows_to_clear):
            for (x, y_above) in sorted(list(locked_positions), key=lambda k: k[1])[::-1]:
                if y_above < y:
                    color = locked_positions.pop((x, y_above))
                    locked_positions[(x, y_above + 1)] = color
    return len(rows_to_clear)

def draw_grid(screen, grid):
    for y in range(rows):
        for x in range(cols):
            pygame.draw.rect(screen, grid[y][x], (x * cell_size, y * cell_size, cell_size, cell_size), 0)
    for x in range(cols):
        pygame.draw.line(screen, (40, 40, 40), (x * cell_size, 0), (x * cell_size, height))
    for y in range(rows):
        pygame.draw.line(screen, (40, 40, 40), (0, y * cell_size), (width, y * cell_size))

def draw_piece(screen, piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, piece.color,
                                 ((piece.x + x) * cell_size, (piece.y + y) * cell_size, cell_size, cell_size))

def draw_score(screen, score):
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (width // 2 - score_text.get_width() // 2, 10))

def draw_game_over(screen, score):
    screen.fill((0, 0, 0))
    game_over_text = big_font.render("Game Over", True, (255, 0, 0))
    score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
    retry_text = font.render("R = Replay", True, (255, 255, 255))
    exit_text = font.render("ESC = Exit", True, (255, 255, 255))

    screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, 200))
    screen.blit(score_text, (width // 2 - score_text.get_width() // 2, 250))
    screen.blit(retry_text, (width // 2 - retry_text.get_width() // 2, 300))
    screen.blit(exit_text, (width // 2 - exit_text.get_width() // 2, 330))
    pygame.display.flip()

def run_game():
    locked_positions = {}
    current_piece = Piece(random.choice(shapes))
    clock = pygame.time.Clock()
    fall_time = 0
    level_time = 0
    score = 0
    speed = 500
    paused = False
    game_over = False

    while True:
        delta = clock.tick()
        fall_time += delta
        level_time += delta

        if game_over:
            draw_game_over(screen, score)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return run_game()
                    elif event.key == pygame.K_ESCAPE:
                        return
            continue

        if paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN and (event.key == pygame.K_p or event.key == pygame.K_SPACE):
                    paused = False
            screen.fill((0, 0, 0))
            pause_text = font.render("Paused (P / Space)", True, (255, 255, 255))
            screen.blit(pause_text, (width // 2 - pause_text.get_width() // 2, height // 2))
            pygame.display.flip()
            continue

        if level_time / 1000 > 10:
            level_time = 0
            if speed > 100:
                speed -= 50

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if check_collision(current_piece, create_grid(locked_positions)):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if check_collision(current_piece, create_grid(locked_positions)):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if check_collision(current_piece, create_grid(locked_positions)):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    old_shape = current_piece.shape
                    current_piece.rotate()
                    if check_collision(current_piece, create_grid(locked_positions)):
                        current_piece.shape = old_shape
                elif event.key == pygame.K_p or event.key == pygame.K_SPACE:
                    paused = True

        if fall_time >= speed:
            fall_time = 0
            current_piece.y += 1
            if check_collision(current_piece, create_grid(locked_positions)):
                current_piece.y -= 1
                add_piece_to_grid(current_piece, locked_positions)
                score += clear_rows(locked_positions) * 10
                current_piece = Piece(random.choice(shapes))
                if check_collision(current_piece, create_grid(locked_positions)):
                    game_over = True

        grid = create_grid(locked_positions)
        screen.fill((0, 0, 0))
        draw_grid(screen, grid)
        draw_piece(screen, current_piece)
        draw_score(screen, score)
        pygame.display.flip()

run_game()
pygame.quit()
