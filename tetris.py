import pygame
import random

pygame.init()

# Screen dimensions
width, height = 300, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tetris")

# Grid settings
cols, rows = 10, 20
cell_size = width // cols

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

# Making the Shapes 2d the ones are the colored in spaces
# example  #### for I shape 
#          s shape   z shape   T shape
# example   ##0        0##      ###
#           0##        ##0      0#0
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
        self.color = colors[random.randint(1, len(colors) - 1)]
        self.x = cols // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

def create_grid(locked_positions={}):
    grid = [[colors[0] for _ in range(cols)] for _ in range(rows)]
    for (x, y), color in locked_positions.items():
        grid[y][x] = color
    return grid

def check_collision(piece, grid):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell and (piece.y + y >= rows or piece.x + x >= cols or piece.x + x < 0 or grid[piece.y + y][piece.x + x] != colors[0]):
                return True
    return False

def add_piece_to_grid(piece, grid, locked_positions):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                locked_positions[(piece.x + x, piece.y + y)] = piece.color
    return locked_positions

def clear_rows(grid, locked_positions):
    rows_cleared = 0
    for y in range(rows - 1, -1, -1):
        if all(grid[y][x] != colors[0] for x in range(cols)):
            rows_cleared += 1
            del_rows = [(x, y) for x in range(cols)]
            for x, y in del_rows:
                if (x, y) in locked_positions:
                    del locked_positions[(x, y)]
            for (x, y) in sorted(locked_positions, key=lambda p: p[1])[::-1]:
                if y < rows:
                    locked_positions[(x, y + rows_cleared)] = locked_positions.pop((x, y))
    return rows_cleared

def draw_grid(screen, grid):
    for y in range(rows):
        for x in range(cols):
            pygame.draw.rect(screen, grid[y][x], (x * cell_size, y * cell_size, cell_size, cell_size), 0)

def draw_piece(screen, piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, piece.color, ((piece.x + x) * cell_size, (piece.y + y) * cell_size, cell_size, cell_size))

def main():
    locked_positions = {}
    grid = create_grid(locked_positions)

    current_piece = Piece(random.choice(shapes))
    clock = pygame.time.Clock()
    fall_time = 0
    level_time = 0
    score = 0
    speed = 500  # Falling speed in milliseconds

    running = True
    while running:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time / 1000 > 10:
            level_time = 0
            if speed > 100:
                speed -= 50

        if fall_time >= speed:
            fall_time = 0
            current_piece.y += 1
            if check_collision(current_piece, grid):
                current_piece.y -= 1
                locked_positions = add_piece_to_grid(current_piece, grid, locked_positions)
                current_piece = Piece(random.choice(shapes))
                rows_cleared = clear_rows(grid, locked_positions)
                score += rows_cleared * 10

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if check_collision(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if check_collision(current_piece, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if check_collision(current_piece, grid):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                    if check_collision(current_piece, grid):
                        current_piece.rotate()
                        current_piece.rotate()
                        current_piece.rotate()

        draw_grid(screen, grid)
        draw_piece(screen, current_piece)
        pygame.display.flip()

    pygame.quit()

main()
