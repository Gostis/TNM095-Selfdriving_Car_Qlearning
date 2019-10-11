import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *
import math
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
        self.q_table = self.defineQtable()
        self.wallPositions = ([[0 for x in range(GRIDWIDTH+1)] for y in range(GRIDHEIGHT+1)])
        self.numberOfEpisodes = 0
        self.episode_rewards = []
        self.aggr_ep_rewards = {'ep': [], 'avg': [], 'min': [], 'max': []}

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'images')
        self.map = Map(path.join(game_folder, 'map5.txt'))
        # Other image
        # self.map = TiledMap(path.join(img_folder, 'MAP1_COLISIONS.tmx'))
        # self.map_img = self.map.make_map()
        # self.map_rect = self.map_img.get_rect()

        self.player_img = pg.image.load(
            path.join(img_folder, PLAYER_IMG)).convert_alpha()
        # Other car
        # .player_img = pg.transform.rotate(pg.transform.scale(self.player_img, (math.floor(self.player_img.get_width() / SHRINK_FACTOR ),math.floor(self.player_img.get_height() / SHRINK_FACTOR))), 180-ROTATE_SPRITE_DEG)
       # self.player_img = pg.transform.rotate(pg.transform.scale(
       #     self.player_img, (self.player_img.get_width(), #self.player_img.get_height())), 0)

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.goals = pg.sprite.Group()
        # self.player = Player(self,4, 12)

        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == 'x':
                    Wall(self, col, row)
                    self.wallPositions[col][row] = 1
                if tile == 'P':
                    self.player = Player(self, col * TILESIZE, row * TILESIZE)
                if tile == 'G':
                    self.goal = Goal(self, col, row)
                    self.wallPositions[col][row] = 2
        '''
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'Player':
                self.player = Player(self, 100, 100)

            if tile_object.name == 'Death':
                Obstacle(self,tile_object.x *TILESIZE ,tile_object.y * TILESIZE,
                         tile_object.width * TILESIZE,tile_object.height * TILESIZE)
        '''
    def defineQtable(self):
        start_q_table = 'qtable_FINAL_1570805657.pickle' #"qtable_FINAL_1570803598.pickle" #'qtable_1570784179.pickle'  # or filename
        if start_q_table is None:
            q_table = {}

            for x in range(0, int(GRIDWIDTH)+1):
                for y in range(0, int(GRIDHEIGHT)+1):
                        q_table[(x,y)] = [np.random.uniform(-5, 0) for i in range(NUMBER_OF_ACTIONS)]
        else:
            with open(start_q_table, 'rb') as f:
                q_table = pickle.load(f)

        return q_table

    def qLearning(self):

        self.player.resetPosition()
        player = self.player
        food = self.goal

        episode_reward = 0
        epsilon = 0

        self.update()
        self.dt = 0.5

        for i in range(ITERATIONS):
        #while True:
            #obs = (self.player-food, self.player-self.closestRaycast())
            obs = (int(player.posToTile.x), int(player.posToTile.y))
            if np.random.random() > epsilon:
                action = np.argmax(self.q_table[obs])
            else:
                action = np.random.randint(0, NUMBER_OF_ACTIONS)

            player.action(action)
            self.update()

            if not LEARNING:
                self.draw()
            if(self.wallPositions[int(player.posToTile.x)][int(player.posToTile.y)] == 1):
                player.hitWall = True
            elif(self.wallPositions[int(player.posToTile.x)][int(player.posToTile.y)] == 2):
                player.hitGoal = True

            #if(player.toMuchRotation == True):
                #player.hitWall = True

            if player.hitWall:
                reward = -DEATH_PENALTY
            elif player.hitGoal:
                reward = FOOD_REWARD
                print("Hit Goal")
            else:
                reward = -MOVE_PENALTY #+ self.distanceTo((player.pos), food)

            new_obs = (player.posToTile.x, player.posToTile.y)

            max_future_q = np.max(self.q_table[new_obs])
            current_q = self.q_table[new_obs][action]

            if reward == FOOD_REWARD:
                new_q = FOOD_REWARD
            elif reward == -DEATH_PENALTY:
                new_q = -DEATH_PENALTY
            else:
                new_q = (1 - LEARNING_RATE) * current_q + LEARNING_RATE * (reward + DISCOUNT * max_future_q)

            self.q_table[(self.player.posToTile.x,self.player.posToTile.y)][(action)] = new_q

            episode_reward += reward

            if reward == FOOD_REWARD or reward == -DEATH_PENALTY:
                player.resetPosition()
                break

        self.episode_rewards.append(episode_reward)
        #epsilon *= EPS_DECAY


    def distanceTo(self, pointOne, pointTwo):
        dist = math.sqrt(
            (pointOne.x - pointTwo.x) ** 2 + (pointOne.x - pointTwo.y) ** 2)
        #(dist)
        if(dist > 200):
            return 0
        else:
            return 1

    def closestRaycast(self):
        rayCast = 0
        highestValue = 0
        for i in range(NUMBER_OF_RAYCASTS):
            if(self.rayCastGroup[i].distanceToObstacle > highestValue):
                highestValue = self.rayCastGroup[i].distanceToObstacle
                rayCast = self.rayCastGroup[i].collidePoint

        if highestValue != 0:
            return rayCast
        else:
            return vec(0, 0)

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        self.coll = False
        self.i = 0

        self.player.resetPosition()

        for episode in range(HM_EPISODES):
            #print("episode", episode)
            self.events()
            self.qLearning()

            if LEARNING:
                if not episode % SHOW_EVERY:
                    average_reward = sum(self.episode_rewards[-SHOW_EVERY:]) / len(self.episode_rewards[-SHOW_EVERY:])
                    self.aggr_ep_rewards['ep'].append(episode)
                    self.aggr_ep_rewards['avg'].append(average_reward)
                    self.aggr_ep_rewards['min'].append(
                        min(self.episode_rewards[-SHOW_EVERY:]))
                    self.aggr_ep_rewards['max'].append(
                        max(self.episode_rewards[-SHOW_EVERY:]))
                    print(
                        f"Episode: {episode} avg: {average_reward} min: {min(self.episode_rewards[-SHOW_EVERY:])} max:{max(self.episode_rewards[-SHOW_EVERY:])}")
                #if not episode % SHOW_EVERY * 10:
                #    with open(f"qtable_{episode}_{int(time.time())}.pickle", "wb") as f:
                #        pickle.dump(self.q_table, f)





    def quit(self):
        if LEARNING:
            with open(f"qtable_FINAL_{int(time.time())}.pickle", "wb") as f:
                pickle.dump(self.q_table, f)

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

        self.all_sprites.update()


        # Raycasts
        '''
        self.rayCastSouth = RayCast((self.player.pos.x, self.player.pos.y), (
            self.player.pos.x, self.player.pos.y - RAYCAST_LENGTH), self.player.rad, self.walls)

        self.rayCastNorth = RayCast((self.player.pos.x, self.player.pos.y), (
            self.player.pos.x, self.player.pos.y + RAYCAST_LENGTH), self.player.rad, self.walls)

        self.rayCastEast = RayCast((self.player.pos.x, self.player.pos.y), (
            self.player.pos.x + RAYCAST_LENGTH, self.player.pos.y), self.player.rad, self.walls)

        self.rayCastWest = RayCast((self.player.pos.x, self.player.pos.y), (
            self.player.pos.x - RAYCAST_LENGTH, self.player.pos.y), self.player.rad, self.walls)

        self.rayCastGroup = [self.rayCastSouth, self.rayCastEast,
                                   self.rayCastNorth, self.rayCastWest]

        '''
        #print(f"South: {self.rayCastSouth.distanceToObstacle}, North: {self.rayCastNorth.distanceToObstacle}, "
        #      f"East: {self.rayCastEast.distanceToObstacle} and West: {self.rayCastWest.distanceToObstacle}")


    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        self.screen.fill(BGCOLOR)

        # self.screen.blit(self.map_img, (0,0))
        self.draw_grid()

        self.all_sprites.draw(self.screen)

        # Raycasts
        """"
        pg.draw.line(self.screen, LIGHTGREEN,
                     (self.player.pos.x, self.player.pos.y), self.rayCastSouth.target, 2)
        pg.draw.circle(self.screen, TEAL, [
            int(x) for x in self.rayCastSouth.collidePoint], 5)

        pg.draw.line(self.screen, LIGHTGREEN,
                     (self.player.pos.x, self.player.pos.y), self.rayCastNorth.target, 2)
        pg.draw.circle(self.screen, TEAL, [
            int(x) for x in self.rayCastNorth.collidePoint], 5)

        pg.draw.line(self.screen, LIGHTGREEN,
                     (self.player.pos.x, self.player.pos.y), self.rayCastEast.target, 2)
        pg.draw.circle(self.screen, TEAL, [
            int(x) for x in self.rayCastEast.collidePoint], 5)

        pg.draw.line(self.screen, LIGHTGREEN,
                     (self.player.pos.x, self.player.pos.y), self.rayCastWest.target, 2)
        pg.draw.circle(self.screen, TEAL, [
            int(x) for x in self.rayCastWest.collidePoint], 5)
        """
        #####
        pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)
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
