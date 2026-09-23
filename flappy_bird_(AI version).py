import pickle
from pathlib import Path
import random

import pygame
import neat
import visualize


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "imgs"

# Network diagrams will be stored here
NETWORK_DIR = BASE_DIR / "networks"
NETWORK_DIR.mkdir(exist_ok=True)


# ============================================================
# INITIALIZE PYGAME
# ============================================================

pygame.init()


# ============================================================
# SCREEN SETTINGS
# ============================================================

SCREEN_WIDTH = 864
SCREEN_HEIGHT = 936

GROUND_Y = 768

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption(
    "Flappy Bird - NEAT AI"
)

clock = pygame.time.Clock()

FPS = 60


# ============================================================
# GAME SETTINGS
# ============================================================

SCROLL_SPEED = 4

PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds

GRAVITY = 0.5
MAX_FALL_SPEED = 8
JUMP_VELOCITY = -10

# Maximum frames a generation can run
MAX_FRAMES = 3000

# Number of generations
GENERATIONS = 100


# ============================================================
# FITNESS SETTINGS
# ============================================================

# Every frame survived
SURVIVAL_REWARD = 1.0

# Every pipe successfully passed
PIPE_REWARD = 10.0

# Penalty when bird dies
DEATH_PENALTY = 5.0


# ============================================================
# COLORS
# ============================================================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# ============================================================
# FONT
# ============================================================

font = pygame.font.SysFont(
    "Bauhaus 93",
    36
)


# ============================================================
# LOAD IMAGES
# ============================================================

BG_IMAGE = pygame.image.load(
    IMG_DIR / "bg.png"
).convert()

GROUND_IMAGE = pygame.image.load(
    IMG_DIR / "ground.png"
).convert_alpha()

PIPE_IMAGE = pygame.image.load(
    IMG_DIR / "pipe.png"
).convert_alpha()


# ============================================================
# GLOBAL TRAINING VARIABLES
# ============================================================

generation = 0

pipe_pair_id = 0

last_pipe = 0


# ============================================================
# BIRD CLASS
# ============================================================

class Bird:

    def __init__(self, x, y):

        # ----------------------------------------------------
        # Load animation images
        # ----------------------------------------------------

        self.images = []

        for number in range(1, 4):

            image = pygame.image.load(
                IMG_DIR / f"bird{number}.png"
            ).convert_alpha()

            self.images.append(image)

        # ----------------------------------------------------
        # Animation variables
        # ----------------------------------------------------

        self.index = 0
        self.counter = 0
        self.animation_speed = 5

        self.image = self.images[self.index]

        self.rect = self.image.get_rect()

        self.rect.center = (
            x,
            y
        )

        # ----------------------------------------------------
        # Physics
        # ----------------------------------------------------

        self.vel = 0

    # --------------------------------------------------------
    # RESET
    # --------------------------------------------------------

    def reset(self, x, y):

        self.rect.center = (
            x,
            y
        )

        self.vel = 0

        self.index = 0
        self.counter = 0

        self.image = self.images[self.index]

    # --------------------------------------------------------
    # JUMP
    # --------------------------------------------------------

    def jump(self):

        self.vel = JUMP_VELOCITY

    # --------------------------------------------------------
    # MOVE
    # --------------------------------------------------------

    def move(self):

        self.vel += GRAVITY

        if self.vel > MAX_FALL_SPEED:

            self.vel = MAX_FALL_SPEED

        self.rect.y += int(self.vel)

    # --------------------------------------------------------
    # ANIMATE
    # --------------------------------------------------------

    def animate(self):

        self.counter += 1

        if self.counter > self.animation_speed:

            self.counter = 0

            self.index += 1

            if self.index >= len(self.images):

                self.index = 0

        rotation = self.vel * -2

        self.image = pygame.transform.rotate(
            self.images[self.index],
            rotation
        )


# ============================================================
# PIPE CLASS
# ============================================================

class Pipe(pygame.sprite.Sprite):

    def __init__(
        self,
        x,
        gap_center,
        position,
        pair_id
    ):

        super().__init__()

        self.original_image = PIPE_IMAGE

        self.image = self.original_image.copy()

        self.rect = self.image.get_rect()

        self.gap_center = gap_center

        self.pair_id = pair_id

        # True = top pipe
        # False = bottom pipe
        self.is_top = position == 1

        # ----------------------------------------------------
        # TOP PIPE
        # ----------------------------------------------------

        if position == 1:

            self.image = pygame.transform.flip(
                self.original_image,
                False,
                True
            )

            self.rect.bottomleft = (
                x,
                gap_center - PIPE_GAP // 2
            )

        # ----------------------------------------------------
        # BOTTOM PIPE
        # ----------------------------------------------------

        else:

            self.rect.topleft = (
                x,
                gap_center + PIPE_GAP // 2
            )

    # --------------------------------------------------------
    # UPDATE PIPE
    # --------------------------------------------------------

    def update(self):

        self.rect.x -= SCROLL_SPEED

        if self.rect.right < 0:

            self.kill()


