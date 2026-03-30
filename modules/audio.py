import pygame
import config

_loaded_sounds = set()
_volume = config.DEFAULT_AUDIO_VOLUME


def init_audio():
    """Initialize the mixer and set the current volume."""
    try:
        pygame.mixer.init()
        print("✓ Pygame mixer инициализирован")
    except pygame.error as e:
        print(f"⚠ Не удалось инициализировать mixer: {e}")
    set_volume(_volume)


def set_volume(value):
    """Set global audio volume for sound effects and music."""
    global _volume
    _volume = max(0.0, min(1.0, value))
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(_volume)
        for sound in list(_loaded_sounds):
            try:
                sound.set_volume(_volume)
            except pygame.error:
                pass
    return _volume


def get_volume():
    """Return current global volume value (0.0-1.0)."""
    return _volume


def load_sound(path):
    """Load a sound and apply the current global volume."""
    if not path:
        return None
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(_volume)
        _loaded_sounds.add(sound)
        return sound
    except (pygame.error, FileNotFoundError) as e:
        print(f"⚠ Ошибка при загрузке звука {path}: {e}. Звук не будет воспроизводиться.")
        return None
