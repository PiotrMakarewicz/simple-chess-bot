from math import sqrt, log, fabs
from copy import deepcopy
import random

import chess

# adapted from https://medium.com/@_michelangelo_/monte-carlo-tree-search-mcts-algorithm-for-dummies-74b2bae53bfa
class MonteCarloNode:
    
    '''
    The MonteCarloNode class represents a node of the MCTS tree. 
    It contains the information needed for the algorithm to run its search.
    '''

    def __init__(self, root_board, is_leaf, parent, node_board, move_stack, evaluation_func, exploration_factor=2e2, max_rollout_depth=8, player_color=chess.WHITE):
          
        # child nodes
        self.child = None
        
        # total rewards from MCTS exploration
        self.T = 0
        
        # visit count
        self.N = 0        
                
        # the board in the current moment of the game
        self.root_board = root_board
        
        # observation of the board in the node's position
        self.node_board = node_board
        
        # if game is won/loss/draw
        self.is_leaf = is_leaf

        # link to parent node
        self.parent = parent
        
        # moves that led to the current position, starting from the root
        self.move_stack = move_stack

        self.evaluation_func = evaluation_func 
        self.exploration_factor = exploration_factor
        self.max_rollout_depth = max_rollout_depth
        self.player_color = player_color


    def getUCBscore(self):
        
        '''
        This is the formula that gives a value to the node.
        The MCTS will pick the nodes with the highest value.        
        '''
        
        # Unexplored nodes have maximum values so we favour exploration
        if self.N == 0:
            return float('inf')
        
        # We need the parent node of the current node 
        top_node = self
        if top_node.parent:
            top_node = top_node.parent
            
        # We use one of the possible MCTS formula for calculating the node value
        return (self.T / self.N) + self.exploration_factor*sqrt(log(top_node.N) / self.N) 


    def create_child(self):
        
        '''
        We create one children for each possible action of the game, 
        then we apply such action to a copy of the current node enviroment 
        and create such child node with proper information returned from the action executed
        '''
        
        if self.is_leaf:
            return
    
        actions = self.node_board.legal_moves
        child_boards = [deepcopy(self.node_board) for _ in actions]
        child = {}

        for move, board in zip(actions, child_boards):
            board.push(move)
            child[move] = MonteCarloNode(root_board=self.root_board,
                               is_leaf=board.is_game_over(),
                               parent=self,
                               node_board=board,
                               move_stack=self.move_stack + [move], 
                               evaluation_func=self.evaluation_func)             
            
        self.child = child


    def explore(self):
        
        '''
        The search along the tree is as follows:
        - from the current node, recursively pick the children which maximizes the value according to the MCTS formula
        - when a leaf is reached:
            - if it has never been explored before, do a rollout and update its current value
            - otherwise, expand the node creating its children, pick one child at random, do a rollout and update its value
        - backpropagate the updated statistics up the tree until the root: update both value and visit counts
        '''
        
        # find a leaf node by choosing nodes with max U.
        
        current = self
        
        while current.child:

            child = current.child
            max_U = max(c.getUCBscore() for c in child.values())
            actions = [ a for a,c in child.items() if c.getUCBscore() == max_U ]
            if len(actions) == 0:
                print("error zero length ", max_U)                      
            action = random.choice(actions)
            current = child[action]
            
        # play a random game, or expand if needed          
            
        if current.N < 1:
            current.T = current.T + current.rollout()
        else:
            current.create_child()
            if current.child is not None and len(current.child) > 0:
                _, current = random.choice(list(current.child.items()))
            current.T = current.T + current.rollout()
            
        current.N += 1      
                
        # update statistics and backpropagate
            
        parent = current
            
        while parent.parent:
            
            parent = parent.parent
            parent.N += 1
            parent.T = parent.T + current.T


    def rollout(self):
        
        '''
        The rollout is a random play from a copy of the environment of the current node using random moves.
        This will give us a value for the current node.
        Taken alone, this value is quite random, but, the more rollouts we will do for such node,
        the more accurate the average of the value for such node will be. This is at the core of the MCTS algorithm.
        '''
        
        if self.is_leaf:
            return self.evaluation_func(self.node_board)        
    
        is_leaf = False

        rollout_depth = 0

        while not is_leaf:
            action = random.choice(list(self.node_board.legal_moves))
            self.node_board.push(action)
            is_leaf = self.node_board.is_game_over() or rollout_depth >= self.max_rollout_depth 
            rollout_depth += 1
        
        # Get evaluation
        black_white_factor = 1 if self.player_color == chess.WHITE else -1
        eval = black_white_factor * self.evaluation_func(self.node_board)

        # Restore the state of the board before the rollout
        for _ in range(rollout_depth):
            self.node_board.pop()

        return eval


    def next(self):
        ''' 
        Once we have done enough search in the tree, the values contained in it should be statistically accurate.
        We will at some point then ask for the next action to play from the current node, and this is what this function does.
        There may be different ways on how to choose such action, in this implementation the strategy is as follows:
        - pick at random one of the node which has the maximum visit count, as this means that it will have a good value anyway.
        '''

        if self.is_leaf:
            raise ValueError("game has ended")

        if not self.child:
            raise ValueError('no children found and game hasn\'t ended')
        
        child = self.child
        
        max_reward = max(node.T for node in child.values())
       
        max_children = [ (a, c) for a,c in child.items() if c.T == max_reward]
        
        max_child = random.choice(max_children)

        ### Print evaluation for all legal moves
        for action, node in child.items():
            print(action, node.N, node.T, node.T / node.N)

        action, next_root = max_child
        
        return action, next_root 