import pygame
import threading
import random
from enum import Enum

# Ustawienia symulacji ################
WIDTH, HEIGHT = 600, 600
CELL_SIZE = 10
num_ants = 5
ants = []
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
STATS_RECT_SIZE = 30
STATS_RECT_MARGIN = 10
#######################################


class Direction(Enum):
    """ Enum odpowiedzialny za kierunek mrowki """
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class Ant(threading.Thread):
    """ Klasa realizujaca funkcjonalnosci mrowki """
    def __init__(self):
        threading.Thread.__init__(self)
        self.x = random.randint(0, grid_width - 1)
        self.y = random.randint(0, grid_height - 1)
        self.direction = random.choice(list(Direction))
        self.running = True
        self.color = colors[i % len(colors)]
        self.start()

    def run(self) -> None:
        """ Wykonanie w osobnym watku """
        while self.running:
            self.move()
            pygame.time.delay(30)

    def move(self) -> None:
        """ Ustawienie mrowki, zmiana koloru pola, interakcja z innymi """
        with screen_lock:    # zabezpieczenie dostepu do zasobow
            if grid[self.y][self.x] == (255, 255, 255):  # Pole biale
                self.direction = Direction((self.direction.value + 1) % len(Direction))
                grid[self.y][self.x] = self.color
            else:    # Pole kolorowe
                self.direction = Direction((self.direction.value - 1) % len(Direction))
                grid[self.y][self.x] = (255, 255, 255)
            self.advance()

            for ant in ants:  # jesli mrowka weszla na pole, gdzie jest inna mrowka to zjada ona mrowke z tamtego pola
                if ant != self and ant.x == self.x and ant.y == self.y:
                    ant.running = False
                    break

    def advance(self) -> None:
        """ Poruszenie mrowki """
        if self.direction == Direction.UP:
            self.y = (self.y - 1) % grid_height
        elif self.direction == Direction.RIGHT:
            self.x = (self.x + 1) % grid_width
        elif self.direction == Direction.DOWN:
            self.y = (self.y + 1) % grid_height
        elif self.direction == Direction.LEFT:
            self.x = (self.x - 1) % grid_width


# Definicja planszy
grid_width = WIDTH // CELL_SIZE
grid_height = HEIGHT // CELL_SIZE
grid = [[(255, 255, 255) for _ in range(grid_width)] for _ in range(grid_height)]

# Ustawienie PyGame
pygame.init()
pygame.display.set_caption("Langton's Ant!")
screen = pygame.display.set_mode((WIDTH, HEIGHT+50))  # Warto zwrocic uwage, ze te dodatkowe 50 tutaj jest na statystyki
clock = pygame.time.Clock()

# Lock do dostepu do zasobow wspoldzielonych
screen_lock = threading.Lock()

# Generowanie mrowek
for i in range(num_ants):
    ant = Ant()
    ants.append(ant)


running = True
while running:
    for event in pygame.event.get():  # Sprawdzenie zakonczenia
        if event.type == pygame.QUIT:
            running = False
            for ant in ants:
                ant.running = False

    # Rysowanie symulacji
    with screen_lock:
        for y, row in enumerate(grid):
            for x, color in enumerate(row):
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Zliczanie statystyk
    color_counts = {}
    for row in grid:
        for color in row:
            if color in color_counts:
                color_counts[color] += 1
            else:
                color_counts[color] = 1

    # Poczatek statystyk
    stats_start_x = (WIDTH - (STATS_RECT_SIZE + STATS_RECT_MARGIN) * len(colors) - STATS_RECT_MARGIN) // 2
    stats_rect_y = HEIGHT + STATS_RECT_MARGIN

    for color, count in color_counts.items():
        # Narysowanie kwadratu
        stats_rect = pygame.Rect(stats_start_x, stats_rect_y, STATS_RECT_SIZE, STATS_RECT_SIZE)
        pygame.draw.rect(screen, color, stats_rect)

        # Tekst w kwadracie
        count_text = pygame.font.SysFont(None, 14).render(str(count), True, (0, 0, 0))
        count_text_rect = count_text.get_rect(center=stats_rect.center)
        screen.blit(count_text, count_text_rect)

        # Ustawienie do rysowania nastepnego kwadratu, wyczyszczenie go (kiedy kolor znika nie zostaje w statystykach)
        stats_start_x += STATS_RECT_SIZE + STATS_RECT_MARGIN
        disapearing_rect = pygame.Rect(stats_start_x, stats_rect_y, STATS_RECT_SIZE, STATS_RECT_SIZE)
        pygame.draw.rect(screen, (0, 0, 0), disapearing_rect)

    # Odswiezenie ekranu
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
