import pygame
import config
import math
import numpy as np

_loaded_sounds = set()
_sfx_volume = config.DEFAULT_SFX_VOLUME_PERCENT / 100
_bg_volume = config.DEFAULT_BG_VOLUME_PERCENT / 100

# Фортепианные ноты (до, ре, ми, фа)
PIANO_NOTES = {
    0: {'name': 'C4', 'freq': 261.63},
    1: {'name': 'D4', 'freq': 293.66},
    2: {'name': 'E4', 'freq': 329.63},
    3: {'name': 'F4', 'freq': 349.23},
}

_piano_sounds = {}


def init_audio():
    """Initialize the mixer and set sound/music volumes."""
    try:
        pygame.mixer.init(frequency=44100)
        print("✓ Pygame mixer инициализирован")
    except pygame.error as e:
        print(f"⚠ Не удалось инициализировать mixer: {e}")
        return
    set_sfx_volume(_sfx_volume)
    set_bg_volume(_bg_volume)
    play_background_music(config.BACKGROUND_MUSIC_PATH)


def generate_piano_note(frequency: float, duration_ms: int = 600, volume: float = 0.3) -> pygame.mixer.Sound:
    """Генерирует фортепианную ноту с гармониками."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration_ms / 1000)
    
    t = np.linspace(0, duration_ms / 1000, n_samples, False)
    
    # Основной тон + гармоники
    wave = np.sin(2 * np.pi * frequency * t)
    wave += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
    wave += 0.15 * np.sin(2 * np.pi * frequency * 3 * t)
    wave += 0.08 * np.sin(2 * np.pi * frequency * 4 * t)
    wave = wave / 1.53
    
    # Огибающая ADSR
    attack_ms = 3
    decay_ms = 100
    sustain_level = 0.35
    release_ms = 400
    
    attack_samples = int(sample_rate * attack_ms / 1000)
    decay_samples = int(sample_rate * decay_ms / 1000)
    release_samples = int(sample_rate * release_ms / 1000)
    sustain_samples = n_samples - attack_samples - decay_samples - release_samples
    
    envelope = np.ones(n_samples)
    pos = 0
    
    if attack_samples > 0:
        envelope[pos:pos+attack_samples] = np.linspace(0, 1, attack_samples)
        pos += attack_samples
    
    if decay_samples > 0:
        decay_curve = 1 - (1 - sustain_level) * np.linspace(0, 1, decay_samples)
        envelope[pos:pos+decay_samples] = decay_curve
        pos += decay_samples
    
    if sustain_samples > 0:
        envelope[pos:pos+sustain_samples] = sustain_level
        pos += sustain_samples
    
    if release_samples > 0 and pos < n_samples:
        release_curve = sustain_level * np.exp(-np.linspace(0, 5, n_samples - pos))
        envelope[pos:n_samples] = release_curve
    
    wave = wave * envelope * volume
    
    # Конвертация в 16-bit PCM
    wave_int16 = (wave * 32767).astype(np.int16)
    
    # Стерео
    stereo = np.zeros((n_samples, 2), dtype=np.int16)
    stereo[:, 0] = wave_int16
    stereo[:, 1] = wave_int16
    
    return pygame.sndarray.make_sound(stereo)


def get_piano_sound(button_index: int) -> pygame.mixer.Sound:
    """Возвращает звук фортепианной ноты для кнопки."""
    if button_index not in _piano_sounds:
        freq = PIANO_NOTES[button_index]['freq']
        _piano_sounds[button_index] = generate_piano_note(freq, duration_ms=600, volume=0.3)
    return _piano_sounds[button_index]


def play_piano_note(button_index: int):
    """Воспроизводит фортепианную ноту."""
    sound = get_piano_sound(button_index)
    sound.set_volume(_sfx_volume)
    sound.play()


def play_note(button_index: int):
    """Алиас для play_piano_note."""
    play_piano_note(button_index)


def set_volume(value):
    set_sfx_volume(value)
    set_bg_volume(value)
    return value


def set_sfx_volume(value):
    global _sfx_volume
    _sfx_volume = max(0.0, min(1.0, value))
    if pygame.mixer.get_init():
        for sound in list(_loaded_sounds):
            try:
                sound.set_volume(_sfx_volume)
            except pygame.error:
                pass
    return _sfx_volume


def set_bg_volume(value):
    global _bg_volume
    _bg_volume = max(0.0, min(1.0, value))
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(_bg_volume)
    return _bg_volume


def get_volume():
    return _sfx_volume


def get_sfx_volume():
    return _sfx_volume


def get_bg_volume():
    return _bg_volume


def play_background_music(path):
    if not path or not pygame.mixer.get_init():
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(_bg_volume)
        pygame.mixer.music.play(-1)
    except (pygame.error, FileNotFoundError) as e:
        print(f"⚠ Ошибка при загрузке фоновой музыки {path}: {e}")


def load_sound(path):
    if not path:
        return None
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(_sfx_volume)
        _loaded_sounds.add(sound)
        return sound
    except (pygame.error, FileNotFoundError) as e:
        print(f"⚠ Ошибка при загрузке звука {path}: {e}")
        return None
