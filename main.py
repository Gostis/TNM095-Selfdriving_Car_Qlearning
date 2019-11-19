import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *
import numpy as np
import pickle
import time
import matplotlib.pyplot as plt


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.rayCastGroup = [0 for i in range(NUMBER_OF_RAYCASTS)]
        # repeating wont be needed.
        pg.key.set_repeat(500, 100)
        self.goal = (0, 0)
        self.load_data()
        self.wallPositions = ([[0 for x in range(GRIDWIDTH + 1)]
                               for y in range(GRIDHEIGHT + 1)])
        self.numberOfEpisodes = 0
        self.episode_rewards = []
        self.aggr_ep_rewards = {'ep': [], 'avg': [], 'min': [], 'max': []}

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'images')
        # self.map = Map(path.join(game_folder, 'mapSimple2.txt'))
        # Other image
        self.map = TiledMap(path.join(img_folder, 'Simple_Road.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        self.player_img = pg.image.load(
            path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.player_img = pg.transform.scale(self.player_img, (TILESIZE, TILESIZE * 2))

        # Bot
        self.bot_image = pg.image.load(
            path.join(img_folder, BOT_IMG)).convert_alpha()
        self.bot_image = pg.transform.scale(self.bot_image, (TILESIZE, TILESIZE * 2))

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.gamer_class = pg.sprite.Group()

        self.walls = pg.sprite.Group()
        self.goals = pg.sprite.Group()
        self.gamer = Player(self, 5*TILESIZE, 5*TILESIZE)

        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'Player':
                self.player = Agent(self, tile_object.x * 2, tile_object.y * 2)
            if tile_object.name == 'Death':
            
                tempPos = vec(int(tile_object.x), int(tile_object.y))
                tempHeight = int(tile_object.height)
                tempWidth = int(tile_object.width)
                for x in range(tempWidth):
                    for y in range(tempHeight):
                        self.wallPositions[int(tempPos.x + x) * 2 // TILESIZE][int(tempPos.y + y) * 2 // TILESIZE] = 1
            if tile_object.name == 'Goal':
                tempPos = vec(int(tile_object.x), int(tile_object.y))
                tempHeight = int(tile_object.height)
                tempWidth = int(tile_object.width)
                self.goal = Goal(self, tempHeight, tempWidth)
                for x in range(tempWidth):
                    for y in range(tempHeight):
                        # print(f'{tempPos.x+x} , {tempPos.y+y} : pos')
                        self.wallPositions[int(tempPos.x + x) * 2 // TILESIZE][int(tempPos.y + y) * 2 // TILESIZE] = 2

    def defineQtable(self):
        start_q_table = QTABLE  # or filename
        if start_q_table is None:
            q_table = {}

            eqDist = self.distanceTo(vec(int(WIDTH), int(HEIGHT)), vec(0, 0))
            print("eqDist", eqDist)
            for dist in range(0, int(eqDist) + 1):
                for x in range(0, int(GRIDWIDTH) + 1):
                    for y in range(0, int(GRIDHEIGHT) + 1):
                        q_table[dist, (x, y)] = [np.random.uniform(-5, 0)
                                                 for i in range(NUMBER_OF_ACTIONS)]
        else:
            with open(start_q_table, 'rb') as f:
                q_table = pickle.load(f)

        return q_table

    def qLearning(self):
        self.player.resetPosition()
        player = self.player
        food = self.goal

        episode_reward = 0

        self.update()
        self.dt = 0.1
        for i in range(ITERATIONS):
            obs = (
            self.distanceTo(self.player.pos, self.goal), (self.player.pos.x // TILESIZE, self.player.pos.y // TILESIZE))
            if np.random.random() > self.epsilon:
                action = np.argmax(self.q_table[obs])
            else:
                action = np.random.randint(0, NUMBER_OF_ACTIONS)

            self.player.action(action)
            self.all_sprites.update()
            self.draw()

            if (self.wallPositions[int(self.player.pos.x // TILESIZE)][int(self.player.pos.y // TILESIZE)] == 1):
                self.player.hitWall = True
            elif (self.wallPositions[int(self.player.pos.x // TILESIZE)][int(self.player.pos.y // TILESIZE)] == 2):
                self.player.hitGoal = True

            self.all_sprites.update()

            if self.player.hitWall:
                reward = -DEATH_PENALTY
            elif self.player.hitGoal:
                reward = FOOD_REWARD
            else:
                reward = -MOVE_PENALTY  # + self.distanceTo((player.pos), self.food)

            new_obs = (
            self.distanceTo(self.player.pos, self.goal), (self.player.pos.x // TILESIZE, self.player.pos.y // TILESIZE))

            max_future_q = np.max(self.q_table[new_obs])
            current_q = self.q_table[obs][action]

            if reward == FOOD_REWARD:
                new_q = FOOD_REWARD
            elif reward == -DEATH_PENALTY:
                new_q = -DEATH_PENALTY
            else:
                new_q = (1 - LEARNING_RATE) * current_q + LEARNING_RATE * (reward + DISCOUNT * max_future_q)

            self.q_table[obs][action] = new_q

            if reward == FOOD_REWARD or reward == -DEATH_PENALTY:
                player.resetPosition()
                break
            else:
                if (LEARNING == False):
                    time.sleep(0.1)

        self.episode_rewards.append(episode_reward)
        self.epsilon *= EPS_DECAY

    def distanceTo(self, pointOne, pointTwo):
        return (math.sqrt((pointOne.x - pointTwo.x) ** 2 + (pointOne.x - pointTwo.y) ** 2)) // TILESIZE

    def closestRaycast(self):
        rayCast = 0
        highestValue = 0
        for i in range(NUMBER_OF_RAYCASTS):
            if (self.rayCastGroup[i].distanceToObstacle > highestValue):
                highestValue = self.rayCastGroup[i].distanceToObstacle
                rayCast = self.rayCastGroup[i].collidePoint

        if highestValue != 0:
            return rayCast
        else:
            return vec(0, 0)

    def startQlearning(self):
        self.epsilon = START_EPSILON
        self.player.resetPosition()

        for episode in range(HM_EPISODES):
            self.events()
            self.qLearning()

            if LEARNING:
                if not episode % SHOW_EVERY:
                    average_reward = sum(
                        self.episode_rewards[-SHOW_EVERY:]) / len(self.episode_rewards[-SHOW_EVERY:])
                    self.aggr_ep_rewards['ep'].append(episode)
                    self.aggr_ep_rewards['avg'].append(average_reward)
                    self.aggr_ep_rewards['min'].append(
                        min(self.episode_rewards[-SHOW_EVERY:]))
                    self.aggr_ep_rewards['max'].append(
                        max(self.episode_rewards[-SHOW_EVERY:]))
                    print(
                        f"Episode: {episode} avg: {average_reward} min: {min(self.episode_rewards[-SHOW_EVERY:])} max:{max(self.episode_rewards[-SHOW_EVERY:])}")
                    print("Epsilon: ", self.epsilon)
                # if not episode % SHOW_EVERY * 10:
                #    with open(f"qtable_{episode}_{int(time.time())}.pickle", "wb") as f:
                #        pickle.dump(self.q_table, f)

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        self.q_table = self.defineQtable()

        if QLEARNING:
            self.startQlearning()
        else:
            self.playerAgainstAI()

    def playerAgainstAI(self):
        self.playing = True
        self.q_table = self.defineQtable()
        iterator = 0

        self.player.resetPosition()
        self.epsilon = START_EPSILON

        while self.playing:
            self.events()
            self.dt = self.clock.tick(FPS) / 1000
            if(iterator % 3 == 0):
                self.qLearningMini(iterator)
            else:
                self.gamer_class.update()
                self.draw()

            iterator = iterator + 1

    def qLearningMini(self, iterator):
        if(iterator == ITERATIONS):
            self.player.resetPosition()

        obs = (self.distanceTo(self.player.pos, self.goal), (self.player.pos.x // TILESIZE, self.player.pos.y // TILESIZE))
        if np.random.random() > self.epsilon:
            action = np.argmax(self.q_table[obs])
        else:
            action = np.random.randint(0, NUMBER_OF_ACTIONS)

        self.player.action(action)
        self.all_sprites.update()
        self.draw()

        if (self.wallPositions[int(self.player.pos.x // TILESIZE)][int(self.player.pos.y // TILESIZE)] == 1):
            self.player.hitWall = True
        elif (self.wallPositions[int(self.player.pos.x // TILESIZE)][int(self.player.pos.y // TILESIZE)] == 2):
            self.player.hitGoal = True

        self.all_sprites.update()

        if self.player.hitWall:
            reward = -DEATH_PENALTY
        elif self.player.hitGoal:
            reward = FOOD_REWARD
        else:
            reward = -MOVE_PENALTY  # + self.distanceTo((player.pos), self.food)

        new_obs = (self.distanceTo(self.player.pos, self.goal), (self.player.pos.x // TILESIZE, self.player.pos.y // TILESIZE))

        max_future_q = np.max(self.q_table[new_obs])
        current_q = self.q_table[obs][action]

        if reward == FOOD_REWARD:
            new_q = FOOD_REWARD
        elif reward == -DEATH_PENALTY:
            new_q = -DEATH_PENALTY
        else:
            new_q = (1 - LEARNING_RATE) * current_q + LEARNING_RATE * (reward + DISCOUNT * max_future_q)

        self.q_table[obs][action] = new_q

        if reward == FOOD_REWARD or reward == -DEATH_PENALTY:
            self.player.resetPosition()
            if reward == FOOD_REWARD:
                self.gamer.resetPosition()

        self.epsilon *= EPS_DECAY

    def quit(self):
        if LEARNING and QLEARNING:
            with open(f"qtable_LAST_{int(time.time())}.pickle", "wb") as f:
                pickle.dump(self.q_table, f)
                # joblib.dump(self.q_table, f)
            plt.plot(self.aggr_ep_rewards['ep'],
                     self.aggr_ep_rewards['avg'], label="avg")
            plt.plot(self.aggr_ep_rewards['ep'],
                     self.aggr_ep_rewards['min'], label="min")
            plt.plot(self.aggr_ep_rewards['ep'],
                     self.aggr_ep_rewards['max'], label="max")
            plt.legend(loc=4)
            plt.show()

        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        pass

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        # self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_img, (0, 0))
        # self.draw_grid()

        self.all_sprites.draw(self.screen)
        self.gamer_class.draw(self.screen)
        

        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass


# create the game object
g = Game()
g.show_start_screen()
jacobsVariabel = True
while jacobsVariabel:
    g.new()
    g.run()
    g.show_go_screen()
    jacobsVariabel = False
g.quit()