# ============================================================
# PIPE GROUP
# ============================================================

pipe_group = pygame.sprite.Group()


# ============================================================
# CREATE A NEW PIPE PAIR
# ============================================================

def create_pipe():

    global pipe_pair_id
    global last_pipe

    pipe_pair_id += 1

    # Random vertical offset
    pipe_offset = random.randint(
        -100,
        100
    )

    gap_center = (
        SCREEN_HEIGHT // 2
        + pipe_offset
    )

    # Bottom pipe
    bottom_pipe = Pipe(
        SCREEN_WIDTH,
        gap_center,
        -1,
        pipe_pair_id
    )

    # Top pipe
    top_pipe = Pipe(
        SCREEN_WIDTH,
        gap_center,
        1,
        pipe_pair_id
    )

    pipe_group.add(
        bottom_pipe,
        top_pipe
    )

    last_pipe = pygame.time.get_ticks()


# ============================================================
# FIND NEXT PIPE
# ============================================================

def get_next_pipe(bird):

    top_pipes = [
        pipe
        for pipe in pipe_group.sprites()
        if pipe.is_top
        and pipe.rect.right >= bird.rect.left
    ]

    if not top_pipes:

        return None

    return min(
        top_pipes,
        key=lambda pipe: pipe.rect.x
    )


# ============================================================
# AI STATE
# ============================================================

def get_ai_state(
    bird,
    next_pipe
):

    # --------------------------------------------------------
    # Input 1
    # Bird Y position
    #
    # Normalized roughly to -1 ... +1
    # --------------------------------------------------------

    bird_y = (
        bird.rect.centery
        - SCREEN_HEIGHT / 2
    ) / (
        SCREEN_HEIGHT / 2
    )

    # --------------------------------------------------------
    # Input 2
    # Bird vertical velocity
    # --------------------------------------------------------

    bird_velocity = (
        bird.vel
        / MAX_FALL_SPEED
    )

    # --------------------------------------------------------
    # Input 3
    # Horizontal distance to pipe
    # --------------------------------------------------------

    horizontal_distance = (
        next_pipe.rect.centerx
        - bird.rect.centerx
    ) / SCREEN_WIDTH

    # --------------------------------------------------------
    # Input 4
    # Vertical distance between bird
    # and center of pipe gap
    # --------------------------------------------------------

    vertical_distance = (
        next_pipe.gap_center
        - bird.rect.centery
    ) / SCREEN_HEIGHT

    return [
        bird_y,
        bird_velocity,
        horizontal_distance,
        vertical_distance
    ]


# ============================================================
# RESET ENVIRONMENT
# ============================================================

def reset_environment():

    global pipe_pair_id
    global last_pipe

    pipe_group.empty()

    pipe_pair_id = 0

    last_pipe = (
        pygame.time.get_ticks()
        - PIPE_FREQUENCY
    )

    # Create first pipe
    create_pipe()


# ============================================================
# DRAW TEXT
# ============================================================

def draw_text(
    text,
    x,
    y,
    size=36
):

    text_font = pygame.font.SysFont(
        "Bauhaus 93",
        size
    )

    image = text_font.render(
        str(text),
        True,
        WHITE
    )

    screen.blit(
        image,
        (x, y)
    )


# ============================================================
# COLLISION CHECK
# ============================================================

def bird_collides(bird):

    # --------------------------------------------------------
    # Ceiling
    # --------------------------------------------------------

    if bird.rect.top <= 0:

        return True

    # --------------------------------------------------------
    # Ground
    # --------------------------------------------------------

    if bird.rect.bottom >= GROUND_Y:

        return True

    # --------------------------------------------------------
    # Pipes
    # --------------------------------------------------------

    for pipe in pipe_group.sprites():

        if bird.rect.colliderect(
            pipe.rect
        ):

            return True

    return False


# ============================================================
# SAVE NETWORK VISUALIZATION
# ============================================================

def save_generation_network(
    config,
    genome,
    current_generation
):

    filename = (
        NETWORK_DIR
        / f"generation_{current_generation:03d}"
    )

    try:

        visualize.draw_net(
            config,
            genome,
            view=False,
            filename=str(filename),
            node_names={
                -1: "Bird Y",
                -2: "Velocity",
                -3: "Pipe Distance",
                -4: "Gap Distance",
                0: "FLAP"
            },
            show_disabled=False,
            prune_unused=True
        )

        print(
            f"Network saved: "
            f"{filename}.svg"
        )

    except Exception as error:

        print(
            "\nWARNING: Could not generate "
            "network visualization."
        )

        print(
            f"Reason: {error}"
        )

        print(
            "Training will continue."
        )

        print(
            "Make sure Graphviz 'dot' is "
            "installed and available in PATH.\n"
        )


