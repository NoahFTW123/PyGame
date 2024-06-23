import pygame
import requests
import json
import os

# Initialize pygame
pygame.init()

# Constants
WIDTH = 600
HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Initialize the window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Game")

# Font
font = pygame.font.Font(None, 40)

HEART_FULL = pygame.image.load('red_heart.png')
HEART_EMPTY = pygame.image.load('grey_heart.png')
HEART_SIZE = HEART_FULL.get_size()
LIVES_POSITION = (30, 540)

# File to store records
RECORDS_FILE = 'sudoku_records.json'


# Function to load records from the file
def load_records():
    if not os.path.exists(RECORDS_FILE):
        return {'easy': None, 'medium': None, 'hard': None}

    with open(RECORDS_FILE, 'r') as file:
        return json.load(file)


# Function to save records to the file
def save_records(records):
    with open(RECORDS_FILE, 'w') as file:
        json.dump(records, file)


def fetch_random_sudoku(difficulty="easy"):
    url = 'https://sudoku-api.vercel.app/api/dosuku'

    while True:
        try:
            response = requests.get(url)
            print(f"Raw Response: {response.text}")  # Print the raw response text for debugging
            response.raise_for_status()  # Raise an exception for bad responses (like 404)

            sudoku_data = response.json()
            print(f"API Response: {sudoku_data}")  # Print the response to understand its structure

            if ('newboard' in sudoku_data and
                    'grids' in sudoku_data['newboard'] and
                    len(sudoku_data['newboard']['grids']) > 0):
                board = sudoku_data['newboard']['grids'][0]['value']
                solution = sudoku_data['newboard']['grids'][0]['solution']
                fetched_difficulty = sudoku_data['newboard']['grids'][0]['difficulty']
                if fetched_difficulty.lower() == difficulty.lower():
                    return board, solution
                else:
                    print(
                        f"Fetched board difficulty ({fetched_difficulty}) does not match the requested difficulty ({difficulty}). Retrying...")
            else:
                print("Invalid JSON format: 'value' or 'solution' key not found. Retrying...")

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch Sudoku board: {e}. Retrying...")

        except ValueError as e:
            print(f"Failed to parse JSON response: {e}. Retrying...")


