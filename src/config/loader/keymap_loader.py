from typing import FrozenSet
import pygame


_key_to_pygame = {
    "q": pygame.K_q,
    "w": pygame.K_w,
    "e": pygame.K_e,
    "r": pygame.K_r,
    "t": pygame.K_t,
    "y": pygame.K_y,
    "u": pygame.K_u,
    "i": pygame.K_i,
    "o": pygame.K_o,
    "p": pygame.K_p,

    "a": pygame.K_a,
    "s": pygame.K_s,
    "d": pygame.K_d,
    "f": pygame.K_f,
    "g": pygame.K_g,
    "h": pygame.K_h,
    "j": pygame.K_j,
    "k": pygame.K_k,
    "l": pygame.K_l,

    "z": pygame.K_z,
    "x": pygame.K_x,
    "c": pygame.K_c,
    "v": pygame.K_v,
    "b": pygame.K_b,
    "n": pygame.K_n,
    "m": pygame.K_m,

    "0": pygame.K_0,
    "1": pygame.K_1,
    "2": pygame.K_2,
    "3": pygame.K_3,
    "4": pygame.K_4,
    "5": pygame.K_5,
    "6": pygame.K_6,
    "7": pygame.K_7,
    "8": pygame.K_8,
    "9": pygame.K_9,

    "enter": pygame.K_RETURN,

    "kp_0": pygame.K_KP_0,
    "kp_1": pygame.K_KP_1,
    "kp_2": pygame.K_KP_2,
    "kp_3": pygame.K_KP_3,
    "kp_4": pygame.K_KP_4,
    "kp_5": pygame.K_KP_5,
    "kp_6": pygame.K_KP_6,
    "kp_7": pygame.K_KP_7,
    "kp_8": pygame.K_KP_8,
    "kp_9": pygame.K_KP_9,

    "kp_enter": pygame.K_KP_ENTER,
    "kp_divide": pygame.K_KP_DIVIDE,
    "kp_/": pygame.K_KP_DIVIDE,
    "kp_multiply": pygame.K_KP_MULTIPLY,
    "kp_*": pygame.K_KP_MULTIPLY,
    "kp_minus": pygame.K_KP_MINUS,
    "kp_-": pygame.K_KP_MINUS,
    "kp_plus": pygame.K_KP_PLUS,
    "kp_+": pygame.K_KP_PLUS,
    "kp_period": pygame.K_KP_PERIOD,
    "kp_.": pygame.K_KP_PERIOD,
    "kp_equals": pygame.K_KP_EQUALS,
    "kp_eq": pygame.K_KP_EQUALS,

    "equals": pygame.K_EQUALS,
    "eq": pygame.K_EQUALS,
    "backslash": pygame.K_BACKSLASH,
    "slash": pygame.K_SLASH,
    "minus": pygame.K_MINUS,
    "backquote": pygame.K_BACKQUOTE,
    "backtick": pygame.K_BACKQUOTE,
    "quote": pygame.K_QUOTE,
    "semicolon": pygame.K_SEMICOLON,

    "[": pygame.K_LEFTBRACKET,
    "left_bracket": pygame.K_LEFTBRACKET,
    "]": pygame.K_RIGHTBRACKET,
    "right_bracket": pygame.K_RIGHTBRACKET,

    "backspace": pygame.K_BACKSPACE,
    "erase": pygame.K_BACKSPACE,

    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,

    "space": pygame.K_SPACE,

    "caps": pygame.K_CAPSLOCK,
    "capslock": pygame.K_CAPSLOCK,

    "scroll": pygame.K_SCROLLOCK,
    "scrolllock": pygame.K_SCROLLOCK,
    "scrollock": pygame.K_SCROLLOCK,

    "num": pygame.K_NUMLOCK,
    "numlock": pygame.K_NUMLOCK,

    "tab": pygame.K_TAB,

    "f1": pygame.K_F1,
    "f2": pygame.K_F2,
    "f3": pygame.K_F3,
    "f4": pygame.K_F4,
    "f5": pygame.K_F5,
    "f6": pygame.K_F6,
    "f7": pygame.K_F7,
    "f8": pygame.K_F8,
    "f9": pygame.K_F9,
    "f10": pygame.K_F10,
    "f11": pygame.K_F11,
    "f12": pygame.K_F12,
    "f13": pygame.K_F13,
    "f14": pygame.K_F14,
    "f15": pygame.K_F15,

    "esc": pygame.K_ESCAPE,
    "print": pygame.K_PRINTSCREEN,
    "printscreen": pygame.K_PRINTSCREEN,
    "pause": pygame.K_PAUSE,
    "insert": pygame.K_INSERT,
    "home": pygame.K_HOME,
    "pgup": pygame.K_PAGEUP,
    "pageup": pygame.K_PAGEUP,
    "pgdown": pygame.K_PAGEDOWN,
    "pagedown": pygame.K_PAGEDOWN,
    "delete": pygame.K_DELETE,
    "end": pygame.K_END,

    "lmeta": pygame.K_LMETA,
    "rmeta": pygame.K_RMETA,
    "lalt": pygame.K_LALT,
    "ralt": pygame.K_RALT,
    "lctrl": pygame.K_LCTRL,
    "lshift": pygame.K_LSHIFT,
    "rctrl": pygame.K_RCTRL,
    "rshift": pygame.K_RSHIFT,
}


def load_keymap(map: dict[str, str]) -> dict[FrozenSet[int], str]:
    """
    Assumes a JSON configuration has been parsed into a key-value
    dictionary and the `keymap` section has been passed here.

    vigmykd doesn't allow a key to be bound to multiple actions,
    this is guaranteed by not using any sort of multimap and instead
    resorting to a normal dictionary.

    Arguments:
        map: dict[str, str] - the loaded key-value dictionary

    Returns:
        dict[Set[int], str] - the dictionary with pygame input values as keys
        and normalized action names as values
    """

    result: dict[FrozenSet[int], str] = {}

    for key, action in map.items():
        keys = frozenset(filter(
            None,
            [_key_to_pygame.get(k.lower()) for k in key.split(" ")]
        ))

        result[keys] = action

    return result
