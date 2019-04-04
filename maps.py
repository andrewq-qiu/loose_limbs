import engine, pymunk, globals, physics

# MAPS:


class SSDepth:
    def init_function(self):
        # Creation of Space
        depth = 10
        number_of_columns = 15

        # Two Separate Box Types: Render, Physics Engine -> which are similar but are not the same
        phys_block_length = 100
        render_block_length = 1
        block_outline_color = (238, 0, 255)

        for a in range(number_of_columns):
            for b in range(depth):
                # Y CONSTANT @ 0
                self.block_list.append(engine.Block(a*render_block_length, 0, b*render_block_length,
                                                    render_block_length, render_block_length, block_outline_color))

            body = pymunk.Body(0, 0, pymunk.Body.STATIC)
            body.position = a * phys_block_length, 0
            poly = pymunk.Poly.create_box(body, (phys_block_length, phys_block_length), 0)
            globals.space.add(body, poly)

            self.body.append(body)
            self.poly.append(poly)

        # Adjust Camera
        engine.back_cam.z = -10
        engine.cam.z = -10

        y_position = -3

        engine.cam.y = y_position * phys_block_length
        engine.back_cam.y = y_position * render_block_length

        engine.cam.x = (number_of_columns/2 - 1/2) * phys_block_length
        engine.back_cam.x = (number_of_columns/2 - 1/2) * render_block_length

        self.spawn_locations = [
            [200, -300],
            [0, -300]
        ]

        for i in range(len(globals.PLAYERS)):
            x = self.spawn_locations[i][0]
            y = self.spawn_locations[i][1]

            globals.PLAYERS[i].sf = \
                physics.StickFigure(x, y, globals.PLAYERS[i].sf.color, globals.PLAYERS[i].player_num)

    def runtime_function(self):
        engine.screen.fill((0, 0, 0))
        # Render Map
        engine.draw_block_set(self.block_list)
        # engine.draw_poly_map(self)

    def __init__(self):
        self.body = list()
        self.poly = list()
        self.block_list = list()
        self.spawn_locations = list()
        # self.outline_color = (238, 0, 255)
        # self.outline_width = 3
        # self.fill_color = (255, 255, 255)
        self.init_function()


