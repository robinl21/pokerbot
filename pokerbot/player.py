'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import random
import eval7

class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        self.my_3bets = 0
        self.opp_raise_3bets = 0
        self.opp_call_3bets = 0
        self.opp_fold_3bets = 0
        self.fold_to_3bet = 0 #percentage
        self.above_ten = False

        self.my_preflop_raises = 0
        self.fold_to_preflop = 0

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        #game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        #round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        #my_cards = round_state.hands[active]  # your cards
        #big_blind = bool(active)  # True if you are the big blind
        self.first_raise = True #beginning of each WHOLE GAME
        self.three_bet = False #indicator that we three-bet in our previous action

        print("NEW ROUND")
        #INITIALLY PLAY 100 until adjusting values to collect data:

        if self.my_3bets < 10:
            print(self.my_3bets, self.opp_raise_3bets, self.opp_call_3bets, self.opp_fold_3bets, "ALL")

            #set to standard, while still collecting data on opponent
            self.three_bet_sizing = 3
            self.three_bet_decision = 3
            
            return None

        else:
            print("ABOVE 10 3 bets")
            self.above_ten = True

            print(self.my_3bets, self.opp_raise_3bets, self.opp_call_3bets, self.opp_fold_3bets, "ALL")

            self.fold_to_3bet = self.opp_fold_3bets / self.my_3bets
            print("fold percentages", self.fold_to_3bet)

            #defaults: 3betsizing and 3betdecisioning
            self.three_bet_sizing = 3 #3 * the continue cost
            self.three_bet_decision = 3 #value hands

            if self.fold_to_3bet <= 0.2: #folds rarely to 3-bets: play tight, high value cards when 3-betting
                self.three_bet_sizing = 3.5  
                self.three_bet_decision = 5 #only 3 bet for high value cards

            elif self.fold_to_3bet >= 0.65: #folds alot, play loose - lower bet since a lot of bets?
                self.three_bet_sizing = 2.75 #variable: if weak, 2.75
                self.three_bet_decision = 4 #3-bet a wide range polarized loose
            else:
                #default:
                self.three_bet_sizing = 3
                self.three_bet_decision = 3 #merged default



        #get information, calculate numbers:total number of raises the opponent does, etc
        #update settings:

        #information: on how to 3-bet:
            # opponent response to 3-bet

                #calling 3-bets, raising 3-bets rather than folding: value hands
                    #pump up the bets sizing!
                #folding to 3-bets: keep bluffs (polarized), size smaller bets
            
            #opponents opening:
                #opening button at very high frequency, 3-bet wide range of hands, size smaller bets
                #opens a small percentage of hands, strong value hands, increase bet size

            
        #dealing with opponent's 3/4/5 bet:
            #if opponent raises very rarely, when facing it, can just fold - play high value hands only, (call/raise less often)

            #if plays loose and aggressive (raises often) - continue with wider polarized range (less scary points), (call/raise more often)

        #opening range:
            #big blind frequently folds to pre-flop raises:
                #open small bet size, large range

            #big blind rarely folds to pre-flop raises: open large size, tighter range


            #aggressive 3-betting strategy: tighten range, larger bets
            #weak 3-betting: large range, smaller bets

            


    def monte_carlo(self, my_hand, iterations, community = []):
        #using code from lecture-ref2 and 3, slightly modified for river of blood
        #probability of winning this round with current hand
        #TODO: consider river of blood. randomly decide 50 percent whether to draw another or not <completed>

        deck = eval7.Deck()
        cur_hand = []
        community_cards = []
        num_red_seen = 0

        #setup cur_hand and deck
        for card in my_hand:
            if card[1] == 'h' or card[1] == 'd':
                num_red_seen += 1
            cur_hand.append(eval7.Card(card))

        for card in cur_hand:
            deck.cards.remove(card)

        #remove community cards from deck
        if community != []:
            for card in community:
                if card[1] == 'h' or card[1] == 'd':
                    num_red_seen += 1
                community_cards.append(eval7.Card(card))

            for card in community_cards:
                deck.cards.remove(card)

        p = 0

        for i in range(iterations):
            deck.shuffle()

            #TODO: generate number of community cards (for now keep 5)

            #simulate red river
            #ratio: 52 total cards. reds: 26
            # (26 - num_red_seen) / (52 - cards_used)
            if len(community) >= 5:
                    if community[-1][1] == 'h' or community[-1][1] == 'd':
                        _COMM = 1 #guaranteed one more community card
                        num_cards_used = 2 + 2 + len(community) + 1 
                
                        red_prob = ((26 - num_red_seen) / (52 - num_cards_used)) * 100
                        
                        #guess whether next one is red or not
                        is_red = random.choices(population = [True, False], weights = [red_prob, 100 - red_prob], k = 1)
                        
                        while is_red[0]: #next guessed to be red
                            #draw additional red card
                            _COMM += 1
                            num_cards_used += 1
                            num_red_seen += 1
                            
                            red_prob = ((26 - num_red_seen) / (52 - num_cards_used)) * 100
                            
                            if red_prob <= 0 or red_prob >= 1:
                                red_prob = 0
                            #reselect
                            is_red = random.choices(population = [True, False], weights = [red_prob, 100 - red_prob], k = 1)

                    else: #last showdown, done flipping
                        _COMM = 0
            
            else:
                _COMM = 5 - len(community) #num of community cards needed to draw
                num_cards_used = 9 
                num_red_seen += int(_COMM / 2)#assume half of those we draw are red

                red_prob = (26 - num_red_seen) / (52 - num_cards_used)
                is_red = random.choices(population = [True, False], weights = [red_prob, 1 - red_prob], k = 1)

                while is_red[0]:
                    _COMM += 1
                    num_cards_used += 1
                    num_red_seen += 1
                    red_prob = (26 - num_red_seen) / (52 - num_cards_used)
                            
                    if red_prob <= 0 or red_prob >= 1:
                        red_prob = 0
                    
                    is_red = random.choices(population = [True, False], weights = [red_prob, 1 - red_prob], k = 1)      
                    
            _OPP = 2

            draw = deck.peek(_COMM + _OPP)

            opp_hole = draw[:_OPP] 
            alt_community = draw[_OPP:]

            #generate hands
            our_hand = cur_hand + community_cards + alt_community
            opp_hand = opp_hole + community_cards + alt_community

            our_value = eval7.evaluate(our_hand)
            opp_value = eval7.evaluate(opp_hand)

            if our_value > opp_value:
                p += 2
            
            elif our_value == opp_value:
                p += 1

            else:
                p += 0

        p = p / (2 * iterations)

        return p


    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        #previous_state = terminal_state.previous_state  # RoundState before payoffs
        #street = previous_state.street  # int of street representing when this round ended
        #my_cards = previous_state.hands[active]  # your cards
        #opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        
        #our last action was a 3-bet, meaning opponent folded to our 3bet:
        if self.three_bet:
            print("OPPONENT FOLDED TO OUR 3BET")
            self.opp_fold_3bets += 1

    def hand_convert(self, card1, card2):
        '''
        Converts two cards 'rank+suite' into (biggest, smaller card + (s, o,))
        '''
        value = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        rank1, rank2 = card1[0], card2[0]
        rank1, rank2 = value[rank1], value[rank2]

        suite1, suite2 = card1[1], card2[1]

        #number, suite, card
        card1 = (rank1, suite1, card1)
        card2 = (rank2, suite2, card2)

        if card1[0] == card2[0]: #same rank
            to_return = (card1[2][0], card2[2][0]) #pair
        elif card1[0] > card2[0]: #card1 bigger
            if card1[1] == card2[1]: #same suite
                to_return = (card1[2][0], card2[2][0] + 's')
            else:
                to_return = (card1[2][0], card2[2][0] + 'o')
        elif card1[0] < card2[0]:
            if card1[1] == card2[1]: #same suite
                to_return = (card2[2][0], card1[2][0] + 's')
            else:
                to_return = (card2[2][0], card1[2][0] + 'o')
        return to_return


    def legalize_raise(self, raise_amount, min_raise, max_raise, my_pip, continue_cost, my_stack, legal_actions):
        '''
        Legalizes raise action. raise -> call > check -> flop
        '''
        # temp_action: best we can do if we want to raise

        #get legal raise amount
        raise_amount = max([min_raise, raise_amount])
        if raise_amount > max_raise:
            raise_amount = max_raise
    
        raise_cost = raise_amount - my_pip

        if (RaiseAction in legal_actions and (raise_cost <= my_stack)): #raise legal
            temp_action = RaiseAction(raise_amount)

        elif (CallAction in legal_actions and (continue_cost <= my_stack)): #continue legal
            temp_action = CallAction()

        elif CheckAction in legal_actions: 
            temp_action = CheckAction()
        else:
            temp_action = FoldAction()

        return temp_action


    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        #borrows some code from lecture 2 reference (logic for actions)
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # int representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        
        # decisions from running simulation
        #0 index - 2 index: 70 percent, 82.5 percent hand, 91 percent hand - opening
        #3 index - 5 index: merged hands (default), polarized (loose) - defending with bluffs, (5) tight
        ranges = {
            'A': {'A': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 
                    'Ko': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 'Qo': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 'Jo': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 'To': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], '9o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'],
                    '8o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '7o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '6o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '5o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '4o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '3o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '2o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], 
                    'Ks': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 'Qs': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 'Js': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 'Ts': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], '9s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'],
                    '8s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '7s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '6s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '5s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '4s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '3s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'],
                    '2s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], 
            },

            'K': {'K': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 'Qo': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 'Jo': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 'To': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], '9o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'],
                    '8o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '7o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '6o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '5o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '4o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '3o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'],
                    '2o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], 'Qs': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 'Js': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 'Ts': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], '9s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'],
                    '8s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '7s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '6s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '5s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '4s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '3s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'],
                    '2s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], 
            },

            'Q': {'Q': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 'Jo': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 'To': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '9o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'],
                    '8o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '7o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '6o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '5o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '4o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '3o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'],
                    '2o': ['Fold', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], 'Js': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 'Ts': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], '9s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'],
                    '8s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '7s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '6s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '5s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '4s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '3s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'],
                    '2s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], 
            },

            'J': {'J': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], 'To': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '9o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'],
                    '8o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '7o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '6o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '5o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '4o': ['Fold', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '3o': ['Fold', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'],
                    '2o': ['Fold', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], 'Ts': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], '9s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'],
                    '8s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '7s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '6s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '5s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '4s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '3s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'],
                    '2s': ['Raise', 'Raise', 'Raise', 'Call', 'Raise', 'Call'], 
            },

            'T': {'T': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'], '9o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'],
                    '8o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '7o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '6o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '5o': ['Fold', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '4o': ['Fold', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '3o': ['Fold', 'Fold', 'Raise', 'Fold', 'Fold', 'Fold'],
                    '2o': ['Fold', 'Fold', 'Raise', 'Fold', 'Fold', 'Fold'], '9s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'],
                    '8s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '7s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '6s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '5s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '4s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '3s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'],
                    '2s': ['Raise', 'Raise', 'Raise', 'Call', 'Raise', 'Call'], 

            },

            '9': {'9': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'],
                    '8o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '7o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '6o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '5o': ['Fold', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '4o': ['Fold', 'Fold', 'Raise', 'Fold', 'Fold', 'Fold'], '3o': ['Fold', 'Fold', 'Raise', 'Fold', 'Fold', 'Fold'],
                    '2o': ['Fold', 'Fold', 'Fold', 'Fold', 'Fold', 'Fold'],
                    '8s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '7s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '6s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '5s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '4s': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], '3s': ['Raise', 'Raise', 'Raise', 'Call', 'Raise', 'Call'],
                    '2s': ['Call', 'Raise', 'Raise', 'Call', 'Raise', 'Call']

            },

            '8': {'8': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'],
                 '7o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '6o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '5o': ['Fold', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '4o': ['Fold', 'Fold', 'Raise', 'Fold', 'Fold', 'Fold'], '3o': ['Fold', 'Fold', 'Fold', 'Fold', 'Fold', 'Fold'],
                    '2o': ['Fold', 'Fold', 'Fold', 'Fold', 'Fold', 'Fold'],
                    '7s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '6s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '5s': ['Raise', 'Raise', 'Raise', 'Call', 'Raise', 'Call'], '4s': ['Raise', 'Raise', 'Raise', 'Call', 'Raise', 'Call'], '3s': ['Call', 'Raise', 'Raise', 'Call', 'Raise', 'Call'],
                    '2s': ['Call', 'Raise', 'Raise', 'Call', 'Raise', 'Call'], 

            },

            '7': {'7': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Raise'],
                 '6o': ['Raise', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '5o': ['Fold', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '4o': ['Fold', 'Fold', 'Raise', 'Fold', 'Fold', 'Fold'], '3o': ['Fold', 'Fold', 'Fold', 'Fold', 'Fold', 'Fold'],
                    '2o': ['Fold', 'Fold', 'Fold', 'Fold', 'Fold', 'Fold'],
                    '6s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '5s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '4s': ['Raise', 'Raise', 'Raise', 'Call', 'Raise', 'Call'], '3s': ['Call', 'Raise', 'Raise', 'Call', 'Raise', 'Call'],
                    '2s': ['Call', 'Raise', 'Raise', 'Call', 'Raise', 'Call'], 

            },

            '6': {'6': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'],
                 '5o': ['Fold', 'Raise', 'Raise', 'Fold', 'Fold', 'Fold'], '4o': ['Fold', 'Fold', 'Raise', 'Fold', 'Fold', 'Fold'], '3o': ['Fold', 'Fold', 'Raise', 'Fold', 'Fold', 'Fold'],
                    '2o': ['Fold', 'Fold', 'Fold', 'Fold', 'Fold', 'Fold'],
                   '5s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '4s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '3s': ['Raise', 'Raise', 'Raise', 'Call', 'Raise', 'Call'],
                    '2s': ['Call', 'Raise', 'Raise', 'Call', 'Raise', 'Call'], 

            },

            '5': {'5': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'],
                 '4o': ['Fold', 'Raise', 'Raise', 'Fold', 'Raise', 'Fold'], '3o': ['Fold', 'Fold', 'Raise', 'Fold', 'Raise', 'Fold'],
                    '2o': ['Fold', 'Fold', 'Fold', 'Fold', 'Fold', 'Fold'],
                 '4s': ['Raise', 'Raise', 'Raise', 'Raise', 'Raise', 'Call'], '3s': ['Raise', 'Raise', 'Raise', 'Call', 'Raise', 'Call'],
                    '2s': ['Call', 'Raise', 'Raise', 'Call', 'Raise', 'Call'], 
            },

            '4': {'4': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'],
                 '3o': ['Fold', 'Fold', 'Fold', 'Fold', 'Raise', 'Fold'],
                    '2o': ['Fold', 'Fold', 'Fold', 'Fold', 'Raise', 'Fold'],
                   '3s': ['Raise', 'Raise', 'Raise', 'Call', 'Raise', 'Call'],
                    '2s': ['Call', 'Raise', 'Raise', 'Call', 'Raise', 'Call'], 
            },

            '3': {'3': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call'], 
                    '2o': ['Fold', 'Fold', 'Fold', 'Fold', 'Fold', 'Raise', 'Fold'],
                    '2s': ['Call', 'Call', 'Raise', 'Call', 'Raise', 'Call']},

            '2': {'2': ['Raise', 'Raise', 'Raise', 'Call', 'Call', 'Call']
            }
        
        }
        
        min_raise, max_raise = round_state.raise_bounds() 
        my_action = None
        print(my_cards)

        pot_total = my_contribution + opp_contribution

        #calculate p of cards
        monte_carlo_p = self.monte_carlo(my_cards, 100, board_cards)
        #guess_p = self.guess_next_probability(my_cards, board_cards, street)

        p = monte_carlo_p

        scary = 0
        #TODO: try to consider opponent range and raises from previous rounds
        #fix p based on opponent's bets (keep low since don't want to kill too early)
        if continue_cost > 0:
            scary = 0

            if continue_cost > 6:
                scary = 0.1

            if continue_cost > 12:
                scary = 0.2

            if continue_cost > 50:
                scary= 0.35

        print("p", p)
        prefix_p = p #before scary modification
        p = max([0, p - scary])
        print("fixed p", p)

        pot_odds = continue_cost / (pot_total + continue_cost) #p*pot_total + (1-p)*cost_to_continue (don't care about previous sunk costs)
        print("pot odds", pot_odds)

        #temporary raise_amount logic
                # raise logic: kill early, raise higher (TAG)
                #kill preflop if nothing raised this round

#COLLECT INFORMATION: our previous action this game was a 3bet
        if self.three_bet:
            self.three_bet = False #reset for next action this round
            #opp either called or raised three-bet:

            if street < 3: #raised 3-bet, but still in pre-flop: opponent raised
                print("OPPONENT RAISED AFTER OUR 3BET")
                self.opp_raise_3bets += 1 #opponent raised, or else round would have ended and three_bet reset
            else: #raised 3-bet, but now in flop means opponent called
                print("OPPONENT CALLED TO OUR 3BET")
                self.opp_call_3bets += 1

            #fold: handled in handle_round_over (our last action was a 3bet, opponent folded)


        #TODO: collect opponent information and adjust
        if street < 3: #preflop: implement folding early via bill chen formula
            card1 = my_cards[0]
            card2 = my_cards[1]
            if continue_cost > 0: #raise
                #opening raise from small blind: continue_cost = 1, my_pip = 1
                #adjust later: currently 2.5 x BB, safe wide range of openings
                if continue_cost == 1 and my_pip == 1: 
                    print("SMALL BLIND INITIAL")
                    hand = self.hand_convert(card1, card2)
                    decision = ranges[hand[0]][hand[1]][1]
                
                    if decision == "Raise":
                        raise_amount = 5
                        return self.legalize_raise(raise_amount, min_raise, max_raise, my_pip, continue_cost, my_stack, legal_actions)
                    
                    elif decision == "Call": #only call available
                        return CallAction()

                    elif decision == "Fold":
                        return FoldAction()

                #three-bet: our first raise encountered by another player this round (non-including small blind)
                #adjust to opponents!! 
                elif self.first_raise: #first defense - initially tight
                    print("Time to 3 BET")
                    self.first_raise = False
                    #three-betting
                    hand = self.hand_convert(card1, card2)
                    decision = ranges[hand[0]][hand[1]][self.three_bet_decision]

                    # #if high fold rate to 3-bets: randomly raise folds (bluff)
                    if self.fold_to_3bet > 0.75 and self.my_3bets > 10:
                        if decision == "Fold":
                            if random.random() > 0.3:
                                decision == "Raise"
                    elif self.fold_to_3bet < 0.25 and self.my_3bets> 10: #low fold rate to 3-bets
                        if decision == "Raise": #high high value hand
                            if random.random() > 0.3 and p > 0.5:
                                self.three_bet_sizing = 4

                    #if playing tight due to low frequency of fold, oftentimes get stuck since we fold and don't give 3-bets
                    #allow more 3-betting when playing tight so we don't get stuck
                    if self.three_bet_decision == 5 and self.above_ten:
                        if ranges[hand[0]][hand[1]][3] == "Raise" and random.random() > 0.5 and p > 0.5:
                            decision = "Raise"
                            self.three_bet_sizing = 3

                    #if playing loose: want to keep the pressure on in the pot odds:
                    if self.three_bet_decision == 4 and self.above_ten:
                        if decision == "Raise":
                            if p > 0.5 and random.random() < self.fold_to_3bet: #the higher the fold percentage is, more likely to put in higher (put same pressure)
                                self.three_bet_sizing = 3
                            else:
                                self.three_bet_sizing = 2.5 #lower if weak

                    if decision == "Raise":
                        #raise 3x amount of opponent's bet: 3 * opp_pip (how much opponent contributed this round of betting )
                        print("WE HAVE 3-BET", self.three_bet_decision)
                        self.three_bet = True #indicator for next action that our previous action was a 3-bet
                        self.my_3bets += 1 #increase num times we 3bet
                        raise_amount = self.three_bet_sizing * opp_pip
                        return self.legalize_raise(raise_amount, min_raise, max_raise, my_pip, continue_cost, my_stack, legal_actions)
                    
                    elif decision == "Call": #only call available
                        return CallAction()

                    elif decision == "Fold": #don't always fold
                        if p > pot_odds and p > 0.5:
                            return CallAction()
                        else:
                            return FoldAction()
                    

                else:
                    #raise beyond first raise, #latter defense: 2.2 * raise?

                    raise_amount = int(my_pip + continue_cost + 0.4*(pot_total + continue_cost))
                
                    raise_amount = max([min_raise, raise_amount]) #biggest one out of min/calculated raise
            
                    if raise_amount > max_raise: #out of bounds (min > max or calculated > max), do max raise
                        raise_amount = max_raise #all-in
                    
                    raise_cost = raise_amount - my_pip #cost to raise

                    #legalize action here: Func

                    # temp_action: best we can do if we want to raise/continue
                    if (RaiseAction in legal_actions and (raise_cost <= my_stack)): #raise legal
                        temp_action = RaiseAction(raise_amount)

                    elif (CallAction in legal_actions and (continue_cost <= my_stack)): #continue legal
                        temp_action = CallAction()

                    elif CheckAction in legal_actions: 
                        temp_action = CheckAction()
                    else:                        
                        return FoldAction()

                    
                    #if pay to keep playing: raise, call, or fold
                    if continue_cost > 0: 
                        
                        if p > pot_odds: #call or raise, don't fold
                            if p > 0.5 and  random.random() < p: #bigger p is, more likely to raise
                                my_action = temp_action #best we can do if want to raise

                            else:
                                my_action = CallAction()
                        else: 
                        #   Fold
                            my_action = FoldAction()
                    
                    else: #pay 0 to play, want to either raise or check
                        if random.random() < p:
                            my_action = temp_action
                        else:
                            my_action = CheckAction()
                    

                    return my_action

            else: #continue_cost == 0:
                print("BIG BLIND OPENING RAISE")
                #big blind first opening raise: same logic as small blind opening raise, except only raise/check
                hand = self.hand_convert(card1, card2)
                decision = ranges[hand[0]][hand[1]][1]
            
                if decision == "Raise":
                    raise_amount = 5
                    temp_action = self.legalize_raise(raise_amount, min_raise, max_raise, my_pip, continue_cost, my_stack, legal_actions)
                    print(temp_action)
                    return temp_action
                else:
                    return CheckAction()

        
        else: 
            
            #postflop, 66 percent of pot. normal play - adjust based on opponent? if opponent folds a lot, play tighter
            raise_amount = int(my_pip + continue_cost + (2/3)*(pot_total + continue_cost))
        
            raise_amount = max([min_raise, raise_amount]) #biggest one out of min/calculated raise
    
            if raise_amount > max_raise: #out of bounds (min > max or calculated > max), do max raise
                raise_amount = max_raise #all-in
            
            raise_cost = raise_amount - my_pip #cost to raise

            #legalize action here: Func

            # temp_action: best we can do if we want to raise/continue
            if (RaiseAction in legal_actions and (raise_cost <= my_stack)): #raise legal
                temp_action = RaiseAction(raise_amount)

            elif (CallAction in legal_actions and (continue_cost <= my_stack)): #continue legal
                temp_action = CallAction()

            elif CheckAction in legal_actions: 
                temp_action = CheckAction()
            else:
                temp_action = FoldAction()

            
            #if pay to keep playing: raise, call, or fold
            if continue_cost > 0: 
                
                if p > pot_odds: #call or raise, don't fold
                    if p > 0.5 and  random.random() < p: #bigger p is, more likely to raise
                        my_action = temp_action #best we can do if want to raise

                    else:
                        my_action = CallAction()
                else: 
                #   Fold
                    my_action = FoldAction()
            
            else: #pay 0 to play, want to either raise or check
                if random.random() < p:
                    my_action = temp_action
                else:
                    my_action = CheckAction()
            

            return my_action


if __name__ == '__main__':
    run_bot(Player(), parse_args())
