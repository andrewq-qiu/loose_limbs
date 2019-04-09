import engine, globals, pymunk, pygame, physics, math

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.font.init()


class Projectile:
    def draw(self):
        pos = engine.distort_point(self.body.position[0], self.body.position[1], 0)
        pos = (round(pos[0]), round(pos[1]))

        pygame.draw.circle(engine.screen, self.fill_color, pos, self.radius, 0)
        pygame.draw.circle(engine.screen, self.outline_color, pos, self.radius, self.outline_width)

        if self.body.position[1] > 1200:
            self.delete()

    def delete(self):
        globals.space.remove(self.poly, self.body)
        globals.PROJECTILES.remove(self)

    def __init__(self, pos, impulse, angle, mass, radius=10, fill_color=(68, 68, 68)):
        self.pos = pos
        self.impulse = impulse
        self.mass = mass
        self.radius = radius
        self.outline_color = globals.COLORS['BLACK']
        self.outline_width = 2
        self.fill_color = fill_color

        self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass, self.radius, self.radius))
        self.body.position = pos

        self.poly = pymunk.Circle(self.body, self.radius)

        globals.space.add(self.body, self.poly)

        impulse_x = self.impulse * math.cos(angle)
        impulse_y = self.impulse * math.sin(angle)

        self.body.apply_impulse_at_local_point((impulse_x, impulse_y), (0, 0))


class RocketLauncher:
    def draw(self):
        engine.draw_poly(self.poly, self.body, globals.COLORS['BLACK'], (56, 56, 56), 2)

        # Check Collision

    def delete(self):

        self.sf.active_item = None
        self.sf.active_item_type = ''

        globals.space.remove(self.body, self.poly, self.joint)
        globals.ACTIVE_ITEMS.remove(self)

    def fire(self):
        # Generate Rocket
        # print('here')
        # Start Position
        local_start_pos = (self.width / 2 + self.height / 2, 0)
        world_start_pos = self.body.local_to_world(local_start_pos)
        # print(world_start_pos)

        impulse = globals.ROCKET_LAUNCHER_IMPULSE
        impulse_scale = 1 / 10

        globals.PROJECTILES.append(Projectile(world_start_pos, impulse, self.body.angle, 100, 10))

        impulse_x = -impulse * math.cos(self.body.angle) * impulse_scale
        impulse_y = -impulse * math.sin(self.body.angle) * impulse_scale

        self.subject.body.apply_impulse_at_local_point((impulse_x, impulse_y), (self.subject.length, 0))
        globals.SOUNDS['ROCKET_LAUNCHER'].play()

        self.ammo -= 1
        if self.ammo <= 0:
            self.delete()

    def append_to_sf(self, sf):
        # Remove Old Entries from Space
        globals.space.remove(self.body, self.poly)
        subject = sf.segments['R_FOREARM']
        self.sf = sf
        self.subject = subject

        # Reset Body
        self.body = pymunk.Body(globals.ROCKET_LAUNCHER_MASS, pymunk.moment_for_box(globals.ROCKET_LAUNCHER_MASS,
                                                                                    (self.width, self.height)))

        self.vertical_displacement = -10

        # Draw Location
        # Right Hand Location
        x, y = subject.length / 2 + self.height / 2, self.vertical_displacement

        body_pos = subject.body.local_to_world((x, y))

        self.body.position = body_pos
        self.body.angle = math.pi / 2 + subject.body.angle

        self.poly = pymunk.Poly.create_box(self.body, (self.width, self.height), 0)

        anchor_point_subject = [0, 0]
        anchor_point_subject[0] += subject.length / 2

        anchor_point_rl = 0, self.vertical_displacement

        # add joint
        self.joint = pymunk.constraint.PinJoint(self.body, subject.body, anchor_point_rl, anchor_point_subject)

        globals.space.add(self.body, self.poly)
        globals.space.add(self.joint)

        sf.active_item_type = 'rocket_launcher'
        sf.active_item = self

    def hit_player(self, arbiter, space, _):
        player_collision_type = arbiter.shapes[0].collision_type

        player_num = 0

        for i in range(len(globals.COLLISION_ID['PLAYERS'])):
            if globals.COLLISION_ID['PLAYERS'][i] == player_collision_type:
                player_num = i
                break

        # Find player with matching player num
        for player in globals.PLAYERS:
            if player.player_num == player_num:
                if player.sf.active_item == None:
                    self.append_to_sf(player.sf)
                    break

    def __init__(self, x, y):
        self.width, self.height = 70, 10
        # Main Body
        self.body = pymunk.Body(globals.ROCKET_LAUNCHER_MASS, pymunk.moment_for_box(globals.ROCKET_LAUNCHER_MASS,
                                (self.width, self.height)))
        self.body.position = x, y
        self.poly = pymunk.Poly.create_box(self.body, (self.width, self.height), 0)
        self.poly.filter = pymunk.ShapeFilter(categories=globals.COLLISION_TYPE['ITEM'])

        globals.ITEMS_COLLISION_ID_INDEX += 1
        self.poly.collision_type = globals.ITEMS_COLLISION_ID_INDEX

        for i in range(len(globals.PLAYERS)):
            player_collision_id = globals.COLLISION_ID['PLAYERS'][i]
            # print('player_collision', player_collision_id)
            # print('item_collision', globals.ITEMS_COLLISION_ID_INDEX)
            globals.space.add_collision_handler(player_collision_id, globals.ITEMS_COLLISION_ID_INDEX).post_solve = \
                self.hit_player

        self.joint = None
        self.vertical_displacement = 0
        self.ammo = 1
        self.sf = None
        self.subject = None

        globals.space.add(self.body, self.poly)
        globals.ACTIVE_ITEMS.append(self)


