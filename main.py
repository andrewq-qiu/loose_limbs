import pygame, map, engine, sys, physics, globals, math, pymunk, pymunk.pygame_util, maps

Map = map.Map

pygame.init()

engine.pygame = pygame

screen = pygame.display.set_mode((1280, 720))
engine.screen = screen

draw_options = pymunk.pygame_util.DrawOptions(screen)

engine.cam.z = -10
engine.back_cam.z = -10
pygame.display.set_caption('Smash a0.1')
pi = math.pi

clock = pygame.time.Clock()
# engine.set_map()
print(engine.cam.x)

pygame.font.init()

engine.activate_players(4)

globals.CURRENT_MAP = maps.SSBase()  # maps.SSDepth()
engine.back_cam.y -= 2


def process_keys(key_state):
    # keyState[pygame.K_x]
    for key in globals.PLAYER_KEY_ASSOCIATION:
        # Key Pressed?
        if key_state[key]:
            globals.PLAYERS[globals.PLAYER_KEY_ASSOCIATION[key]].process_keys(key)


while True:
    # FPS LIMIT = 60
    clock.tick(globals.FPS)
    globals.space.step(globals.TICK)
    keyState = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    # screen.fill((255, 255, 255))
    # engine.draw_block(testB)
    globals.CURRENT_MAP.runtime_function()
    # Process Keys:
    process_keys(keyState)
    # globals.space.debug_draw(draw_options)
    # engine.draw_block_set(engine.render_map.block_list)

    # Draw All Active Players
    for player in globals.PLAYERS:
        engine.draw_stick_figure(player.sf)

    # Draw HitBox Map
    engine.draw_hud()
    # engine.draw_poly_map(g)

    pygame.display.flip()

