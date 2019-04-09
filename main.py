import pygame, map, engine, sys, physics, globals, math, pymunk, pymunk.pygame_util, maps, title_screen, game_init, finish_screen, items

Map = map.Map

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.font.init()

engine.pygame = pygame

screen = pygame.display.set_mode((1280, 720))
engine.screen = screen
pygame.display.set_icon(globals.ASSETS['STICK_FIGURE_IMG'])

draw_options = pymunk.pygame_util.DrawOptions(screen)

engine.cam.z = -10
engine.back_cam.z = -10
pygame.display.set_caption('Loose Limbs')
pi = math.pi

clock = pygame.time.Clock()
globals.AVAILABLE_ITEMS = [items.RocketLauncher, items.HandHeldBallPit]
# engine.set_map()
# print(engine.cam.x)

# engine.activate_players(4)

# globals.CURRENT_MAP = maps.SSBase()  # maps.SSDepth()
engine.back_cam.y -= 2

# game_init_object = game_init.GameInit()
globals.TITLE_SCREEN = title_screen.TitleScreen()
globals.PHASE = 'title_screen'

globals.FINISH_SCREEN = finish_screen.FinishScreen()


def process_keys(key_state):
    # keyState[pygame.K_x]
    for key in globals.PLAYER_KEY_ASSOCIATION:
        # Key Pressed?
        if key_state[key]:
            globals.PLAYERS[globals.PLAYER_KEY_ASSOCIATION[key]].process_keys(key)


while True:
    # FPS LIMIT = 60
    clock.tick(globals.FPS)

    globals.CURRENT_TIME = pygame.time.get_ticks()

    globals.space.step(globals.TICK)
    keyState = pygame.key.get_pressed()
    engine.screen.fill((255, 255, 255))
    process_keys(keyState)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            globals.IS_MOUSE_DOWN = True
        elif event.type == pygame.MOUSEBUTTONUP:
            globals.IS_MOUSE_DOWN = False

    # globals.CURRENT_MAP.runtime_function()

    if globals.PHASE == 'title_screen':
        globals.TITLE_SCREEN.runtime()
    elif globals.PHASE == 'game':
        # print('ere')
        globals.CURRENT_MAP.runtime_function()

        # Draw All Active Players
        for player in globals.PLAYERS:
            engine.draw_stick_figure(player.sf)

        for item in globals.ACTIVE_ITEMS:
            item.draw()

        for projectile in globals.PROJECTILES:
            projectile.draw()

        # Draw HitBox Map
        engine.draw_hud()
    elif globals.PHASE == 'game_init':
        globals.GAME_INIT_SCREEN.runtime()

    if globals.PHASE_EXTRA == 'finish':
        globals.FINISH_SCREEN.runtime()

    engine.manual_draw()

    # Process Keys:

    # globals.space.debug_draw(draw_options)
    # engine.draw_block_set(engine.render_map.block_list)

    # engine.draw_poly_map(g)
    # globals.space.debug_draw(draw_options)
    pygame.display.flip()

