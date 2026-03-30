import pygame
import config

_loaded_sounds = set()
_sfx_volume = config.DEFAULT_SFX_VOLUME_PERCENT / 100
_bg_volume = config.DEFAULT_BG_VOLUME_PERCENT / 100


def init_audio():
    """Initialize the mixer and set sound/music volumes."""
    try:
        pygame.mixer.init()
        print("✓ Pygame mixer инициализирован")
    except pygame.error as e:
        print(f"⚠ Не удалось инициализировать mixer: {e}")
        return
    set_sfx_volume(_sfx_volume)
    set_bg_volume(_bg_volume)
    play_background_music(config.BACKGROUND_MUSIC_PATH)


def set_volume(value):
    """Set both sound effects and background music volume."""
    set_sfx_volume(value)
    set_bg_volume(value)
    return value


def set_sfx_volume(value):
    """Set volume for sound effects."""
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
    """Set volume for background music."""
    global _bg_volume
    _bg_volume = max(0.0, min(1.0, value))
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(_bg_volume)
    return _bg_volume


def get_volume():
    """Return current sound effects volume if used as legacy getter."""
    return _sfx_volume


def get_sfx_volume():
    """Return current sound effects volume."""
    return _sfx_volume


def get_bg_volume():
    """Return current background music volume."""
    return _bg_volume


def play_background_music(path):
    """Load and loop background music."""
    if not path or not pygame.mixer.get_init():
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(_bg_volume)
        pygame.mixer.music.play(-1)
    except (pygame.error, FileNotFoundError) as e:
        print(f"⚠ Ошибка при загрузке фоновой музыки {path}: {e}. Музыка не будет воспроизводиться.")


def load_sound(path):
    """Load a sound and apply the current sound effects volume."""
    if not path:
        return None
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(_sfx_volume)
        _loaded_sounds.add(sound)
        return sound
    except (pygame.error, FileNotFoundError) as e:
        print(f"⚠ Ошибка при загрузке звука {path}: {e}. Звук не будет воспроизводиться.")
        return None
