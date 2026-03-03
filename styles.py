try:
    from styleOBJ import *
except:
    from .styleOBJ import *

# --- THE SNAKE PIT (1-10) ---
SNAKE = Style('~', '>', '-')
ANACONDA = Style('=', 'O', ' ')
PYTHON = Style('s', 'S', '.')
COBRA = Style('-', 'Z', '_')
VIPER = Style('≈', 'v', '·')
MAMBA = Style('▒', '█', '░')
WORM = Style('o', 'O', ' ')
SIDEWINDER = Style('~', '»', ' ')
RATTLE = Style('=', '§', '-')
NEON_SNAKE = Style('━', '>', ' ')

# --- THE CLASSICS (11-20) ---
BLOCK = Style('█', '█', '░')
SHADE = Style('▓', '▓', '░')
HASH = Style('#', '#', '.')
DOTS = Style('•', '•', ' ')
PLUS = Style('+', '+', '-')
EQUALS = Style('=', '=', ' ')
STARS = Style('*', '*', ' ')
DASH = Style('-', '-', ' ')
PIPE = Style('┃', '┃', '│')
BRICK = Style('■', '■', '□')

# --- GAMER & TECH (21-40) ---
RETRO = Style('▰', '▰', '▱')
PIXEL = Style('■', '□', ' ')
CYBER = Style('⚡', '⚡', '─')
GHOST = Style('👻', '👻', ' ')
HEART = Style('♥', '♥', '♡')
SWORD = Style('═', '⚔️', '─')
SHIELD = Style('🛡️', '🛡️', ' ')
ALIEN = Style('👾', '👾', ' ')
ROCKET = Style('━', '🚀', ' ')
FIRE = Style('🔥', '🔥', ' ')
WATER = Style('🌊', '🌊', ' ')
GALAXY = Style('✧', '✦', ' ')
MATRIX = Style('0', '1', ' ')
BIT = Style('1', '0', ' ')
GLITCH = Style('░', '█', '▒')
LEVEL = Style('▮', '▮', '▯')
XP = Style('▰', '▰', ' ')
HP = Style('█', '█', ' ')
MANA = Style('🔹', '🔹', ' ')
STAMINA = Style('🔸', '🔸', ' ')

# --- ARROWS & FLOW (41-60) ---
FLOW = Style('→', '→', ' ')
DOUBLE_ARROW = Style('»', '»', ' ')
TRIANGLE = Style('▶', '▶', '▷')
DIAMOND = Style('◆', '◆', '◇')
BULLET = Style('➲', '➲', ' ')
POINTER = Style('☞', '☞', ' ')
TARGET = Style('◎', '◎', ' ')
CIRCLE = Style('●', '●', '○')
WAVE = Style('〰', '〰', ' ')
ZAP = Style('⚡', '⚡', ' ')
SPARKLE = Style('✨', '✨', ' ')
BOLT = Style('⇶', '⇶', ' ')
LEAF = Style('🌿', '🌿', ' ')
CLOUD = Style('☁', '☁', ' ')
SNOW = Style('❄', '❄', ' ')
SUN = Style('☀️', '☀️', ' ')
MOON = Style('🌙', '🌙', ' ')
STAR_WARS = Style('=', '>', ' ')
TREK = Style('─', '🖖', ' ')
HALO = Style('━', '😇', ' ')

# --- MINIMALIST (61-80) ---
THIN = Style('─', '─', ' ')
THICK = Style('━', '━', ' ')
DOT_LEADER = Style('.', '.', ' ')
DASH_LEADER = Style('-', '-', ' ')
UNDER = Style('_', '_', ' ')
UPPER = Style('‾', '‾', ' ')
SLASH = Style('/', '/', ' ')
BACKSLASH = Style('\\', '\\', ' ')
X_MARK = Style('x', 'x', ' ')
SQUARE = Style('■', '■', ' ')
TINY = Style('·', '·', ' ')
FAT = Style('█', '█', ' ')
HOLLOW = Style('□', '□', ' ')
FILL = Style('▩', '▩', ' ')
CROSS = Style('†', '†', ' ')
CHECK = Style('✓', '✓', ' ')
INFO = Style('ℹ', 'ℹ', ' ')
WARN = Style('⚠', '⚠', ' ')
ERROR = Style('✘', '✘', ' ')
MUSIC = Style('♪', '♫', ' ')

# --- ABSTRACT & WILD (81-100) ---
BUBBLES = Style('○', '●', ' ')
GEARS = Style('⚙', '⚙', ' ')
TOOLS = Style('🔧', '🔧', ' ')
HAMMER = Style('🔨', '🔨', ' ')
LOCK = Style('🔒', '🔓', ' ')
KEY = Style('🔑', '🔑', ' ')
MAIL = Style('✉', '✉', ' ')
EYE = Style('👁️', '👁️', ' ')
BRAIN = Style('🧠', '🧠', ' ')
DNA = Style('🧬', '🧬', ' ')
ATOM = Style('⚛️', '⚛️', ' ')
SKULL = Style('💀', '💀', ' ')
BONE = Style('🦴', '🦴', ' ')
CROWN = Style('👑', '👑', ' ')
MONEY = Style('💵', '💵', ' ')
GEM = Style('💎', '💎', ' ')
TROPHY = Style('🏆', '🏆', ' ')
MEDAL = Style('🥇', '🥇', ' ')
FLAG = Style('🚩', '🚩', ' ')
DONE = Style('✅', '✅', ' ')
SPIN_CAT = Style(' ', '🐱', ' ') # The cat just floats through the void


# cringe
HEARTBEAT = FunStyle(
    bar_fils=['❤', '💖', '💗', '💓'],
    ends=[' ', '·', ' ', '·'],
    bar_unfils=[' '],
    elapse_pattern=[2.5, 5, 2.5, 25] # Quick pulse, then a long "chill"
)

PULSE = FunStyle(
    bar_fils=[':'],
    ends=['.', '..', '...', '..', '.'], # Scanning movement
    bar_unfils=[' '],
    elapse_pattern=[10, 6, 6, 6, 1]
)

num = FunStyle(
    bar_fils='o i i a'.split(' '),
    ends=[' ', '·', ' ', '·'],
    bar_unfils=[' '],
    elapse_pattern=[4, 2, 2, 6]  # 'o' lingers, 'i-i' is a quick double-tap, 'a' is a long breath
 # Quick pulse, then a long "chill"
)
# The 'end' character cycles through the growth stages
SMOOTH_BLOCK = FunStyle(
    bar_fils=['█'], 
    ends=['▏', '▎', '▍', '▌', '▋', '▊', '▉', '█'],
    bar_unfils=[' '],
    elapse_pattern=[1, 1, 1, 1, 1, 1, 1, 1] 
)