class SSBase:
    def startup(self):
        if self.startup_tick > 0:
            self.startup_tick += 1
            # print(self.startup_tick)
            if self.startup_tick % self.spawn_time == 0:
                m = round(self.startup_tick / self.spawn_time)
                if m == globals.PLAYER_INIT_NUM - 1:
                    self.startup_tick = 0
                    # globals.space.gravity = 0, 400
                    globals.TICK = 1 / globals.FPS

                engine.add_player()

                # Update Player
                player = globals.PLAYERS[m]
                player.pos = self.spawn_locations[m]

                player.sf = \
                    physics.StickFigure(player.pos[0], player.pos[1], player.sf.color, player.player_num)

    def init_function(self):
        # globals.space.gravity = 0, 0
        globals.TICK = 0
        # STOP TIME
        globals.MODE = '3D'
        self.startup_tick = 1
        engine.clear_players()
        engine.add_player()

        # Symmetrical
        self.symmetry_vertices = [
            [0, 2.7],
            [1, 2.6],
            [1.5, 2.2],
            [2, 2],
            [2.4, 1.8],
            [3.0, 1.0],
            [4.6, 0.6],
            [6, 0]
        ]

        self.base_vertices = list()
        reflection = list()
        # This must end up as counter-clockwise
        for i in range(len(self.symmetry_vertices)):
            if self.symmetry_vertices[i][0] != 0:
                reflection.append([-self.symmetry_vertices[i][0], self.symmetry_vertices[i][1]])

        reflection = reflection[::-1]
        self.base_vertices = reflection + self.symmetry_vertices
        # print('base_vertices', self.base_vertices)

        # Create Depth Object
        self.depth_object = engine.DepthObject(self.base_vertices, 2, (-1, -1, -1), (0, 0, 0), 3)

        # HitBox Creation (Physics Engine)
        # Vertices Expanded By A Factor of 100
        self.physics_vertices = list()
        for i in range(len(self.base_vertices)):
            self.physics_vertices.append([self.base_vertices[i][0] * 100, self.base_vertices[i][1] * 100])
        # print(self.physics_vertices)

        # Static Body
        self.body = pymunk.Body(0, 0, pymunk.Body.STATIC)
        self.body.position = 0, 0
        self.poly = pymunk.Poly(self.body, self.physics_vertices, None, 0)
        self.poly.friction = globals.MAP_FRICTION

        globals.space.add(self.body, self.poly)

        # Adjust Camera
        y_position = 0
        engine.back_cam.y = y_position * 1
        engine.cam.y = y_position * 100 - 2 * 100

        # Moving Platforms
        self.platform = engine.Platform(150, -200, 300, 10, 1)

        self.spawn_locations = [
            [-300, -400],
            [100, -500],
            [200, -500],
            [400, -300]
        ]

        self.elimination_bounds = [
            -1500,  # MIN X
            1500,  # MAX X
            -1200,  # MIN Y
            1200,  # MAX Y
        ]

        player = globals.PLAYERS[len(globals.PLAYERS) - 1]
        player.pos = self.spawn_locations[len(globals.PLAYERS) - 1]

        player.sf = \
            physics.StickFigure(player.pos[0], player.pos[1], player.sf.color, player.player_num)

    def __init__(self):
        self.body = None
        self.poly = list()
        self.objects = list()
        self.spawn_locations = list()
        self.platform = None
        self.startup_tick = 0
        self.spawn_time = 10
        self.elimination_bounds = list()

        self.physics_vertices = list()
        self.base_vertices = list()
        self.symmetry_vertices = list()
        self.depth_object = None

        self.init_function()

    @staticmethod
    def reset_player(player):
        player.lives -= 1
        player.sf.remove_self_from_space()
        if player.lives > 0:
            player.sf = physics.StickFigure(player.pos[0], player.pos[1], player.color, player.player_num)
        else:
            print('PLAYER ' + str(player.lives) + ' HAS LOST ALL LIVES')

    def runtime_function(self):
        # engine.screen.fill((255, 255, 255))
        self.depth_object.draw()
        self.platform.draw()
        self.startup()

        # Adjust Camera To Match Average of Stick Figures
        sum_x = 0
        sum_y = 0

        min_x = 0
        max_x = 0
        min_y = 0
        max_y = 0

        for player in globals.PLAYERS:
            if player.lives > 0:
                # Selected Point: Center of Torso
                seg = player.sf.segments['TORSO']
                p = seg.body.position

                sum_x += p[0]
                sum_y += p[1]

                if p[0] < min_x:
                    min_x = p[0]
                if p[0] > max_x:
                    max_x = p[0]
                if p[1] < min_y:
                    min_y = p[1]
                if p[1] > max_y:
                    max_y = p[1]

                # Eliminated ?
                if p[0] < self.elimination_bounds[0]:
                    print('PLAYER ' + str(player.player_num) + ' ELIMINATED LEFT BOUND')
                    self.reset_player(player)

                elif p[0] > self.elimination_bounds[1]:
                    print('PLAYER ' + str(player.player_num) + ' ELIMINATED RIGHT BOUND')
                    self.reset_player(player)

                elif p[1] < self.elimination_bounds[2]:
                    print('PLAYER ' + str(player.player_num) + ' ELIMINATED UP BOUND')
                    self.reset_player(player)

                elif p[1] > self.elimination_bounds[3]:
                    print('PLAYER ' + str(player.player_num) + ' ELIMINATED DOWN BOUND')
                    self.reset_player(player)

        # BOUNDS = (min_x, max_x, min_y, max_y)
        padding = 1000
        bounds = (min_x - padding, max_x + padding, min_y - padding, max_y + padding)
        anchor = 3
        a_xy = (sum_x/(len(globals.PLAYERS) + anchor), sum_y/(len(globals.PLAYERS) + anchor))

        b_x = max(abs(bounds[0] - a_xy[0]), abs(bounds[1] - a_xy[0]))
        zd_x = (a_xy[0] - engine.s_w/2)/b_x
        z_x = engine.s_w/(200 * zd_x)

        b_y = max(abs(bounds[2] - a_xy[1]), abs(bounds[3] - a_xy[1]))
        zd_y = (a_xy[1] - engine.s_h/2)/b_y
        z_y = engine.s_w/(200 * zd_y)

        max_z = max(z_x, z_y, 10)
        final_z = min(max_z, 30)
        engine.cam.z = -final_z
        engine.back_cam.z = -final_z

        # Move Camera x, y
        engine.cam.x = a_xy[0]
        engine.cam.y = a_xy[1]

        engine.back_cam.x = ((a_xy[0])/100) * 1
        engine.back_cam.y = ((a_xy[1]) / 100) * 1