# ============================================================
# EVALUATE GENOMES
# ============================================================

def eval_genomes(
    genomes,
    config
):

    global generation

    generation += 1

    print(
        f"\nGeneration {generation}"
    )

    # --------------------------------------------------------
    # Reset environment
    # --------------------------------------------------------

    reset_environment()

    # --------------------------------------------------------
    # Create neural-network agents
    # --------------------------------------------------------

    agents = []

    for genome_id, genome in genomes:

        # Reset fitness
        genome.fitness = 0.0

        # Build neural network
        network = neat.nn.FeedForwardNetwork.create(
            genome,
            config
        )

        # Create bird
        bird = Bird(
            100,
            SCREEN_HEIGHT // 2
        )

        agents.append(
            {
                "genome_id": genome_id,
                "genome": genome,
                "network": network,
                "bird": bird,
                "passed_pipes": set()
            }
        )

    # --------------------------------------------------------
    # Generation simulation
    # --------------------------------------------------------

    frame_count = 0

    while (
        len(agents) > 0
        and frame_count < MAX_FRAMES
    ):

        frame_count += 1

        # ====================================================
        # EVENTS
        # ====================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()

                raise SystemExit

        # ====================================================
        # CREATE PIPES
        # ====================================================

        current_time = pygame.time.get_ticks()

        if (
            current_time - last_pipe
            > PIPE_FREQUENCY
        ):

            create_pipe()

        # ====================================================
        # AI DECISIONS
        # ====================================================

        for agent in agents:

            bird = agent["bird"]
            genome = agent["genome"]
            network = agent["network"]

            # ------------------------------------------------
            # Find next pipe
            # ------------------------------------------------

            next_pipe = get_next_pipe(
                bird
            )

            if next_pipe is not None:

                # ------------------------------------------------
                # Get neural-network inputs
                # ------------------------------------------------

                state = get_ai_state(
                    bird,
                    next_pipe
                )

                # ------------------------------------------------
                # Neural-network prediction
                # ------------------------------------------------

                output = network.activate(
                    state
                )[0]

                # ------------------------------------------------
                # AI ACTION
                # ------------------------------------------------

                if output > 0.5:

                    bird.jump()

            # ------------------------------------------------
            # Bird physics
            # ------------------------------------------------

            bird.move()

            bird.animate()

            # ------------------------------------------------
            # Survival reward
            # ------------------------------------------------

            genome.fitness += SURVIVAL_REWARD

        # ====================================================
        # MOVE PIPES
        # ====================================================

        pipe_group.update()

        # ====================================================
        # CHECK EACH BIRD
        # ====================================================

        dead_agents = []

        top_pipes = [
            pipe
            for pipe in pipe_group.sprites()
            if pipe.is_top
        ]

        for agent in agents:

            bird = agent["bird"]
            genome = agent["genome"]
            passed_pipes = agent[
                "passed_pipes"
            ]

            # ------------------------------------------------
            # Reward passing a pipe
            # ------------------------------------------------

            for pipe in top_pipes:

                if (
                    pipe.pair_id
                    not in passed_pipes
                ):

                    if (
                        bird.rect.left
                        > pipe.rect.right
                    ):

                        genome.fitness += (
                            PIPE_REWARD
                        )

                        passed_pipes.add(
                            pipe.pair_id
                        )

            # ------------------------------------------------
            # Collision
            # ------------------------------------------------

            if bird_collides(bird):

                genome.fitness -= (
                    DEATH_PENALTY
                )

                dead_agents.append(
                    agent
                )

        # ====================================================
        # REMOVE DEAD BIRDS
        # ====================================================

        for agent in dead_agents:

            if agent in agents:

                agents.remove(agent)

        # ====================================================
        # DRAW BACKGROUND
        # ====================================================

        screen.blit(
            BG_IMAGE,
            (0, 0)
        )

        # ====================================================
        # DRAW PIPES
        # ====================================================

        pipe_group.draw(
            screen
        )

        # ====================================================
        # DRAW BIRDS
        # ====================================================

        for agent in agents:

            screen.blit(
                agent["bird"].image,
                agent["bird"].rect
            )

        # ====================================================
        # DRAW GROUND
        # ====================================================

        screen.blit(
            GROUND_IMAGE,
            (0, GROUND_Y)
        )

        # ====================================================
        # FIND BEST CURRENT FITNESS
        # ====================================================

        best_current_fitness = max(
            genome.fitness
            for _, genome in genomes
        )

        # ====================================================
        # HUD
        # ====================================================

        draw_text(
            f"Generation: {generation}",
            20,
            20,
            32
        )

        draw_text(
            f"Alive: {len(agents)}",
            20,
            55,
            32
        )

        draw_text(
            f"Best Fitness: "
            f"{best_current_fitness:.1f}",
            20,
            90,
            32
        )

        draw_text(
            f"Frame: {frame_count}",
            20,
            125,
            32
        )

        # ====================================================
        # UPDATE SCREEN
        # ====================================================

        pygame.display.update()

        clock.tick(FPS)

    # ========================================================
    # GENERATION FINISHED
    # ========================================================

    # Find best genome of this generation
    best_genome_id, best_genome = max(
        genomes,
        key=lambda item: item[1].fitness
    )

    best_fitness = best_genome.fitness

    # --------------------------------------------------------
    # Console output
    # --------------------------------------------------------

    print(
        f"Generation {generation} finished | "
        f"Best fitness: {best_fitness:.2f}"
    )

    # --------------------------------------------------------
    # Save best network from this generation
    # --------------------------------------------------------

    save_generation_network(
        config,
        best_genome,
        generation
    )


