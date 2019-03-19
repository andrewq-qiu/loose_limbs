import pygame, math, sys
pygame.init()
screen = pygame.display.set_mode((1280, 720))


class Point:
    def __init__(self, pos, vel, force):
        self.pos = pos
        self.vel = vel
        self.force = force


def init_points(arr):
    to_return = []
    for i in range(len(arr)):
        to_return.append(Point(arr[i], [0, 0], [0, 0]))

    return to_return


class Body:
    def __init__(self, x, y, points, segments, scale, spring_constant, color, damp, mass):

        self.raw_points = points
        self.points = []

        # Erase Later
        y = y - (1 + octo_y) * scale

        for i in range(0, len(points)):
            n_x = points[i].pos[0]*scale + x
            n_y = points[i].pos[1]*scale + y

            self.points.append(Point([n_x, n_y], [0, 0], [0, 0]))

        self.segments = segments
        self.baseSegmentLength = []
        self.baseDisplacement = []

        for segment in self.segments:
            d_x = self.points[segment[0]].pos[0] - self.points[segment[1]].pos[0]
            d_y = self.points[segment[0]].pos[1] - self.points[segment[1]].pos[1]

            self.baseDisplacement.append([abs(d_x), abs(d_y)])
            self.baseSegmentLength.append(d_x*d_x + d_y*d_y)
        self.spring_constant = spring_constant
        self.color = color
        self.damp = damp
        self.mass = mass

        self.relevantSegment = {}
        for i in range(len(self.segments)):
            segment = self.segments[i]
            if segment[0] not in self.relevantSegment.keys():
                self.relevantSegment[segment[0]] = [i]
            else:
                self.relevantSegment[segment[0]].append(i)
            if segment[1] not in self.relevantSegment.keys():
                self.relevantSegment[segment[1]] = [i]
            else:
                self.relevantSegment[segment[1]].append(i)


octo_y = 2/math.sqrt(2)

ball = Body(1280/2, 720/2,
            init_points([[-1, 0], [1, 0], [1 + octo_y, octo_y], [1 + octo_y, 2 + octo_y], [1, 2 + 2*octo_y],
                        [-1, 2 + 2*octo_y], [-1 - octo_y, 2 + octo_y], [-1 - octo_y, octo_y]]),
            [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 0]],
            40,
            0.0001,
            (0, 0, 0),
            0.85,
            1
            )


def render_body(b):
    for segment in b.segments:
        pygame.draw.line(screen, b.color, b.points[segment[0]].pos, b.points[segment[1]].pos, 5)


bodies = [ball]
g = 0


def calculate_physics():
    global g

    for body in bodies:
        for i in range(len(body.points)):
            point = body.points[i]

            # Update Points Based On Velocity of Each
            pos = point.pos
            vel = point.vel

            pos[0] += vel[0]
            pos[1] += vel[1]

            # Calculate Force:
            point.force = [0, body.mass * g]
            force = point.force

            # NOTE FOR FUTURE CHANGE: ITERATE BY SEGMENTS AND NOT POINTS AFTER  !!!!

            # Spring Forces
            r_s = body.relevantSegment[i]
            for segment in r_s:
                o_length = body.baseSegmentLength[segment]
                p1 = body.points[body.segments[segment][0]].pos
                p2 = body.points[body.segments[segment][1]].pos

                d_x = abs(p1[0] - p2[0])
                d_y = abs(p1[1] - p2[1])

                o_x = body.baseDisplacement[segment][0]
                o_y = body.baseDisplacement[segment][1]

                f_x = (d_x - o_x) * body.spring_constant
                f_y = (d_y - o_y) * body.spring_constant

                force[0] += f_x
                force[1] += f_y
                print(force)

            # Update Velocity based on Force of each
            acc = [force[0] / body.mass, force[1] / body.mass]
            vel[0] += acc[0]
            vel[1] += acc[1]

            # Damping Effect on Velocity
            body.vel = [vel[0] * body.damp, vel[1] * body.damp]


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
           sys.exit('Closed Game')

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        print('LEFT KEY PRESSED')
        ball.points[0].pos[0] -= 0.1
    elif keys[pygame.K_RIGHT]:
        ball.points[0].pos[0] += 0.1


    screen.fill((255, 255, 255))
    calculate_physics()
    render_body(ball)

    pygame.display.flip()


