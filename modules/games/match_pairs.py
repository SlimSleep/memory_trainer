import os
import random
import pygame
import config


class MatchPairsGame:
    """Логика игры "Найди пару" без визуальной реализации."""

    CARD_PADDING = 10
    SPRITE_SURFACES = None

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
        self.start_time = None
        self.finish_time = None
        self.completed = False
        self.locked = False
        self.locked_until = 0
        self.animation_started = pygame.time.get_ticks()
        self.animation_duration = 800
        self.preview_duration = 1500
        self.animation_done = False
        self.previewing = False

        self.card_sprites = self._load_card_sprites()
        self._create_cards()

    def _load_card_sprites(self):
        """Load PNG card sprites from the assets/images folder."""
        if MatchPairsGame.SPRITE_SURFACES is not None:
            return MatchPairsGame.SPRITE_SURFACES

        sprites = []
        if os.path.isdir(config.IMAGES_DIR):
            for filename in sorted(os.listdir(config.IMAGES_DIR)):
                if filename.lower().endswith('.png'):
                    path = os.path.join(config.IMAGES_DIR, filename)
                    try:
                        sprite = pygame.image.load(path).convert_alpha()
                        sprites.append(sprite)
                    except (pygame.error, FileNotFoundError) as e:
                        print(f"⚠ Не удалось загрузить спрайт карточки {path}: {e}")

        MatchPairsGame.SPRITE_SURFACES = sprites
        return sprites

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
        center_x = self.board_rect.centerx
        center_y = self.board_rect.centery

        available_colors = list(config.MATCH_PAIRS_COLORS)
        sprite_indices = list(range(len(self.card_sprites))) if self.card_sprites else [None]
        all_combinations = [
            (sprite_index, color)
            for sprite_index in sprite_indices
            for color in available_colors
        ]
        if len(all_combinations) >= self.pair_count:
            selected_combinations = random.sample(all_combinations, self.pair_count)
        else:
            selected_combinations = all_combinations[:]
            while len(selected_combinations) < self.pair_count:
                selected_combinations.extend(all_combinations)
            random.shuffle(selected_combinations)
            selected_combinations = selected_combinations[:self.pair_count]

        pair_styles = {
            pair_id: selected_combinations[pair_id]
            for pair_id in range(self.pair_count)
        }

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
                start_rect = pygame.Rect(
                    center_x - card_size // 2,
                    center_y - card_size // 2,
                    card_size,
                    card_size
                )
                sprite_surface = None
                sprite_index, card_color = pair_styles[pair_id]
                if sprite_index is not None and self.card_sprites:
                    base_sprite = self.card_sprites[sprite_index]
                    if base_sprite:
                        sprite_surface = pygame.transform.smoothscale(base_sprite, (card_size, card_size))

                self.cards.append({
                    'pair_id': pair_id + 1,
                    'rect': rect,
                    'current_rect': start_rect.copy(),
                    'revealed': False,
                    'matched': False,
                    'color': card_color,
                    'sprite': sprite_surface
                })

    def get_card_index_at(self, pos):
        for index, card in enumerate(self.cards):
            if card['rect'].collidepoint(pos):
                return index
        return None

    def select_card(self, index, current_time):
        if self.completed or self.locked or not self.animation_done or self.previewing:
            return None

        card = self.cards[index]
        if card['revealed'] or card['matched']:
            return None

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
                    self.finish_time = current_time
                    return 'victory'
                return 'match'
            else:
                self.locked = True
                self.locked_until = current_time + 1000
                return 'wrong'
        return None

    def update(self, current_time):
        if not self.animation_done:
            progress = min(1.0, (current_time - self.animation_started) / self.animation_duration)
            center_x = self.board_rect.centerx
            center_y = self.board_rect.centery
            for card in self.cards:
                final = card['rect']
                start_x = center_x - final.width // 2
                start_y = center_y - final.height // 2
                current_x = int(start_x + (final.x - start_x) * progress)
                current_y = int(start_y + (final.y - start_y) * progress)
                card['current_rect'] = pygame.Rect(current_x, current_y, final.width, final.height)
            if progress >= 1.0:
                self.animation_done = True
                self.previewing = True
                self.preview_start_time = current_time
                for card in self.cards:
                    card['revealed'] = True
                    card['current_rect'] = card['rect'].copy()
            return

        if self.previewing:
            if current_time >= self.preview_start_time + self.preview_duration:
                self.previewing = False
                self.start_time = current_time
                for card in self.cards:
                    if not card['matched']:
                        card['revealed'] = False
                        card['current_rect'] = card['rect'].copy()
            return

        if self.locked and current_time >= self.locked_until:
            for index in self.selected_indices:
                self.cards[index]['revealed'] = False
            self.selected_indices = []
            self.locked = False

    def is_completed(self):
        return self.completed

    def get_elapsed_seconds(self, current_time):
        if self.start_time is None:
            return 0
        end_time = self.finish_time if self.finish_time is not None else current_time
        return max(0, (end_time - self.start_time) // 1000)

    def get_score(self):
        return self.matched_pairs * 10

    def get_level(self):
        return self.level