# ============================================================
# TRAINING
# ============================================================

def run_training():

    global generation

    # --------------------------------------------------------
    # CONFIG PATH
    # --------------------------------------------------------

    config_path = (
        BASE_DIR
        / "config-feedforward.txt"
    )

    if not config_path.exists():

        raise FileNotFoundError(
            f"NEAT configuration not found:\n"
            f"{config_path}"
        )

    # --------------------------------------------------------
    # LOAD NEAT CONFIG
    # --------------------------------------------------------

    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        str(config_path)
    )

    # --------------------------------------------------------
    # CREATE POPULATION
    # --------------------------------------------------------

    population = neat.Population(
        config
    )

    # --------------------------------------------------------
    # CONSOLE REPORTER
    # --------------------------------------------------------

    population.add_reporter(
        neat.StdOutReporter(
            True
        )
    )

    # --------------------------------------------------------
    # STATISTICS REPORTER
    # --------------------------------------------------------

    statistics = neat.StatisticsReporter()

    population.add_reporter(
        statistics
    )

    # --------------------------------------------------------
    # CHECKPOINTING
    # --------------------------------------------------------

    population.add_reporter(
        neat.Checkpointer(
            generation_interval=10,
            filename_prefix=str(
                BASE_DIR
                / "neat-checkpoint-"
            )
        )
    )

    # --------------------------------------------------------
    # RUN EVOLUTION
    # --------------------------------------------------------

    winner = population.run(
        eval_genomes,
        GENERATIONS
    )

    # --------------------------------------------------------
    # SAVE WINNING GENOME
    # --------------------------------------------------------

    winner_path = (
        BASE_DIR
        / "best_genome.pkl"
    )

    with open(
        winner_path,
        "wb"
    ) as file:

        pickle.dump(
            winner,
            file
        )

    # ========================================================
    # FINAL VISUALIZATIONS
    # ========================================================

    print(
        "\nGenerating final visualizations..."
    )

    # --------------------------------------------------------
    # Fitness graph
    # --------------------------------------------------------

    try:

        visualize.plot_stats(
            statistics,
            view=False,
            filename=str(
                BASE_DIR
                / "fitness.svg"
            )
        )

        print(
            "Saved: fitness.svg"
        )

    except Exception as error:

        print(
            f"Could not create fitness graph: "
            f"{error}"
        )

    # --------------------------------------------------------
    # Species graph
    # --------------------------------------------------------

    try:

        visualize.plot_species(
            statistics,
            view=False,
            filename=str(
                BASE_DIR
                / "species.svg"
            )
        )

        print(
            "Saved: species.svg"
        )

    except Exception as error:

        print(
            f"Could not create species graph: "
            f"{error}"
        )

    # --------------------------------------------------------
    # Final winner network
    # --------------------------------------------------------

    save_generation_network(
        config,
        winner,
        generation
    )

    # --------------------------------------------------------
    # Training summary
    # --------------------------------------------------------

    print(
        "\n======================================"
    )

    print(
        "TRAINING COMPLETE"
    )

    print(
        "======================================"
    )

    print(
        f"Generations: {generation}"
    )

    print(
        f"Winner fitness: "
        f"{winner.fitness:.2f}"
    )

    print(
        f"Winner saved to:\n"
        f"{winner_path}"
    )

    print(
        f"\nNetwork diagrams:\n"
        f"{NETWORK_DIR}"
    )

    print(
        "\nFinal visualizations:"
    )

    print(
        f"{BASE_DIR / 'fitness.svg'}"
    )

    print(
        f"{BASE_DIR / 'species.svg'}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        run_training()

    except KeyboardInterrupt:

        print(
            "\nTraining interrupted by user."
        )

    except SystemExit:

        pass

    except Exception as error:

        print(
            "\nPROGRAM ERROR:"
        )

        print(error)

        raise

    finally:

        pygame.quit()