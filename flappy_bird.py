import pygame
import random
import os
import neat

pygame.init()  # Initialize pygame

WIN_WIDTH = 600  # Window Width
WIN_HEIGHT = 800  # Window Height
FLOOR = 730  # y position of FLOOR
Font = pygame.font.SysFont("comicsans", 50)  # Import font

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))  # Create a Window
pygame.display.set_caption("Flappy Bird")  # Set a window title

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("Assets", "pipe.png")))  # Importing pipe Image

bg_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "bg.png")),
                                (600, 900))  # Importing background Image with (600, 900) pixels

# Loading all bird images as a list of images
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("Assets", "bird1.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("Assets", "bird2.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("Assets", "bird3.png")))]

Ground = pygame.transform.scale2x(pygame.image.load
                                  (os.path.join("Assets", "base.png")))  # Importing Ground Image

gen = 0  # Current Generation Count


class Bird:
    Maximum_Rotation = 25
    Images = bird_images  # References to bird_images
    Rotation_Velocity = 20  # how fast to rotate the bird
    Animation_cycle_time = 5  # Time it take for bird to complete 1 rotation

    def __init__(self, x, y):
        self.x = x  # x coordinate of bird
        self.y = y  # y coordinate of bird
        self.tick_count = 0  # ticks passed
        self.height = self.y  # Height before jump
        self.tilt = 0  # degrees to tilt
        self.vel = 0  # current velocity
        self.img = self.Images[0]  # sets current img
        self.img_count = 0  # current img shown in animation

    def jump(self):
        self.tick_count = 0  # ticks after last jump
        self.height = self.y  # height before jump
        self.vel = -10.5  # jump force

    def move(self):
        self.tick_count += 1  # increase tick count

        # calculate displacement using s = ut + 1/2 at^2  where ut is always 0
        displacement = self.vel * self.tick_count + 0.5 * 3 * self.tick_count ** 2

        # terminal velocity i.e limiting maximum velocity
        if displacement >= 16:
            displacement = (displacement / abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.Maximum_Rotation:
                self.tilt = self.Maximum_Rotation
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.Rotation_Velocity

    def draw(self, win):
        self.img_count += 1

        # For animation of bird, loop through three images
        if self.img_count <= self.Animation_cycle_time:
            self.img = self.Images[0]
        elif self.img_count <= self.Animation_cycle_time * 2:
            self.img = self.Images[1]
        elif self.img_count <= self.Animation_cycle_time * 3:
            self.img = self.Images[2]
        elif self.img_count <= self.Animation_cycle_time * 4:
            self.img = self.Images[1]
        elif self.img_count == self.Animation_cycle_time * 4 + 1:
            self.img = self.Images[0]
            self.img_count = 0

        # if bird is going down it should not flap
        if self.tilt <= -80:
            self.img = self.Images[1]
            self.img_count = self.Animation_cycle_time * 2

        # Rotate bird w.r.t center of bird
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, rect.topleft)

    # get collision mask for bird
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 160
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird, win):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point:
            return True

        return False


class Base:
    VEL = 5
    WIDTH = Ground.get_width()
    IMG = Ground

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    if gen == 0:
        gen = 1
    win.blit(bg_img, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        # draw bird
        bird.draw(win)

    # score
    score_label = Font.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # generations
    score_label = Font.render("Gens: " + str(gen - 1), 1, (255, 255, 255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = Font.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


def main(genomes, config):
    global WIN, gen
    win = WIN
    gen += 1

    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()

    Run = True
    while Run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1

        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.move()

            output = nets[birds.index(bird)].activate(
                (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            # check for collision
            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                genome.fitness -= 5
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))
        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to 50 generations.
    winner = p.run(main, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
