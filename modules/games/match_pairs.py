import random
import pygame
import config


class MatchPairsGame:
    """Логика игры "Найди пару" без визуальной реализации."""

    CARD_PADDING = 10
    PAIR_COLORS = [
        (255, 179, 186),
        (255, 223, 186),
        (255, 255, 186),
        (186, 255, 201),
        (186, 225, 255),
        (201, 186, 255),
        (255, 186, 255),
        (186, 255, 255),
        (255, 210, 218),
        (210, 255, 214),
    ]

    def __init__(self, level: int = 1, board_rect: pygame.Rect = None):
        self.level = level
        self.level_config = config.MATCH_PAIRS_LEVELS.get(level, config.MATCH_PAIRS_LEVELS[1])
        self.rows = self.level_config['rows']
        self.cols = self.level_config['cols']
        self.total_cards = self.rows * self.cols
        self.pair_count = self.total_cards // 2
        self.board_rect = board_rect or pygame.Rect(
            0,
            120,
            config.WINDOW_WIDTH,
            config.WINDOW_HEIGHT - 180
        )

        self.cards = []
        self.selected_indices = []
        self.matched_pairs = 0
        self.moves = 0
        self.start_time = pygame.time.get_ticks()
        self.completed = False
        self.locked = False
        self.locked_until = 0

        self._create_cards()

    def _create_cards(self):
        deck = [pair_id for pair_id in range(self.pair_count) for _ in range(2)]
        random.shuffle(deck)

        board_width = self.board_rect.width - self.CARD_PADDING * 2
        board_height = self.board_rect.height - self.CARD_PADDING * 2
        card_width = int((board_width - (self.cols - 1) * self.CARD_PADDING) / self.cols)
        card_height = int((board_height - (self.rows - 1) * self.CARD_PADDING) / self.rows)
        card_size = min(card_width, card_height)

        horizontal_margin = self.board_rect.left + (self.board_rect.width - (card_size * self.cols + self.CARD_PADDING * (self.cols - 1))) // 2
        vertical_margin = self.board_rect.top + (self.board_rect.height - (card_size * self.rows + self.CARD_PADDING * (self.rows - 1))) // 2

        self.cards = []
        for row in range(self.rows):
            for col in range(self.cols):
                index = row * self.cols + col
                pair_id = deck[index]
                rect = pygame.Rect(
                    horizontal_margin + col * (card_size + self.CARD_PADDING),
                    vertical_margin + row * (card_size + self.CARD_PADDING),
                    card_size,
                    card_size
                )
                self.cards.append({
                    'pair_id': pair_id + 1,
                    'rect': rect,
                    'revealed': False,
                    'matched': False,
                    'color': self.PAIR_COLORS[pair_id % len(self.PAIR_COLORS)]
                })

    def get_card_index_at(self, pos):
        for index, card in enumerate(self.cards):
            if card['rect'].collidepoint(pos):
                return index
        return None

    def select_card(self, index, current_time):
        if self.completed or self.locked:
            return

        card = self.cards[index]
        if card['revealed'] or card['matched']:
            return

        card['revealed'] = True
        self.selected_indices.append(index)

        if len(self.selected_indices) == 2:
            self.moves += 1
            first, second = self.selected_indices
            first_card = self.cards[first]
            second_card = self.cards[second]
            if first_card['pair_id'] == second_card['pair_id']:
                first_card['matched'] = True
                second_card['matched'] = True
                self.selected_indices = []
                self.matched_pairs += 1
                if self.matched_pairs == self.pair_count:
                    self.completed = True
            else:
                self.locked = True
                self.locked_until = current_time + 1000

    def update(self, current_time):
        if self.locked and current_time >= self.locked_until:
            for index in self.selected_indices:
                self.cards[index]['revealed'] = False
            self.selected_indices = []
            self.locked = False

    def is_completed(self):
        return self.completed

    def get_elapsed_seconds(self, current_time):
        return max(0, (current_time - self.start_time) // 1000)

    def get_score(self):
        return self.matched_pairs * 10

    def get_level(self):
        return self.level
