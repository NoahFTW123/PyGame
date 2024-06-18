import pygame
import requests
import json

# Initialize pygame
pygame.init()

# Constants
WIDTH = 540
HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Initialize the window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Game")

# Font
font = pygame.font.Font(None, 40)


# Fetch random Sudoku board and solution
def fetch_random_sudoku():
    url = 'https://sudoku-api.vercel.app/api/dosuku'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad responses (like 404)
        sudoku_data = response.json()

        # Extract the Sudoku board and solution from the JSON response
        if 'newboard' in sudoku_data and 'grids' in sudoku_data['newboard'] and len(sudoku_data['newboard']['grids']) > 0:
            board = sudoku_data['newboard']['grids'][0]['value']
            solution = sudoku_data['newboard']['grids'][0]['solution']
            return board, solution
        else:
            print("Invalid JSON format: 'value' or 'solution' key not found")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch Sudoku board: {e}")
        return None, None
    except KeyError as e:
        print(f"Invalid JSON format: {e}")
        return None, None


# Main loop
def main():
    grid, solution = fetch_random_sudoku()
    if grid is None or solution is None:
        print("Failed to fetch a valid Sudoku board and solution.")
        return

    selected_cell = None
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                selected_cell = handle_mouse_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if selected_cell and grid:
                    handle_keypress(event.key, grid, selected_cell, solution)

        # Update display
        draw_grid(grid, selected_cell)
        pygame.display.flip()

    pygame.quit()


# Function to handle mouse click and return selected cell
def handle_mouse_click(position):
    x, y = position
    if 30 <= x <= 480 and 30 <= y <= 480:
        col = (x - 30) // 50
        row = (y - 30) // 50
        return row, col
    return None


# Function to handle keypress
def handle_keypress(key, grid, selected_cell, solution):
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


# Run the game
if __name__ == "__main__":
    main()


