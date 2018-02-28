import sys
import gym
import pylab
import random
import numpy as np
from collections import deque
from keras.layers import Dense
from keras.optimizers import Adam
from keras.models import Sequential

EPISODES = 300

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.render = False
        self.load_model = False

        # S, A
        self.state_size = state_size
        self.action_size = action_size

        # DQN hyperparams
        self.discount_factor = 0.99
        self.learning_rate = 0.001
        self.epsilon = 1.0
        self.epsilon_decay = 0.999
        self.epsilon_min = 0.01
        self.batch_size = 64
        self.train_start = 1000

        # replay memory
        self.memory = deque(maxlen=2000)

        # model & target model
        self.model = self.build_model()
        self.target_model = self.build_model()

        # init. target model
        self.update_target_model()

        if self.load_model:
                self.model.load_weights("./model/stock_trained.h5")

    # NN
    def build_model(self):
        model = Sequential()

        model.add(Dense(24, input_dim = self.state_size, activation='relu', kernel_initializer='he_uniform'))
        model.add(Dense(24, activation='relu', kernel_initializer='he_uniform'))
        model.add(Dense(24, activation='linear', kernel_initializer='he_uniform'))
        model.summary()
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model

    # update target model to weight of model
    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    # select action with epsilon greedy policy
    def get_Action(Self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        else:
            q_value = self.model.predict(state)
            return np.argmax(q_value[0])

    # save <s,a,r,s'> to replay memory
    def append_sample(self, state, action, reward, next_state, done):
        self.memory.append((state,action,reward,next_state,done))

    # train model with random extraction from replay memory
    def train_model(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        # sample extraction
        mini_batch = random.sample(self.memory, self.batch_size)

        states = np.zeros((self.batch_size, self.state_size))
        next_states = np.zeros((self.batch_size, self.state_size))
        actions,rewards,dones=[],[],[]

        for i in range(self.batch_size):
            states[i] = mini_batch[i][0]
            actions.append(mini_batch[i][1])
            rewards.append(mini_batch[i][2])
            next_states[i] = mini_batch[i][3]
            dones.append(mini_batch[i][4])
        
        # Q-function for current state
        target = self.model.predict(states)
        # Q-function of target model for next state
        target_val = self.target_model.predict(next_states)

        # update target with Bellman Opt. Eq.
        for i in range(self.batch_size):
            if done[i]:
                target[i][actions[i]] = rewards[i]
            else:
                target[i][actions[i]] = rewards[i] + self.discount_factor*(np.amax(target_val[i]))
        
        self.model.fit(states, target, batch_size=self.batch_size, epochs=1, verbose=0)

if __name__="__main__":
    