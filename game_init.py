import engine, pymunk, pygame, globals, maps, math

button_hash = {
    'player_count_l': 0x10000000,
    'player_count_r': 0x01000000,
    'go_button': 0x00100000
}


class SandBox:
    def draw(self):
        for seg in self.segment_coordinates:
            pygame.draw.line(engine.screen, globals.COLORS['BLACK'], seg[0], seg[1], self.outline_thickness)

    def __init__(self):
        self.padding = 50
        padding = self.padding

        self.top_end = 1/4 * engine.s_h
        top_end = self.top_end

        self.bottom_end = 3/4 * engine.s_h
        bottom_end = self.bottom_end

        self.segment_coordinates = [
            [[padding, padding], [engine.s_w/2, padding]],
            [[engine.s_w/2, padding], [engine.s_w/2, top_end]],
            [[engine.s_w/2, top_end], [engine.s_w-padding, top_end]],
            [[engine.s_w - padding, top_end], [engine.s_w - padding, engine.s_h - padding]],
            [[engine.s_w - padding, engine.s_h - padding], [engine.s_w/2, engine.s_h - padding]],
            [[engine.s_w/2, engine.s_h - padding], [engine.s_w/2, bottom_end]],
            [[engine.s_w/2, bottom_end], [padding, bottom_end]],
            [[padding, bottom_end], [padding, padding]]
        ]

        self.body = []
        self.poly = []
        self.outline_thickness = 3

        for seg in self.segment_coordinates:
            body = pymunk.Body(0, 0, pymunk.Body.STATIC)
            poly = pymunk.Segment(body, seg[0], seg[1], 1)
            poly.filter = pymunk.ShapeFilter(categories=0x00000001)
            self.body.append(body)
            self.poly.append(poly)
            # print(body)
            globals.space.add(body, poly)


class Button:
    def draw(self):
        x, y = self.body.position
        engine.screen.blit(self.image_asset, (x, y))

        v = engine.global_vertices(self.poly.get_vertices(), self.body)
        pygame.draw.polygon(engine.screen, (0, 0, 0), v, 2)

    def __init__(self, x, y, button_size, button_id, reverse=False):
        self.body = pymunk.Body(0, 0, pymunk.Body.STATIC)
        self.body.position = x, y

        self.button_size = button_size
        self.image_asset = pygame.transform.scale(globals.ASSETS['ARROW'], (self.button_size, self.button_size))
        if reverse:
            self.image_asset = pygame.transform.flip(self.image_asset, True, False)

        # Centered Around Body

        vertices = []
        if reverse:
            vertices = [
                [self.button_size, 0],
                [0, self.button_size / 2],
                [self.button_size, self.button_size]
            ]
        else:
            vertices = [
                [0, 0],
                [0, self.button_size],
                [self.button_size, self.button_size / 2]
            ]

        self.poly = pymunk.Poly(self.body, vertices, None, 0)
        self.poly.filter = pymunk.ShapeFilter(categories=button_hash[button_id])
        globals.space.add(self.body, self.poly)
        # print(button_id)