# Function to display the difficulty selection screen
def select_difficulty(records):
    window.fill(WHITE)
    title_text = font.render("Select Difficulty", True, BLACK)
    easy_text = font.render("1. Easy", True, BLACK)
    medium_text = font.render("2. Medium", True, BLACK)
    hard_text = font.render("3. Hard", True, BLACK)

    # Get best times from records
    best_time_easy = records.get('easy', None)
    best_time_medium = records.get('medium', None)
    best_time_hard = records.get('hard', None)

    # Render best times text
    best_time_easy_text = font.render(f"Best Time: {format_time(best_time_easy) if best_time_easy else '--:--'}", True,
                                      BLACK)
    best_time_medium_text = font.render(f"Best Time: {format_time(best_time_medium) if best_time_medium else '--:--'}",
                                        True, BLACK)
    best_time_hard_text = font.render(f"Best Time: {format_time(best_time_hard) if best_time_hard else '--:--'}", True,
                                      BLACK)

    draw_hearts(3)

    window.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
    window.blit(easy_text, (WIDTH // 2 - easy_text.get_width() // 2, HEIGHT // 2 - 40))
    window.blit(best_time_easy_text, (WIDTH // 2 + easy_text.get_width() // 2 + 10, HEIGHT // 2 - 40))
    window.blit(medium_text, (WIDTH // 2 - medium_text.get_width() // 2, HEIGHT // 2))
    window.blit(best_time_medium_text, (WIDTH // 2 + medium_text.get_width() // 2 + 10, HEIGHT // 2))
    window.blit(hard_text, (WIDTH // 2 - hard_text.get_width() // 2, HEIGHT // 2 + 40))
    window.blit(best_time_hard_text, (WIDTH // 2 + hard_text.get_width() // 2 + 10, HEIGHT // 2 + 40))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "Easy", best_time_easy
                elif event.key == pygame.K_2:
                    return "Medium", best_time_medium
                elif event.key == pygame.K_3:
                    return "Hard", best_time_hard


# Main loop
def main():
    records = load_records()
    difficulty, best_time = select_difficulty(records)
    if difficulty is None:
        return

    grid, solution = fetch_random_sudoku(difficulty)
    if grid is None or solution is None:
        print("Failed to fetch a valid Sudoku board and solution.")
        return

    start_ticks = pygame.time.get_ticks()  # Start timer when board is loaded
    lives = 3

    selected_cell = None
    while True:
        running = True
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    selected_cell = handle_mouse_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if selected_cell and grid:
                        handle_keypress(event.key, grid, selected_cell, solution, lives)
                        # Check for board completion after each keypress
                        if is_board_complete(grid, solution):
                            running = False  # End the game loop
                        if lives <= 0:
                            print("Game Over!")

            # Calculate elapsed time
            elapsed_seconds = (pygame.time.get_ticks() - start_ticks) // 1000
            elapsed_minutes = elapsed_seconds // 60
            elapsed_seconds = elapsed_seconds % 60
            elapsed_time = f"{elapsed_minutes:02}:{elapsed_seconds:02}"

            # Update display
            draw_grid(grid, selected_cell)
            draw_timer(elapsed_time)
            draw_hearts(lives)
            pygame.display.flip()

        # Game end, check for new record
        total_elapsed_seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        if records[difficulty] is None or total_elapsed_seconds < records[difficulty]:
            records[difficulty] = total_elapsed_seconds
            save_records(records)
            print(f"New record for {difficulty}: {elapsed_time}")

        # Reset grid and solution to fetch a new puzzle
        grid = None
        solution = None

        # Return to difficulty selection
        difficulty, best_time = select_difficulty(records)
        if difficulty is None:
            return

        grid, solution = fetch_random_sudoku(difficulty)
        if grid is None or solution is None:
            print("Failed to fetch a valid Sudoku board and solution.")
            return

        start_ticks = pygame.time.get_ticks()  # Restart timer for new board
        lives = 3
        selected_cell = None


# Function to handle mouse click and return selected cell
def handle_mouse_click(position):
    x, y = position
    if 30 <= x <= 480 and 30 <= y <= 480:
        col = (x - 30) // 50
        row = (y - 30) // 50
        return row, col
    return None


# Function to handle keypress
def handle_keypress(key, grid, selected_cell, solution, lives):
    row, col = selected_cell
    if key == pygame.K_BACKSPACE:
        grid[row][col] = 0
    elif pygame.K_1 <= key <= pygame.K_9:
        num = key - pygame.K_0
        if num == solution[row][col]:
            grid[row][col] = num
        else:
            # Indicate incorrect entry (optional visual feedback)
            grid[row][col] = -num  # Temporarily store negative value to indicate incorrect entry
            lives -= 1  # Lose a life

            if lives <= 0:
                print("Game over!")  # Implement game over logic here

    # Redraw hearts after each key press
    draw_hearts(lives)


# Function to draw the Sudoku grid
def draw_grid(grid, selected_cell):
    window.fill(WHITE)
    # Draw the Sudoku grid lines
    for i in range(10):
        thick = 4 if i % 3 == 0 else 1
        pygame.draw.line(window, BLACK, (30 + i * 50, 30), (30 + i * 50, 480), thick)
        pygame.draw.line(window, BLACK, (30, 30 + i * 50), (480, 30 + i * 50), thick)

    # Highlight the selected cell
    if selected_cell:
        row, col = selected_cell
        pygame.draw.rect(window, BLUE, (30 + col * 50, 30 + row * 50, 50, 50), 3)

    # Fill numbers into grid
    if grid is not None:
        for row in range(9):
            for col in range(9):
                num = grid[row][col]
                if num != 0:
                    if num > 0:
                        text_color = BLACK
                    else:
                        text_color = RED
                        num = -num  # Convert back to positive for display
                    text = font.render(str(num), True, text_color)
                    text_rect = text.get_rect(center=(30 + col * 50 + 25, 30 + row * 50 + 25))
                    window.blit(text, text_rect)
    else:
        # Handle case where grid is None (failed to fetch or invalid response)
        error_text = font.render("Failed to fetch Sudoku board", True, BLACK)
        window.blit(error_text, (WIDTH // 2 - error_text.get_width() // 2, HEIGHT // 2 - error_text.get_height() // 2))


# Function to draw the timer
def draw_timer(elapsed_time):
    timer_text = font.render(f"Time: {elapsed_time}", True, BLACK)
    window.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 500))


def is_board_complete(grid, solution):
    for row in range(9):
        for col in range(9):
            if grid[col][row] == 0 or grid[row][col] != solution[row][col]:
                return False
    return True


def draw_hearts(lives):
    for i in range(3):
        heart_image = HEART_FULL if i < lives else HEART_EMPTY
        window.blit(heart_image, (LIVES_POSITION[0] + i * (HEART_SIZE[0] + 10), LIVES_POSITION[1]))

    pygame.display.flip()


def format_time(seconds):
    if seconds is None:
        return '--:--'
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"


# Run the game
if __name__ == "__main__":
    main()
