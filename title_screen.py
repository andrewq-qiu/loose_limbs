import pygame, engine, physics, globals, pymunk, random, copy, math, game_init


class Circle:
    def draw(self):
        x, y = round(self.body.position[0]), round(self.body.position[1])
        pygame.draw.circle(engine.screen, self.color, (x, y), self.radius)
        pygame.draw.circle(engine.screen, globals.COLORS['BLACK'], (x, y), self.radius, 2)

    def __init__(self, x, y, radius=-1, color=(-1, -1, -1)):

        if radius == -1:
            self.radius = random.randint(30, 50)
        else:
            self.radius = radius

        if color == (-1, -1, -1):
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        else:
            self.color = color

        self.body = pymunk.Body(10, pymunk.moment_for_circle(10, self.radius, self.radius))
        self.body.position = x, y
        self.poly = pymunk.Circle(self.body, self.radius)
        self.poly.filter = pymunk.ShapeFilter(categories=199, mask=pymunk.ShapeFilter.ALL_MASKS ^ 198)

        globals.space.add(self.body, self.poly)


class StartBox:
    def draw(self):
        engine.draw_poly_raw(self.poly, self.body, globals.COLORS['BLACK'], self.fill_color, 8)
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
        new_go = pygame.transform.rotate(globals.ASSETS['GO'], angle*180/math.pi)
        # new_go = globals.ASSETS['GO']

        engine.screen.blit(new_go, top_left)

    def __init__(self, size):
        self.body = pymunk.Body(10, pymunk.moment_for_box(10, size))
        self.body.position = 100, 400
        self.poly = pymunk.Poly.create_box(self.body, size, 0)

        self.fill_color = (244, 66, 66)

        globals.space.add(self.body, self.poly)


class TitleScreen:
    @staticmethod
    def finish():
        print('Title_Screen Sequence Complete')
        globals.space.gravity = 0, 400
        physics.space.remove(physics.space.bodies, physics.space.shapes)
        print('Cleared Space...')

        globals.PHASE = 'game_init'
        # Re-Init Game Init
        globals.GAME_INIT_SCREEN = game_init.GameInit()

    def runtime(self):

        # Check For Mouse Collision
        self.mp = pygame.mouse.get_pos()
        # print(self.mp)
        hit = globals.space.point_query_nearest((self.mp[0], self.mp[1]),
                                                10, pymunk.ShapeFilter
                                                (categories=198, mask=pymunk.ShapeFilter.ALL_MASKS ^ 199))
        if hit == None:
            self.start_box.fill_color = (244, 66, 66)
        else:
            self.start_box.fill_color = (0, 255, 237)
            if globals.IS_MOUSE_DOWN:
                self.finish()

        engine.draw_stick_figure_raw(globals.PLAYERS[0].sf)

        for obj in self.objects:
            obj.draw()

        self.start_box.draw()

        engine.screen.blit(globals.ASSETS['LOOSE_LIMBS'], (100, 100))

    def __init__(self):
        globals.MODE = '2D'
        globals.space.gravity = 400, 400
        engine.activate_players(1)
        self.objects = []
        self.mp = (0, 0)

        for i in range(20):
            self.objects.append(Circle(random.randint(500, engine.s_w-100), random.randint(100, engine.s_h-100)))

        # World Boundaries
        bounds = [
            [[0, 0], [engine.s_w, 0]],
            [[engine.s_w, 0], [engine.s_w, engine.s_h]],
            [[engine.s_w, engine.s_h], [0, engine.s_h]],
            [[0, engine.s_h], [0, 0]]
        ]

        self.bound_body = []
        self.bound_poly = []

        for bound in bounds:
            body = pymunk.Body(0, 0, pymunk.Body.STATIC)
            poly = pymunk.Segment(body, bound[0], bound[1], 1)
            poly.filter = pymunk.ShapeFilter(categories=199, mask=pymunk.ShapeFilter.ALL_MASKS ^ 198)

            globals.space.add(body, poly)

            self.bound_body.append(body)
            self.bound_poly.append(poly)

        self.start_box = StartBox((300, 100))
