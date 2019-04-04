import pymunk
import pygame
import pymunk.pygame_util

# Segment Types & Values
# Create Segments

space = pymunk.Space()
pymunk.pygame_util.positive_y_is_up = False
pygame.init()
pygame.font.init()

FPS = 60
TICK = 1/FPS

ARM_BOOST_FORCE = 1000
CURRENT_MAP = None


class Segment:
    def __init__(self, pos, length, width):
        self.pos = pos
        self.length = length
        self.width = width

        self.body = None
        self.poly = None


class Joint:
    def __init__(self, pos, range):
        self.pos = pos
        self.range = range

        self.pivot_joint = None
        self.rotary_limit_joint = None


SEGMENT_SCALE = 10
FLAME_SCALE = (1/20)
BOOSTER_COLOR = (255, 63, 0)
# SEGMENT_SCALE = 0.1

SEGMENTS = {
    'L_BICEP': Segment(pos=(-1, -1), length=4, width=1),
    'R_BICEP': Segment(pos=(-1, -1), length=4, width=1),
    'L_FOREARM': Segment(pos=(-1, -1), length=4, width=1),
    'R_FOREARM': Segment(pos=(-1, -1), length=4, width=1),
    'TORSO': Segment(pos=(-1, -1), length=1, width=8),
    'L_THIGH': Segment(pos=(-1, -1), length=1, width=4),
    'R_THIGH': Segment(pos=(-1, -1), length=1, width=4),
    'L_CALF': Segment(pos=(-1, -1), length=1, width=4),
    'R_CALF': Segment(pos=(-1, -1), length=1, width=4),
    'NECK': Segment(pos=(-1, -1), length=1, width=1)
}

SEGMENT_MASSES = {
    'L_BICEP': 10,
    'R_BICEP': 10,
    'L_FOREARM': 10,
    'R_FOREARM': 10,
    'TORSO': 10,
    'L_THIGH': 10,
    'R_THIGH': 10,
    'L_CALF': 10,
    'R_CALF': 10,
    'NECK': 10
}

JOINT_PAIRS = {
    'L_SHOULDER': ('L_BICEP', 'TORSO'),
    'R_SHOULDER': ('R_BICEP', 'TORSO'),
    'L_ELBOW': ('L_BICEP', 'L_FOREARM'),
    'R_ELBOW': ('R_BICEP', 'R_FOREARM'),
    'L_HIP': ('L_THIGH', 'TORSO'),
    'R_HIP': ('R_THIGH', 'TORSO'),
    'L_KNEE': ('L_THIGH', 'L_CALF'),
    'R_KNEE': ('R_THIGH', 'R_CALF'),
    'NECK': ('TORSO', 'HEAD')
}

COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255)
}

ASSETS = {
    'STICK_FIGURE_IMG': pygame.image.load('assets/stick_figure.png'),
    'LOOSE_LIMBS': pygame.transform.scale(pygame.image.load('assets/loose_limbs.png'), (400, 400)),
    'GO': pygame.image.load('assets/go.png'),
    'ARROW': pygame.image.load('assets/arrow.png'),
    'player_count_box': pygame.image.load('assets/player_count_box.png'),
    '1': pygame.image.load('assets/1.png'),
    '2': pygame.image.load('assets/2.png'),
    '3': pygame.image.load('assets/3.png'),
    '4': pygame.image.load('assets/4.png')
}

FONTS = {
    'HUD_FONT': pygame.font.SysFont('Arial', 20)
}

PLAYERS = list()
PLAYER_INIT_NUM = 2
# Description: key -> given a pygame keyState Object -> return a player key association
PLAYER_KEY_ASSOCIATION = dict()
ROCKET_LAUNCHER_MASS = 15
MAP_FRICTION = 0.1
PLAYER_FRICTION = 0.1
COLLISION_MOUSE = 1
IS_MOUSE_DOWN = False

ACTIVE_ITEMS = list()
PHASE = ''
MODE = '2D'

print('globals.py Completed Loading')
TITLE_SCREEN = None
GAME_INIT_SCREEN = None