class HandHeldBallPit:
    def draw(self):
        engine.draw_poly(self.poly, self.body, globals.COLORS['BLACK'], (29, 255, 0), 2)

    def delete(self):

        self.sf.active_item = None
        self.sf.active_item_type = ''

        globals.space.remove(self.body, self.poly, self.joint)
        globals.ACTIVE_ITEMS.remove(self)

    def fire(self):
        # Generate Rocket
        # print('here')
        # Start Position
        local_start_pos = (self.width / 2 + self.height / 2, 0)
        world_start_pos = self.body.local_to_world(local_start_pos)
        # print(self.ammo)

        impulse = 100
        impulse_scale = 5

        projectile = Projectile(world_start_pos, impulse, self.body.angle, 10, 5, engine.random_color())
        globals.PROJECTILES.append(projectile)

        impulse_x = -impulse * math.cos(self.body.angle) * impulse_scale
        impulse_y = -impulse * math.sin(self.body.angle) * impulse_scale

        self.subject.body.apply_impulse_at_local_point((impulse_x, impulse_y), (self.subject.length, 0))
        globals.SOUNDS['BALL'].play()

        self.ammo -= 1
        if self.ammo <= 0:
            self.delete()


    def append_to_sf(self, sf):
        # Remove Old Entries from Space
        globals.space.remove(self.body, self.poly)
        subject = sf.segments['R_FOREARM']
        self.sf = sf
        self.subject = subject

        # Reset Body
        self.body = pymunk.Body(globals.ROCKET_LAUNCHER_MASS, pymunk.moment_for_box(globals.ROCKET_LAUNCHER_MASS,
                                                                                    (self.width, self.height)))

        self.vertical_displacement = -10

        # Draw Location
        # Right Hand Location
        x, y = subject.length / 2 + self.height / 2, self.vertical_displacement

        body_pos = subject.body.local_to_world((x, y))

        self.body.position = body_pos
        self.body.angle = math.pi / 2 + subject.body.angle

        self.poly = pymunk.Poly.create_box(self.body, (self.width, self.height), 0)

        anchor_point_subject = [0, 0]
        anchor_point_subject[0] += subject.length / 2

        anchor_point_rl = 0, self.vertical_displacement

        # add joint
        self.joint = pymunk.constraint.PinJoint(self.body, subject.body, anchor_point_rl, anchor_point_subject)

        globals.space.add(self.body, self.poly)
        globals.space.add(self.joint)

        sf.active_item_type = 'handheld_ball_pit'
        sf.active_item = self

    def hit_player(self, arbiter, space, _):
        player_collision_type = arbiter.shapes[0].collision_type

        player_num = 0

        for i in range(len(globals.COLLISION_ID['PLAYERS'])):
            if globals.COLLISION_ID['PLAYERS'][i] == player_collision_type:
                player_num = i
                break

        # Find player with matching player num
        for player in globals.PLAYERS:
            if player.player_num == player_num:
                if player.sf.active_item == None:
                    self.append_to_sf(player.sf)
                    break

    def __init__(self, x, y):
        self.width, self.height = 70, 10
        # Main Body
        self.body = pymunk.Body(globals.ROCKET_LAUNCHER_MASS, pymunk.moment_for_box(globals.ROCKET_LAUNCHER_MASS,
                                (self.width, self.height)))
        self.body.position = x, y
        self.poly = pymunk.Poly.create_box(self.body, (self.width, self.height), 0)
        self.poly.filter = pymunk.ShapeFilter(categories=globals.COLLISION_TYPE['ITEM'])

        globals.ITEMS_COLLISION_ID_INDEX += 1
        self.poly.collision_type = globals.ITEMS_COLLISION_ID_INDEX

        for i in range(len(globals.PLAYERS)):
            player_collision_id = globals.COLLISION_ID['PLAYERS'][i]
            # print('player_collision', player_collision_id)
            # print('item_collision', globals.ITEMS_COLLISION_ID_INDEX)
            globals.space.add_collision_handler(player_collision_id, globals.ITEMS_COLLISION_ID_INDEX).post_solve = \
                self.hit_player

        self.joint = None
        self.vertical_displacement = 0
        self.ammo = 1000
        self.sf = None
        self.subject = None

        globals.space.add(self.body, self.poly)
        globals.ACTIVE_ITEMS.append(self)


