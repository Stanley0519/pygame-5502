from dataclasses import dataclass

import numpy as np
import pygame
import pygame,sys


@dataclass
class Position:
    x: int
    y: int


LEN_SCREEN = 1000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (69,89,171)
GRAY = (30,30,30)
BG_COLOR = (100, 180, 250)

GAME_OVER = "Win the Game"
GAME_OVER_POS = (300, 200)
START_OVER = "Do you want to start over? Y/N"
START_OVER_POS = (250, 300)

DIS_TO_BOUNDARY = 50
LEN_CHESS_SQUARE = 50
CHESS_PIECE_RADIUS = 20

pygame.init()

WHITE_BOARDER_IMG = pygame.image.load("white_boarder.png")
WHITE_BOARDER_IMG = pygame.transform.scale(WHITE_BOARDER_IMG, (LEN_CHESS_SQUARE, LEN_CHESS_SQUARE))

screen = pygame.display.set_mode((LEN_SCREEN, LEN_SCREEN))
font = pygame.font.Font('msjhbd.ttc', 32)
font.set_bold(True)
font.set_italic(True)
def init_game():
    global BOARD_LEN, board_matrix, is_black
    is_black = True
    BOARD_LEN = 15
    board_matrix = np.zeros((BOARD_LEN, BOARD_LEN), dtype=int)


def to_matrix_pos(pos):
    x = (pos[0] - DIS_TO_BOUNDARY) // LEN_CHESS_SQUARE
    y = (pos[1] - DIS_TO_BOUNDARY) // LEN_CHESS_SQUARE
    return Position(x, y)


def make_move(pos, is_black):
    if board_matrix[pos.y][pos.x] == 0:
        board_matrix[pos.y][pos.x] = 1 if is_black else -1
        return True
    return False


def rolling_window_sum(values, window):
    result = []
    for i in range(len(values)-window+1):
        sliced_window = values[i:i+window]
        result.append(sum(sliced_window))
    return result


def check_horizontal_win(matrix_pos):
    x = matrix_pos.x
    row = board_matrix[matrix_pos.y]
    left_end_start = max(0, x - 4)
    left_end_end = min(x, BOARD_LEN - 5)
    for i in range(left_end_start, left_end_end + 1):
        if abs(sum(row[i:i + 5])) == 5:
            return True
    return False


def check_vertical_win(matrix_pos):
    y = matrix_pos.y
    col = board_matrix[:, matrix_pos.x]
    top_end_start = max(0, y - 4)
    top_end_end = min(y, BOARD_LEN - 5)
    for i in range(top_end_start, top_end_end + 1):
        if abs(sum(col[i:i + 5])) == 5:
            return True
    return False


def check_diagonal_win(matrix_pos):
    x, y = matrix_pos.x, matrix_pos.y
    all_values = []
    for i in range(-4, 5):
        if 0 <= x + i < BOARD_LEN and 0 <= y + i < BOARD_LEN:
            # store all values that need to be checked in a list
            all_values.append(board_matrix[y+i, x+i])
    rolling_sum = rolling_window_sum(np.array(all_values), 5)
    if 5 in rolling_sum:
        return True
    all_values = []
    for i in range(-4, 5):
        if 0 <= x + i < BOARD_LEN and 0 <= y - i < BOARD_LEN:
            # store all values that need to be checked in a list
            all_values.append(board_matrix[y - i, x + i])
    rolling_sum = rolling_window_sum(np.array(all_values), 5)
    if 5 in rolling_sum:
        return True

    return False


def check_winner(is_black, matrix_pos):
    if check_horizontal_win(matrix_pos) or check_vertical_win(matrix_pos) or check_diagonal_win(matrix_pos):
        return 1 if is_black else -1
    return 0


def wait_in_ms(time):
    t_cur = pygame.time.get_ticks()
    while pygame.time.get_ticks() - t_cur < time:
        continue


def display_end_game(winner):
    draw_chess_piece()
    game_over = font.render(winner + " " + GAME_OVER, True, BLUE, GRAY)
    screen.blit(game_over, GAME_OVER_POS)
    start_over = font.render(START_OVER, True, BLUE, GRAY)
    screen.blit(start_over, START_OVER_POS)
    pygame.display.update()


def should_restart():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYUP and event.key == pygame.K_y:
                return True
            elif event.type == pygame.KEYUP and event.key == pygame.K_n:
                return False
        wait_in_ms(500)


def matrix_pos_to_screen_pos(row, col):
    return (DIS_TO_BOUNDARY + col * LEN_CHESS_SQUARE + LEN_CHESS_SQUARE / 2,
            DIS_TO_BOUNDARY + row * LEN_CHESS_SQUARE + LEN_CHESS_SQUARE / 2)


def draw_chess_piece():
    for row in range(len(board_matrix)):
        for col in range(len(board_matrix[row])):
            if board_matrix[row][col] == 1:
                pygame.draw.circle(screen, BLACK, matrix_pos_to_screen_pos(row, col), CHESS_PIECE_RADIUS)
            if board_matrix[row][col] == -1:
                pygame.draw.circle(screen, WHITE, matrix_pos_to_screen_pos(row, col), CHESS_PIECE_RADIUS)

def draw_checkerboard():
    for i in range(BOARD_LEN):
        for j in range(BOARD_LEN):
            screen_pos = matrix_pos_to_screen_pos(j,i)
            screen_pos = (screen_pos[0]-LEN_CHESS_SQUARE/2, screen_pos[1]-LEN_CHESS_SQUARE/2)
            screen.blit(WHITE_BOARDER_IMG,screen_pos)

init_game()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            click_pos = pygame.mouse.get_pos()
            if DIS_TO_BOUNDARY <= click_pos[0] <= LEN_SCREEN - DIS_TO_BOUNDARY and DIS_TO_BOUNDARY <= click_pos[
                1] <= LEN_SCREEN - DIS_TO_BOUNDARY:
                matrix_pos = to_matrix_pos(click_pos)
                is_black = not is_black if make_move(matrix_pos, is_black) else is_black
                winner = check_winner(is_black, matrix_pos)
                if winner != 0:
                    display_end_game("??????" if winner == -1 else "??????")
                    # because the color has updated
                    if should_restart():
                        init_game()
                    else:
                        running = False

    screen.fill(BG_COLOR)
    draw_checkerboard()
    draw_chess_piece()
    pygame.display.update()
    
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
                