class PlayerCounter:
    def draw(self, mp, root):

        # Step Click Time
        if self.click_time_current > 0:
            if self.click_time_current >= self.click_time_complete:
                self.click_time_current = 0
            else:
                self.click_time_current += 1

        # Hitting Left Button ?
        hit_left = globals.space.point_query_nearest((mp[0], mp[1]), 10,
                                                     pymunk.ShapeFilter(
                                                         mask=pymunk.ShapeFilter.ALL_MASKS
                                                              ^ button_hash['player_count_l']
                                                              ^ 0x00000001
                                                              ^ button_hash['go_button']
                                                     ))

        hit_right = globals.space.point_query_nearest((mp[0], mp[1]), 10, pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS
                                                                                                  ^ button_hash['player_count_r']
                                                                                                  ^ 0x00000001
                                                                                                  ^ button_hash['go_button']
                                                                                             ))

        if hit_left != None:
            if globals.IS_MOUSE_DOWN and self.click_time_current == 0:
                if self.player_count - 1 >= self.min_player_count:
                    self.player_count -= 1
                    globals.PLAYER_INIT_NUM = self.player_count
                    self.click_time_current = 1
                    engine.remove_player()

        if hit_right != None:
            if globals.IS_MOUSE_DOWN and self.click_time_current == 0:
                if self.player_count + 1 <= self.max_player_count:
                    self.player_count += 1
                    globals.PLAYER_INIT_NUM = self.player_count
                    self.click_time_current = 1
                    engine.add_player()

        for button in self.buttons:
            button.draw()

        # Draw Box Region
        x, y = self.body.position
        x -= self.width/2
        y -= self.height/2

        engine.screen.blit(self.image_asset, (x, y))

        n_x = x + self.width / 2 - self.number_asset_size / 2
        n_y = y + ((self.height - self.number_asset_size) / 2)

        # Draw Numbers
        engine.screen.blit(self.number_assets[self.player_count], (n_x, n_y))

    def __init__(self, x, y, height):
        self.player_count = 2
        globals.PLAYER_INIT_NUM = self.player_count
        self.min_player_count = 2
        self.max_player_count = 4
        self.click_time_complete = 10
        self.click_time_current = 0

        # Player Count Buttons
        bd_x = engine.s_w * (1 / 20)
        bd_y = height / 2

        self.buttons = [
            Button(x + bd_x, y - bd_y, height, 'player_count_l'),
            Button(x - bd_x - height, y - bd_y, height, 'player_count_r', True)
        ]

        asset_w = globals.ASSETS['player_count_box'].get_width()
        asset_h = globals.ASSETS['player_count_box'].get_height()

        self.width = round(height * (asset_w / asset_h))
        self.height = height

        self.body = pymunk.Body(0, 0, pymunk.Body.STATIC)
        self.body.position = x, y
        self.poly = pymunk.Poly.create_box(self.body, (self.width, self.height), 0)
        self.poly.filter = pymunk.ShapeFilter(categories=0x00000001)
        globals.space.add(self.body, self.poly)
        # print(globals.space.bodies)

        self.image_asset = pygame.transform.scale(globals.ASSETS['player_count_box'], (self.width, self.height))
        self.number_assets = {}
        # Number Asset Scale Factor
        self.number_assets_scale_factor = 7/8
        self.number_asset_size = round(self.number_assets_scale_factor * height)

        for i in range(1, self.max_player_count + 1):
            number_asset = pygame.transform.scale(
                globals.ASSETS[str(i)], (self.number_asset_size, self.number_asset_size))

            self.number_assets[i] = number_asset


class StartBox:
    def draw(self, mp, root):
        hit_go = globals.space.point_query_nearest((mp[0], mp[1]), 10,
                                                     pymunk.ShapeFilter(
                                                         mask=pymunk.ShapeFilter.ALL_MASKS ^
                                                              button_hash['player_count_l']
                                                              ^ 0x00000001
                                                              ^ button_hash['player_count_r']
                                                     ))

        if hit_go != None:
            self.fill_color = (0, 255, 237)
            if globals.IS_MOUSE_DOWN:
                root.finish()
        else:
            self.fill_color = (244, 66, 66)

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
        self.body.position = 300, 400
        self.poly = pymunk.Poly.create_box(self.body, size, 0)
        self.poly.filter = pymunk.ShapeFilter(categories=button_hash['go_button'])
        self.image_asset = pygame.transform.scale(globals.ASSETS['GO'], size)

        self.fill_color = (244, 66, 66)

        globals.space.add(self.body, self.poly)
        # self.body.apply_impulse_at_local_point((100, 100), (0, 0))


class GameInit:
    @staticmethod
    def finish():
        globals.PHASE = 'game'
        globals.space.remove(globals.space.bodies, globals.space.shapes)
        # engine.activate_players(globals.PLAYER_INIT_NUM)
        globals.CURRENT_MAP = maps.SSBase()

    def runtime(self):

        self.sandbox.draw()
        for player in globals.PLAYERS:
            engine.draw_stick_figure_raw(player.sf)

        # Get Mouse Position
        mp = pygame.mouse.get_pos()

        for obj in self.physics_objects:
            obj.draw(mp, self)

    def __init__(self):
        globals.MODE = '2D'
        engine.activate_players(2)
        self.sandbox = SandBox()
        self.physics_objects = []
        # Add Buttons

        c_x = engine.s_w * (1 / 4)
        c_y = (((engine.s_h - self.sandbox.padding) + self.sandbox.bottom_end) / 2)
        # Player Count Screen
        self.physics_objects.append(PlayerCounter(c_x, c_y, 50))
        self.physics_objects.append(StartBox((150, 50)))
        print(globals.space.bodies)



