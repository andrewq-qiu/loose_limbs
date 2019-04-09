import engine, globals, physics, pygame, pymunk, random, copy, math, game_init, time

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.font.init()


class Ball:
    def draw(self):
        pos = self.body.position
        pos = round(pos[0]), round(pos[1])

        pygame.draw.circle(engine.screen, self.color, pos, self.radius, 0)
        pygame.draw.circle(engine.screen, globals.COLORS['BLACK'], pos, self.radius, 2)

    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = engine.random_color()

        self.body = pymunk.Body(0.01, pymunk.moment_for_circle(0.01, radius, radius))
        self.body.position = x, y
        self.poly = pymunk.Circle(self.body, radius)
        self.poly.filter = pymunk.ShapeFilter(categories=0x10000000)

        globals.space.add(self.body, self.poly)


class StartBox:
    def draw(self, mp, root):
        mask_num = pymunk.ShapeFilter.ALL_MASKS ^ 0x10000000
        for ct in globals.COLLISION_TYPE['PLAYERS']:
            mask_num = mask_num ^ ct

        hit_go = globals.space.point_query_nearest((mp[0], mp[1]), 10,
                                                     pymunk.ShapeFilter(
                                                         mask=mask_num
                                                     ))

        if (not self.last_hit_state) and hit_go != None:
            self.fill_color = (0, 255, 237)
            globals.SOUNDS['MOUSE_CLICK'].play()
            self.last_hit_state = True
        elif self.last_hit_state and hit_go == None:
            self.fill_color = (244, 66, 66)
            self.last_hit_state = False

        if hit_go != None:
            if globals.IS_MOUSE_DOWN:
                root.finish()

        engine.draw_poly_raw(self.poly, self.body, globals.COLORS['BLACK'], self.fill_color, 4)
        # Top Left V Location
        vertices = self.poly.get_vertices()
        g_vertices = engine.global_vertices(vertices, self.body)

        smallest_x = 9999
        smallest_y = 9999

        # Most Left (x) Most Up (y)
        for v in g_vertices:
            if v[0] < smallest_x:
                smallest_x = v[0]
            if v[1] < smallest_y:
                smallest_y = v[1]

        top_left = (smallest_x, smallest_y)

        angle = -self.body.angle

        # print(angle)
        new_go = pygame.transform.rotate(self.image_asset, angle*180/math.pi)
        # new_go = globals.ASSETS['GO']

        engine.screen.blit(new_go, top_left)

    def __init__(self, size):
        self.body = pymunk.Body(10, pymunk.moment_for_box(10, size))
        self.body.position = 600, 0
        self.poly = pymunk.Poly.create_box(self.body, size, 0)
        self.poly.filter = pymunk.ShapeFilter(categories=0x01000000)
        self.image_asset = pygame.transform.scale(globals.ASSETS['GO'], size)
        self.last_hit_state = False

        self.fill_color = (244, 66, 66)

        globals.space.add(self.body, self.poly)
        # self.body.apply_impulse_at_local_point((100, 100), (0, 0))


class BallPit:
    def draw(self):

        for ball in self.balls:
            ball.draw()
        for bound in self.bounds:
            pygame.draw.line(engine.screen, globals.COLORS['BLACK'], bound[0], bound[1], 2)

        mp = pygame.mouse.get_pos()

        self.start_box.draw(mp, self)

    @staticmethod
    def finish():
        engine.clear_players()
        globals.PHASE = 'game_init'
        globals.PHASE_EXTRA = ''
        # Re-Init Game Init
        engine.reset_template_players()
        globals.GAME_INIT_SCREEN = game_init.GameInit()

        # pygame.mixer.music.stop()
        # time.sleep(1)

    def __init__(self):
        self.bounds = [
            [[engine.s_w / 4, engine.s_h / 4], [engine.s_w / 4, engine.s_h * 3 / 4]],
            [[engine.s_w / 4, engine.s_h * 3 / 4], [engine.s_w * 3 / 4, engine.s_h * 3 / 4]],
            [[engine.s_w * 3 / 4, engine.s_h * 3 / 4], [engine.s_w * 3 / 4, engine.s_h / 4]]
        ]

        self.bound_body = []
        self.bound_poly = []
        self.start_box = StartBox((150, 50))

        for bound in self.bounds:
            body = pymunk.Body(0, 0, pymunk.Body.STATIC)
            poly = pymunk.Segment(body, bound[0], bound[1], 1)
            poly.filter = pymunk.ShapeFilter(categories=0x10000000)

            self.bound_body.append(body)
            self.bound_poly.append(poly)

            globals.space.add(body, poly)

        self.balls = []
        for i in range(200):
            x = random.randint(round(self.bounds[0][0][0]), round(self.bounds[2][0][0]))
            y = random.randint(round(self.bounds[0][0][1]), round(self.bounds[0][1][1]))

            radius = 10
            ball = Ball(x, y, radius)

            self.balls.append(ball)


class FinishScreen:
    def game_title(self):
        index = self.tick - 1
        current_image = self.game_images[index]

        w, h = current_image.get_size()
        x = round((engine.s_w - w) / 2)
        y = round((engine.s_h - h) / 2)

        # Draw Image
        engine.screen.blit(current_image, (x, y))

    def runtime(self):
        self.tick += 1

        if self.tick <= self.game_title_time:
            self.game_title()
        elif self.tick == self.game_title_time + 1:
            engine.clear_players()
            # print('here at runtime')
            self.ball_pit = BallPit()
            globals.TICK = 1/globals.FPS
            # print(globals.TICK)
            globals.PHASE = ''

            self.last_player = engine.TEMPLATE_PLAYERS[globals.LAST_PLAYER]
            self.last_player.sf = \
                physics.StickFigure(engine.s_w/2, 300, self.last_player.sf.color, self.last_player.player_num)

            pygame.mixer.music.load(globals.MUSIC['VICTORY'])
            pygame.mixer.music.play()

            globals.PROJECTILES = list()
            globals.ACTIVE_ITEMS = list()


        else:
            self.ball_pit.draw()
            engine.draw_stick_figure_raw(self.last_player.sf)

    def __init__(self):
        self.game_start_scale = 0.70
        self.game_end_scale = 0.60
        self.game_asset = globals.ASSETS['GAME']
        self.ball_pit = None
        self.last_player = None

        w, h = self.game_asset.get_size()
        # Scale Image
        self.game_asset = \
            pygame.transform.scale(
                self.game_asset, (round(w * self.game_start_scale), round(h * self.game_start_scale)))

        self.tick = 0
        self.game_title_time = 100

        self.game_scale_step = (self.game_end_scale - self.game_start_scale) / self.game_title_time
        self.game_images = []

        w, h = self.game_asset.get_size()
        self.game_frozen_time = 20
        for i in range(self.game_title_time - self.game_frozen_time):
            tick = i

            current_scale = self.game_start_scale + self.game_scale_step * tick
            game_image = \
                pygame.transform.scale(
                    self.game_asset, (round(w * current_scale), round(h * current_scale)))

            self.game_images.append(game_image)

        for i in range(self.game_frozen_time):
            self.game_images.append(self.game_images[self.game_title_time - self.game_frozen_time - 1])