class PlayerSwitcher:
    def draw(self):
        vertices = self.poly.get_vertices()
        g_vertices = engine.global_vertices(vertices, self.body)

        d_vertices = []
        for v in g_vertices:
            d_vertices.append(engine.distort_point(v[0], v[1], 0))

        engine.draw_poly(self.poly, self.body, globals.COLORS['BLACK'], (29, 255, 0), 2)
        engine.draw_angled_image(self.image, d_vertices, -self.body.angle)

        local_start_pos = (self.width / 2 + self.height / 2, 0)
        world_start_pos = self.body.local_to_world(local_start_pos)

        start_pos = engine.distort_point(world_start_pos[0], world_start_pos[1], 0)

        # print(world_start_pos)

        # Draw HitScan Beam
        angle = self.body.angle
        length = 1000

        end_pos = engine.distort_point(length * math.cos(angle), length * math.sin(angle), 0)
        pygame.draw.line(engine.screen, (0, 255, 237), start_pos, end_pos, 3)

    def delete(self):

        self.sf.active_item = None
        self.sf.active_item_type = ''

        globals.space.remove(self.body, self.poly, self.joint)
        globals.ACTIVE_ITEMS.remove(self)

    def fire(self):
        # Generate Rocket
        # print('here')
        # Start Position
        local_start_pos = (self.width / 2 + self.height / 2, 0)
        world_start_pos = self.body.local_to_world(local_start_pos)
        # print(world_start_pos)

        # Draw HitScan Beam
        angle = self.body.angle
        length = 1000

        end_pos = (length*math.cos(angle), length*math.sin(angle))
        pygame.draw.line(engine.screen, (0, 255, 237), world_start_pos, end_pos, 3)


    def append_to_sf(self, sf):
        # Remove Old Entries from Space
        globals.space.remove(self.body, self.poly)
        subject = sf.segments['R_FOREARM']
        self.sf = sf
        self.subject = subject

        # Reset Body
        self.body = pymunk.Body(globals.ROCKET_LAUNCHER_MASS, pymunk.moment_for_box(globals.ROCKET_LAUNCHER_MASS,
                                                                                    (self.width, self.height)))

        self.vertical_displacement = -20

        # Draw Location
        # Right Hand Location
        x, y = subject.length / 2 + self.height / 2, self.vertical_displacement

        body_pos = subject.body.local_to_world((x, y))

        self.body.position = body_pos
        self.body.angle = subject.body.angle

        self.poly = pymunk.Poly.create_box(self.body, (self.width, self.height), 0)

        anchor_point_subject = [0, 0]
        anchor_point_subject[0] += subject.length / 2

        anchor_point_rl = 0, 0

        # add joint
        self.joint = pymunk.constraint.PinJoint(self.body, subject.body, anchor_point_rl, anchor_point_subject)

        globals.space.add(self.body, self.poly)
        globals.space.add(self.joint)

        sf.active_item_type = 'player_switcher'
        sf.active_item = self

    def hit_player(self, arbiter, space, _):
        player_collision_type = arbiter.shapes[0].collision_type

        player_num = 0

        for i in range(len(globals.COLLISION_ID['PLAYERS'])):
            if globals.COLLISION_ID['PLAYERS'][i] == player_collision_type:
                player_num = i
                break

        # Find player with matching player num
        for player in globals.PLAYERS:
            if player.player_num == player_num:
                self.append_to_sf(player.sf)
                break

    def __init__(self, x, y):
        self.width, self.height = 70, 20
        # Main Body
        self.body = pymunk.Body(globals.ROCKET_LAUNCHER_MASS, pymunk.moment_for_box(globals.ROCKET_LAUNCHER_MASS,
                                (self.width, self.height)))
        self.body.position = x, y
        self.poly = pymunk.Poly.create_box(self.body, (self.width, self.height), 0)
        self.poly.filter = pymunk.ShapeFilter(categories=globals.COLLISION_TYPE['ITEM'])

        globals.ITEMS_COLLISION_ID_INDEX += 1
        self.poly.collision_type = globals.ITEMS_COLLISION_ID_INDEX

        for i in range(len(globals.PLAYERS)):
            player_collision_id = globals.COLLISION_ID['PLAYERS'][i]
            print('player_collision', player_collision_id)
            print('item_collision', globals.ITEMS_COLLISION_ID_INDEX)
            globals.space.add_collision_handler(player_collision_id, globals.ITEMS_COLLISION_ID_INDEX).post_solve = \
                self.hit_player

        self.joint = None
        self.vertical_displacement = 0
        self.ammo = 1
        self.sf = None
        self.subject = None
        self.image = pygame.transform.scale(globals.ASSETS['LASER_GUN'], (self.width, self.height))

        globals.space.add(self.body, self.poly)
        globals.ACTIVE_ITEMS.append(self)
