#This is my attempt to make a simulated monopoly game
import random
import cmd

players_all = []#players in the game
players_human_max = 1
total_pieces = ["Horse", "Hat", "Battleship", "Thimbal", "Cannon", "Car", "Dog", "Shoe"]
space_jail = 10
space_illinois = 24
space_st_charles = 11
space_go = 0
space_boardwalk = 39
space_reading = 5
money_pass_go = 200
jail_bail = 50

rail_spaces = (space_reading, 15, 25, 35)
util_spaces = (12, 28)

class Die:
    max_roll = 6
    rolls = [0, 0]
    last_roll = sum(rolls)
    text = str(rolls)

    def roll():
        for n in range(len(Die.rolls)):
            Die.rolls[n] = random.randint(1, Die.max_roll)
        Die.last_roll = sum(Die.rolls)#this has to be in here to update last_roll variable

    def is_doubles():#assume it works for now
        last_roll = Die.rolls[0]
        double = False
        for roll in Die.rolls:
            if roll == last_roll:
                double = True
            else:
                double = False
                break
            last_roll = roll
        return double

class Bank:
    houses = 32
    hotels = 12

    def give_money(a_player, amount):
        a_player.money = a_player.money + amount

    def give_house(a_player):
        if Bank.houses > 0:
            a_player.houses = a_player.houses + 1
            Bank.houses = Bank.houses - 1
            return True
        else:
            return False

    def give_hotel(a_player):
        if Bank.hotels > 0:
            a_player.hotels = a_player.hotels + 1
            a_player.houses = a_player.houses - 4
            Bank.hotels = Bank.hotels - 1
            Bank.houses = Bank.houses + 4
            return True
        else:
            return False
    
    def mortgage_property(a_player, prop):
        if type(prop) is Property or type(prop) is RentalProperty:
            borrow = int(prop.mortgage * 1.10)
            Bank.give_money(a_player, borrow)
            prop.is_mortgaged = True

    def unmortgage_property(a_player, prop):
        if type(prop) is Property or type(prop) is RentalProperty:
            payback = int(prop.mortgage * 1.10)
            if a_player.money > payback:
                a_player.money = a_player.money - payback
                prop.is_mortgaged = False
            else:
                pass

    def mortgaged_properties(a_player, mort):
        mortgaged_props = []
        for a_prop in a_player.properties:
            if a_prop.is_mortgaged is mort:
                mortgaged_props.append(a_prop)
        return mortgaged_props

class Action:
    text = None

    def do_to(self, the_player):
        print(the_player.status(self.text))

class Place(Action):
    title = None
    
    def __init__(self, t):
        self.title = t

    def __str__(self):
        return self.title
    
    def do_to(self, the_player):
        message = f"{the_player} has landed on {self}"
        print(the_player.status(message))

class Property(Place):
    price = 0
    mortgage = 0
    owner = None
    is_mortgaged = False
    rent = (0, 0, 0, 0, 0, 0)
    rent_level = 0
    property_set = (0, 0)

    def __init__(self, t, p, r, m, s):
        self.title = t
        self.price = p
        self.rent = r
        self.mortgage = m
        self.property_set = s

    def do_to(self, the_player):
        Place.do_to(self, the_player)
        the_player.land_on_property(self)
                    
    def has_monopoly(self, player):
        has = True
        for n in self.property_set:
            place = board_places[n]
            if place.owner != player:
                has = False
                break
        return has 

    def rent_howmuch(self, the_player):
        amount = self.rent[self.rent_level]
        if self.rent_level == 0:
            if self.has_monopoly(the_player):
                amount = amount * 2
        return amount

class RentalProperty(Property):
    house_cost = 50

    def __init__(self, t, p, r, m, h, s):
        self.title = t
        self.price = p
        self.rent = r
        self.mortgage = m
        self.house_cost = h
        self.property_set = s

    def buy_house(self, the_player):
        if self.rent_level < 6:
            self.rent_level = self.rent_level + 1
            if self.rent_level == 5:
                if Bank.give_hotel(the_player):
                    print(f"{the_player} has bought a hotel on {self}")
                else:
                    print("There are no more hotels to buy!")
            else:
                if Bank.give_house(the_player):
                    print(f"{the_player} has bought a house on {self}")
                else:
                    print("There are no more houses to buy!")


class IncomeTax(Place):
    price = 200   
    tax_rate = .10
    tax200 = price
    tax_percent = 0

    def do_to(self, the_player):
        Place.do_to(self, the_player) 
        IncomeTax.tax_percent = int(the_player.money * IncomeTax.tax_rate)
        the_player.land_on_incometax()

class LuxuryTax(Place):
    price = 75

    def do_to(self, the_player):
        the_player.give_money_to_bank(self.price)
        message = f"{the_player} has Paid ${str(self.price)} in Luxury Tax."
        print(the_player.status(message))

class GoToJail(Place):
    
    def do_to(self, the_player):
        Place.do_to(self, the_player) 
        the_player.move_to_jail()
     
class Jail(Place):
    
    def do_to(self, the_player):
        if the_player.in_jail is False:
            Place.do_to(self, the_player)
        else:#I don't know if player.get_out_of_jail should be called here
            message = f"{the_player} is in jail!"
            print(the_player.status(message))
            player.get_out_of_jail()

#Beginning of cards
class Card(Action):
    text = "community chest says..."
    money = 0
    go_to = 0

    def __init__(self, t, m, p):
        self.text = t
        self.money = m
        self.go_to = p
    
    def __str__(self):
        return self.text

    def do_to(self, the_player):
        Action.do_to(self, the_player)
        Bank.give_money(the_player, self.money)
        if self.go_to is not None:
            the_player.move_to(self.go_to)
            the_player.space().do_to(the_player)#does whatever to the player in the new space

#special cards here
class Collect50(Card):

    def do_to(self, the_player):
        total = 0
        for other_player in players_all:
            if other_player is not the_player:
                other_player.give_money(the_player, self.money)
                total = total + self.money
        self.text = self.text + f" (${total})"
        Action.do_to(self, the_player)

class GoBack3(Card):

    def do_to(self, the_player):
        Action.do_to(self, the_player)
        the_player.move(-3)
        the_player.space().do_to(the_player)

class Pay50(Card):

    def do_to(self, the_player):
        total = 0
        for other_player in players_all:
            if other_player is not the_player:
                the_player.give_money(other_player, self.money)
                total = total + self.money
        self.text = self.text + f" ({total})"
        Action.do_to(self, the_player)

class NearestRailroad(Card):
    _spaces = rail_spaces

    #this method can be used for either nearest railroad or utily
    def move_to_nearest_(self, the_player):
        for r_space in self._spaces:
            if the_player.space_number < r_space:
                the_player.space_number = r_space
            else:#this is when it is after the last space
                the_player.money = the_player.money + money_pass_go #this is for when you pass go 
                the_player.space_number = self._spaces[0]
            break

    def do_to(self, the_player):
        Action.do_to(self, the_player)
        self.move_to_nearest_(the_player)        
        if the_player.space().owner == None:
            the_player.land_on_property(the_player.space())
        else:
            double_rent = the_player.space().rent_howmuch(the_player) * 2
            the_player.give_money(the_player.space().owner, double_rent)
            message = f"{the_player} has paid {str(double_rent)} for riding on the {self}"
            print(the_player.status(message))

class NearestUtility(NearestRailroad):
    _spaces = util_spaces

    def do_to(self, the_player):
        Action.do_to(self, the_player)
        self.move_to_nearest_(the_player)
        if the_player.space().owner == None:
            the_player.land_on_property(the_player.space())
        else:
            Die.roll()
            roll_rent = Die.last_roll * 10 #roll dice and multiplies by 10.  I donn't know how this effects rest of game
            the_player.give_money(the_player.space().owner, roll_rent)
            message = f"{the_player} has paid {str(roll_rent)} for using utility {self}"
            print(the_player.status(message))

class StreetRepairs(Card):

    def do_to(self, the_player):
        total_repair_cost = (the_player.houses * 25) + (the_player.hotels * 100)
        the_player.give_money_to_bank(total_repair_cost)
        self.text = self.text + " $" + str(total_repair_cost) 
        Action.do_to(self, the_player)

class JailCard(Card):

    def do_to(self, the_player):
        Action.do_to(self, the_player)
        the_player.move_to_jail()

class GetOutOfJail(Card):

    def do_to(self, the_player):
        the_player.out_of_jail_free = True
        Action.do_to(self, the_player)

class Chance(Place):
    card_index = 0
    cards = [
            Card("Pay Poor Tax $15", -15, None), 
            NearestUtility("Advance Token To Nearest Utility", 0, None),
            Card("Take A Ride On The Reading.  If You Pass Go Collect $200", 200, space_reading),
            GoBack3("Go Back Three Spaces", 0, None), 
            Card("Advance To Illinois Ave.", 0, space_illinois),
            JailCard("Go To Jail", 0, space_jail),
            StreetRepairs("Make General Repairs On All of Your Properties", 0, None),
            NearestRailroad("Advance Token To The Nearest Railroad", 0, None),
            Pay50("Elected Chairman of the Board. Pay Each Player $50", 50, None), 
            Card("Your Building And Loan Matures Collect $150", 150, None), 
            Card("Advance To St. Charles Place. If You Pass Go Collect $200", 0, space_st_charles),
            Card("Advance To Board Walk", 0, space_boardwalk), 
            Card("Bank Pays You Dividend Of $50", 50, None), 
            NearestRailroad("Advance Token To The Nearest Railroad", 0, None),
            GetOutOfJail("Get Out Of Jail Free Card", 0, None), 
            Card("Advance To Go", 0, space_go)
            ]

    def __init__(self):
        self.title = "Chance"
        random.shuffle(self.cards)
    
    def draw_card(self):#this has to overridden to make sure it draws from the right pile
        if self.card_index >= len(self.cards) - 1:
            self.card_index = 0
        else:
            self.card_index = self.card_index + 1
        return self.cards[self.card_index]

    def do_to(self, the_player):#this has to be overridden to make sure it uses the right draw_card method
        Place.do_to(self, the_player)
        card = self.draw_card()
        card.do_to(the_player)


class Chest(Chance):
    cards = [
            Card("Income Tax Refund Collect $20", 20, None), 
            Card("You Have Won Second Prize in Beauty Contest Collect $10", 10, None),
            Card("Pay Hospital Bill $100", -100, None),
            Card("Advance to Go", 200, space_go), 
            StreetRepairs("You Are Assessed Street Repairs", 0, None), 
            Card("Receive For Services $25", 25, None),
            JailCard("Go To Jail", 0, space_jail), 
            Card("Bank Error In Your Favor Collect $200", 200, None), 
            GetOutOfJail("Get Out Of Jail Free", 0, None), 
            Card("From Sale of Stock You Get $45", 45, None), 
            Card("Doctor's Fee Pay $50", -50, None), 
            Card("XMAS Fund Matures Collect $100", 100, None), 
            Card("You Inherit $100", 100, None), 
            Collect50("Collect $50 From Every Player", 50, None), 
            Card("Pay School Tax of $150", -150, None), 
            Card("Life Insurance Matures Collect $100", 100, None)
            ]

    def __init__(self):
        self.title = "Community Chest"
        random.shuffle(self.cards) 

#beginning of choices objects
class Choice(Action):
    text = "choice"

    def __init__(self, t):
        self.text = t

    def do_to(self, the_player):
        pass

    def __str__(self):
        return self.text

class TradeChoice(Choice):

    def __init__(self):
        self.text = "Trade Properties"

    def do_to(self, the_player):
        other_players = [None]
        other_players = other_players + players_all.copy() 
        other_players.remove(the_player)
        question = "Which player do you want to trade with? "
        other_player = print_choice(other_players, question)
        if other_player is not None:
            other_player_props = [None, CashChoice()]
            other_player_props = other_player_props + other_player.properties.copy()
            other_player_offer = [None]
            question = f"Which one of {other_player} properties do you want? "
            while True:
                other_player_prop = print_choice(other_player_props, question)
                if other_player_prop is None:
                    break
                elif type(other_player_prop) is CashChoice:
                    other_player_money = question_loop("How much money are you asking for? $")
                    other_player_offer = other_player_offer + [other_player_money]
                else:
                    other_player_offer = other_player_offer + [other_player_prop]
                other_player_props.remove(other_player_prop)
            if len(other_player_offer) > 1:
                the_player_props = [None, CashChoice()]
                the_player_props = the_player_props + the_player.properties
                the_player_offer = [None]
                question = f"What are you willing to offer {other_player}? "
                while True:
                    the_player_prop = print_choice(the_player_props, question)
                    if the_player_prop is None:
                        break
                    elif type(the_player_prop) is CashChoice:
                        the_player_money = question_loop(f"How much cash are you willing to offer {other_player}? $")
                        the_player_offer = the_player_offer + [the_player_money]
                    else:
                        the_player_offer = the_player_offer + [the_player_prop]
                    the_player_props.remove(the_player_prop)
                if len(the_player_offer) > 1:
                    other_player_offer = other_player_offer[1:]
                    the_player_offer = the_player_offer[1:]#this is to get rid of the None objects in them
                    other_player.ask_trade(other_player_offer, the_player, the_player_offer)

class BuyChoice(Choice):
    the_prop = None

    def __init__(self, prop):
        self.the_prop = prop
        self.text = "Buy " + self.the_prop.title + " for $" + str(self.the_prop.price)

    def do_to(self, the_player):
        message = None
        if the_player.money > self.the_prop.price:
            the_player.buy_property(self.the_prop)
            message = f"{the_player} has bought {self.the_prop}"
        else:
            message = f"{the_player} does not have enough money to buy {self.the_prop}"
        print(the_player.status(message))

class MortgageChoice(Choice):

    def __init__(self):
        self.text = 'Mortgage Properties'

    def do_to(self, the_player):
        unmortgaged_props = [None]
        unmortgaged_props = unmortgaged_props + Bank.mortgaged_properties(the_player, False)
        question = 'Which one of these do you wish to mortgage? '
        unmortgaged_prop = print_choice(unmortgaged_props, question)
        if unmortgaged_prop is not None:
            Bank.mortgage_property(the_player, unmortgaged_prop) 
            message = f"{the_player} has mortgaged {unmortgaged_prop}"
            print(the_player.status(message))

class UnmortgageChoice(Choice):

    def __init__(self):
        self.text = 'Unmortgage Properties'

    def do_to(self, the_player):
        mortgaged_props = [None]
        mortgaged_props = mortgaged_props + Bank.mortgaged_properties(the_player, True)
        question = "Which one of these do you wish to unmortgage? "
        mortgaged_prop = print_choice(mortgaged_props, question)
        if mortgaged_prop is not None:
            Bank.unmortgage_property(the_player, mortgaged_prop) 
            message = f"{the_player} has unmortgaged {mortgaged_prop}"
            print(the_player.status(message))


class QuitGameChoice(Choice):

    def __init__(self):
        self.text = "Quit Game"

    def do_to(self, the_player):
        the_player.quit_game()

class BuyHouseChoice(Choice):

    def __init__(self):
        self.text = "Buy House or Hotel"

    def do_to(self, the_player):
        monopolies = [None]
        for a_prop in the_player.properties:
            if type(a_prop) is RentalProperty:
                if a_prop.has_monopoly(the_player):
                    monopolies = monopolies + [a_prop]
        question = "Here is a list of available properties you can upgrade "
        prop = print_choice(monopolies, question)
        if prop is not None:
            the_player.buy_house(prop)
            building = "house"
            if prop.rent_level > 4:
                building = "hotel"
            message = f"{the_player} has bought a {building} on {prop}"
            print(the_player.status(message))

class PlayerAssetChoice(Choice):

    def __init__(self):
        self.text = "See Assets of..."

    def do_to(self, the_player):
        players = players_all.copy()
        player = print_choice(players, "Whose Assets do you want to see? ")
        print(f"${player.money}")
        for player_prop in player.properties:
            print(f"{player_prop}")

class CardChoice(Choice):

    def __init__(self):
        self.text = "Use Get Out of Jail Card"

    def do_to(self, the_player):
        if the_player.out_of_jail_card == True:
            the_player.use_card()
            message = f"{the_player} has decided to use their Get Out of Jail Card"
            print(the_player.status(message))

class PayChoice(Choice):

    def __init__(self):
        self.text = "Pay $50 to Get Out of Jail"

    def do_to(self, the_player):
        if the_player.money > jail_bail:
            the_player.pay_fine()
            message = f"{the_player} has decided to pay their way out of jail"
            print(player.status(message))


class RollChoice(Choice):

    def __init__(self):
        self.text = "Roll For Doubles to Get Out of Jail"

    def do_to(self, the_player):
        if the_player.out_of_jail_rolls < 3:
            the_player.roll_for_doubles()
            message = f"{the_player} has rolled {str(Die.last_roll)}"
            print(the_player.status(message))

class EndChoice(Choice):
    
    def __init__(self):
        self.text = "End Turn"

    def do_to(self, the_player):
        pass

class CashChoice(Choice):

    def __init__(self):
        self.text = "Money"

    def do_to(self, the_player):
        pass 

railroad_rents = (25, 50, 100, 200)

purple_spaces = (1, 3)
blue_spaces = (6, 8, 9)
lavender_spaces = (11, 13, 14)
brown_spaces = (16, 18, 19)
red_spaces = (21, 23, 24)
yellow_spaces = (26, 27, 29)
green_spaces = (31, 32, 34)
dark_blue_spaces = (37, 39)

railroad_property = (
        Property("Reading RailRoad", 200, railroad_rents, 100, rail_spaces), 
        Property("Pennsylvania RailRoad", 200, railroad_rents, 100, rail_spaces), 
        Property("B&O RailRoad", 200, railroad_rents, 100, rail_spaces), 
        Property("Short Line RailRoad", 200, railroad_rents, 100, rail_spaces)
        ) 

util_property = (
	Property("Electric Company", 150, (100, 100), 75, util_spaces),
	Property("Water Works", 150, (100, 100), 75, util_spaces)
	)

purple_property = (
        RentalProperty("Mediteranian", 60, (2, 10, 30, 90, 160), 30, 50, purple_spaces), 
        RentalProperty("Baltic Avenue", 60, (4, 20, 180, 320, 450), 30, 50, purple_spaces)
        )

blue_property = (
 	RentalProperty("Oriental", 100, (6, 30, 90, 270, 400, 550), 50, 50, blue_spaces),
 	RentalProperty("Vermont", 100, (6, 30, 90, 270, 400, 550), 50, 50, blue_spaces), 
        RentalProperty("Connecticut Avenue", 120, (8, 40, 100, 300, 450, 600), 60, 50, blue_spaces)
	)

lavender_property = (
	RentalProperty("St. Charles Place", 140, (10, 50, 150, 450, 625, 750), 70, 100, lavender_spaces),
	RentalProperty("States Avenue", 140, (10, 50, 150, 450, 625, 750), 70, 100, lavender_spaces), 
	RentalProperty("Virginia Avenue", 160, (12, 60, 180, 500, 700, 900), 80, 100, lavender_spaces)
	)
	
brown_property = (
	RentalProperty("St. James Place", 180, (14, 70, 200, 550, 750, 950), 90, 100, brown_spaces),
	RentalProperty("Tennesee Avenue", 180, (14, 70, 200, 550, 750, 950), 90, 100, brown_spaces), 
	RentalProperty("New York Avenue", 200, (16, 80, 220, 600, 800, 1000), 100, 100, brown_spaces)
	)

red_property = (
	RentalProperty("Kentucky Avenue", 220, (18, 90, 250, 700, 875, 1050), 110, 150, red_spaces),
	RentalProperty("Indiana Avenue", 220, (18, 90, 250, 700, 875, 1050), 110, 150, red_spaces), 
	RentalProperty("Illinois Avenue", 240, (20, 100, 300, 750, 925, 1100), 120, 150, red_spaces)
	)
	
yellow_property = (
	RentalProperty("Atlantic Avenue", 260, (22, 110, 330, 800, 975, 1150), 130, 150, yellow_spaces), 
	RentalProperty("Ventor Avenue", 260, (22, 110, 330, 800, 975, 1150), 130, 150, yellow_spaces),
	RentalProperty("Marvin Gardens", 280, (24, 120, 360, 850, 1025, 1200), 140, 150, yellow_spaces)
	)
	
green_property = (
	RentalProperty("Pacific Avenue", 300, (26, 130, 390, 900, 1100, 1275), 150, 200, green_spaces), 
	RentalProperty("North Carolina Avenue", 300, (26, 130, 390, 900, 1100, 1275), 150, 150, green_spaces),
	RentalProperty("Pennsylvania Avenue", 320, (28, 150, 450, 1000, 1200, 1400), 160, 150, green_spaces)
	)
	
dark_blue_property = (
	RentalProperty("Park Place", 350, (35, 175, 500, 1100, 1300, 1500), 175, 200, dark_blue_spaces),
	RentalProperty("Bordwalk", 400, (50, 200, 600, 1400, 1700, 2000), 200, 200, dark_blue_spaces)
	)

chance_place = Chance()
chest_place = Chest()

board_places = (
        Place("Go"),
        purple_property[0],
        chest_place, 
        purple_property[1],
        IncomeTax("Pay Income Tax"), 
        railroad_property[0],
        blue_property[0], 
        chance_place, 
        blue_property[1],
        blue_property[2], 
        Jail("Jail"), 
        lavender_property[0], 
        util_property[0], 
        lavender_property[1],
        lavender_property[2], 
        railroad_property[1], 
        brown_property[0], 
        chest_place, 
        brown_property[1],
        brown_property[2], 
        Place("Free Parking"), 
        red_property[0], 
        chance_place, 
        red_property[1],
        red_property[2], 
        railroad_property[2], 
        yellow_property[0],
        yellow_property[1], 
        util_property[1], 
        yellow_property[2], 
        GoToJail("Go To Jail"), 
        green_property[0],
        green_property[1], 
        chest_place, 
        green_property[2], 
        railroad_property[3], 
        chance_place, 
        dark_blue_property[0], 
        LuxuryTax("Luxory Tax"), 
        dark_blue_property[1]
        )

total_spaces = len(board_places)

#this is a convenience function for getting board space object from their space number
def clear_screen():
    screen_height = 30
    for i in range(screen_height):
        print("")
    
def print_choice(a_list, question):
    n = 1
    for an_item in a_list:
        i_text = '  ' + str(n) + ') '
        if type(an_item) is Property or type(an_item) is RentalProperty:
            i_text = i_text + an_item.title
        elif type(an_item) is Player or type(an_item) is HumanPlayer:
            i_text = i_text + an_item.piece
        elif type(an_item) is str:#this is for string items
            i_text = i_text + an_item
        else:
            i_text = i_text + an_item.__str__()
        print(i_text)
        n = n + 1
    answer = question_loop(question)
    while answer < 1 or answer > len(a_list):
        answer = question_loop(question)
    else:
        return a_list[answer - 1]


#this is a convenience method for when someone puts in the wrong text.  It just loops back to the same question until they put in the right text
def question_loop(question):
    while True:
        choice = input(question)
        if type(choice) is str:
            if choice.isdigit():
                choice = int(choice)
                if choice >= 0:
                    return choice #this is the correct output
            elif choice == "quit":
                quit()#this shoud force terminate program

#this is the basic decision making method that this object will use
def decision(odds):
    to_beat = random.randint(1, 10)
    if odds > to_beat:
        return True
    else:
        return False

def exchange_property(first_player, first_player_offer, second_player, second_player_offer):
    #first player stuff
    for first_player_prop in first_player_offer:
        if type(first_player_prop) is Property or type(first_player_prop) is RentalProperty:
            first_player.give_property(first_player_prop, second_player)
        elif type(first_player_prop) is int:
            first_player_money = first_player_prop
            first_player.give_money(second_player, first_player_money) 
    #second player stuff
    for second_player_prop in second_player_offer:
        if type(second_player_prop) is Property or type(second_player_prop) is RentalProperty:
            second_player.give_property(second_player_prop, first_player)
        elif type(second_player_prop) is int:
            second_player_money = second_player_prop
            second_player.give_money(first_player, second_player_money)

#buy_ methods buy from the game or bank
#give_ methods gives to another player and should be used for exchanging property
#move_to_ methods will move player on game board

#this computer player will be the typical cmputer player.  Other versions of types such as timid types can 
#be created later by overiding decision making methods.
class Player:
    piece = None
    money = 1500#this is to offset the initial loop it is 1500 by game rules
    houses = 0
    hotels = 0
    space_number = 0 
    in_jail = False
    out_of_jail_card = False
    out_of_jail_rolls = 0

    def __init__(self, p):
        self.piece = p
        self.properties = [] #this has to be here in order for each list to be associated with each seperate player instance

    def __str__(self):
        return self.piece
            
    def status(self, status_message):
        message_roll = str(Die.rolls)
        return f"{str(turns)}>{self}\{message_roll}\{self.space()}\${self.money}\{status_message}"

    def give_money_to_bank(self, amount):
        self.money = self.money - amount

    def give_money(self, other_player, amount):
        self.money = self.money - amount
        other_player.money = other_player.money + amount
    
    def give_property(self, prop, other_player):
        prop.owner = other_player
        self.properties.remove(prop)
        other_player.properties.append(prop)

    def buy_property(self, prop):
        prop.owner = self
        self.money = self.money - prop.price
        self.properties.append(prop)

    def buy_house(self, prop):
        if self.money > prop.house_cost:
            prop.buy_house(self)
            self.money = self.money - prop.house_cost

    def space(self):
        return board_places[self.space_number]

    def move(self, p):
        self.space_number = self.space_number + p
        if self.space_number > total_spaces - 1:#this is for when player passes go
            self.space_number -= total_spaces
            self.money = self.money + money_pass_go
    
    def move_to(self, new_space):
        if new_space is not None:
            if self.space_number > new_space:
                self.money = self.money + money_pass_go #this is for when it passes go
            self.space_number = new_space

    def move_to_jail(self):
        self.space_number = space_jail
        self.in_jail = True
        self.jail_dice_roll = 0

    def move_to_go(self):
        self.space_number = space_go
        self.money = self.money + money_pass_go
    
    def turn(self):
        self.move(Die.last_roll)
        self.space().do_to(self)

    def use_card(self):
        self.in_jail = False
        self.out_of_jail_card = False
        self.jail_dice_roll = 0

    def pay_fine(self):
        self.in_jail = False
        self.give_money_to_bank(jail_bail)
        self.jail_dice_roll = 0

    def roll_for_doubles(self):
        Die.roll()
        if (Die.is_doubles()):
            self.in_jail = False
            self.move(Die.last_roll)
        else:
            self.out_of_jail_rolls = self.out_of_jail_rolls + 1
            if self.out_of_jail_rolls > 2:
                self.in_jail = False
                self.out_of_jail_rolls = 0


    def is_bankrupt(self):
        if self.money < 1:
            return True
        else:
            return False
   
    #I'm not sure about the official rules of the game for this
    def quit_game(self):
        for a_prop in self.properties:
            a_prop.owner = None
        try:
            players_all.remove(self)
        except: 
            pass#this is just temporary until I figure out how to deal with this

    #these are specific actions that are unique for human and computer players and must be written for each
    def ask_trade(self, player_offer, other_player, other_player_offer):
        trade_decision = decision(5)#standard percent
        for other_player_prop in other_player_offer:
            other_player_prop_type = type(other_player_prop)
            for player_prop in player_offer:
                player_prop_type = type(player_prop)
                if other_player_prop_type is Property or other_player_prop_type is RentalProperty:
                    if player_prop_type is Property or player_prop_type is RentalProperty:
                        prop_value = board_places.index(player_prop)
                        other_player_prop_value = board_places.index(other_player_prop)
                        if prop_value + 10 < other_player_prop_value: 
                            trade_decision = decision(6)
                        elif prop_value > other_player_prop_value + 10: 
                            trade_decision = decision(3)
                    elif player_prop_type is int:
                        pass#I don't know what to do I just want it to compile
                elif other_player_prop_type is int:
                    if player_prop_type is Property or player_prop_type is RentalProperty:
                        if other_player_prop < player_prop.mortgage:
                            trade_decision = decision(2)
                        elif other_player_prop > player_prop.mortgage * 4:
                            trade_decision = decision(9)
                        elif other_player_prop > player_prop.mortgage * 3:
                            trade_decision = decision(8)
                        elif other_player_prop > player_prop.mortgage * 2:
                            trade_decision = decision(7)
                        elif other_player_prop > player_prop.mortgage * 1:
                            trade_decision = decision(6)
                        else:
                            trade_decision = decision(5)
                    elif player_prop_type is int:
                        pass#just f'n work

        if trade_decision:
            exchange_property(self, player_offer, other_player, other_player_offer)
            print(self.status(f"{self} agreed to trade with you"))
        else:
            print(self.status(f"{self} did not want to trade with you"))

    def land_on_property(self, prop):
        message = None
        if prop.owner is not self:
            if prop.owner is None:
                if self.money > prop.price:
                    if prop.title == "Boardwalk":
                        self.buy_property(prop)
                        message = f"{self} has bought {prop}"
                    elif decision(9) == True:
                        self.buy_property(prop)
                        message = f"{self} has bought {prop}"
                    else:
                        message = f"{self} has decided to not buy {prop}"
                else:
                    message = f"{self} could not afford to buy {prop}"
            else:
                rent_money = prop.rent_howmuch(self)
                self.give_money(prop.owner, rent_money)
                message = f"{self} has paid {str(rent_money)} in rent to {prop.owner} for staying at {prop}"
            print(self.status(message))

    def land_on_incometax(self):
        message = None
        if IncomeTax.tax_percent < IncomeTax.tax200:
            self.money = self.money - IncomeTax.tax_percent 
            message = f"{self} has paid {str(IncomeTax.tax_percent)} in income tax"
        else:
            self.money = self.money - IncomeTax.tax200
            message = f"{self} has paid {str(IncomeTax.tax200)} in income tax"
        print(player.status(message))
    
    def get_out_of_jail(self):

        if self.out_of_jail_card == True:
            self.use_card()
        else:
            if self.out_of_jail_rolls < 3:
                self.roll_for_doubles()
            elif self.money > jail_bail:
                self.pay_fine()

class HumanPlayer(Player, cmd.Cmd):
    
    def __init__(self, p):
        Player.__init__(self, p)
        cmd.Cmd.__init__(self, 'tab')
        self.prompt = self.piece

    def do_end_turn(self, arg):
        'this will end turn'
        return True

    def ask_trade(self, player_offer, other_player, other_player_offer):
        question = f"{other_player} wants to trade {player_offer} for {other_player_offer}"
        answer = print_choice(["Yes", "No"], question)
        if answer == "Yes":
            exchange_property(self, player_offer, other_player, other_player_offer)
            print(self.status(f"{other_player} has accepted your offer."))
        else:
            print(self.status(f"{other_player} has declined your offer."))

    def land_on_property(self, prop):
        if prop.owner is not self:
            if prop.owner is not None:
                rent_money = prop.rent_howmuch(self)
                self.give_money(prop.owner, rent_money)
            self.print_player_menu()

    def land_on_incometax(self):
        question = f"> What does {self.piece} wish to pay? "
        pay_tax = print_choice([IncomeTax.tax_percent, IncomeTax.tax200], question)
        self.money = self.money - pay_tax
        message = f"{self} has paid {str(pay_tax)} in income tax"
        print(player.status(message))

    def get_out_of_jail(self):
        
        while True:
            jail_choices = None
            if self.out_of_jail_card is False:
                jail_choices = (
                    TradeChoice(),
                    MortgageChoice(),
                    UnmortgageChoice(),
                    BuyHouseChoice(),
                    PlayerAssetChoice(),
                    QuitGameChoice(),
                    #CardChoice(),
                    PayChoice(),
                    RollChoice()
                    )
            elif self.out_of_jail_card is True:
                jail_choices = (
                    TradeChoice(),
                    MortgageChoice(),
                    UnmortgageChoice(),
                    BuyHouseChoice(),
                    PlayerAssetChoice(),
                    QuitGameChoice(),
                    CardChoice(),
                    PayChoice(),
                    RollChoice()
                    )
            jail_choice = print_choice(jail_choices, "What do you want to do in jail? ")          
            jail_choice.do_to(self)
            if type(jail_choice) is CardChoice or type(jail_choice) is PayChoice or type(jail_choice) is RollChoice:
                break
    
    def print_player_menu(self):
        while True:
            player_choices = ()
            question = "what does " + str(self) + " want to do? "
            answer = 0
            if self.space().owner == None:
                player_choices = (
                        BuyChoice(self.space()),
                        TradeChoice(),
                        MortgageChoice(),
                        UnmortgageChoice(),
                        BuyHouseChoice(),
                        PlayerAssetChoice(),
                        QuitGameChoice(),
                        EndChoice()
                        )
            else:
                player_choices = (
                        TradeChoice(),
                        MortgageChoice(),
                        UnmortgageChoice(),
                        BuyHouseChoice(),
                        PlayerAssetChoice(),
                        QuitGameChoice(),
                        EndChoice()
                        )
                
            player_choice = print_choice(player_choices, question)
            player_choice.do_to(self)
            if type(player_choice) is EndChoice:
                break


#Actual Beginning of the game
print("""   
            M     M               PPPP     PPPP     L  Y   Y
            M M M M OOO NN  N OOO P  P OOO P  P OOO L   Y Y
            M  M  M O O N N N O O PPPP O O PPPP O O L    Y
            M     M OOO N  NN OOO P    OOO P    OOO LLL  Y
            """)

players_human_max = question_loop("How many human players do you want? ")
for h in range(players_human_max):
    player_piece = print_choice(total_pieces, "what piece do you want to be? ")
    total_pieces.remove(player_piece)
    players_all.append(HumanPlayer(player_piece))#this appends human player

players_computer_max = question_loop("How many COMPUTER players do you want? ")
for n in range(players_computer_max):
    player_piece = random.choice(total_pieces)
    total_pieces.remove(player_piece)
    players_all.append(Player(player_piece))
    
#actual game loop
if len(players_all) > 0:
    turns = 0
    while len(players_all) > 1:
        turns = turns + 1
        for player in players_all:
            if player.in_jail is False:
                Die.roll()
                player.turn()
                if Die.is_doubles() is True and player.in_jail is False:
                    Die.roll()
                    player.turn()
                    if Die.is_doubles() is True and player.in_jail is False:
                        Die.roll()
                        if Die.is_doubles() is True:#this is going to jail on third roll
                            player.move_to_jail()
                        else:
                            player.turn()
            else:
                player.space().do_to(player)#this will call the in jail function

            if player.is_bankrupt():
                message = f"{player}<---game is over because they are bankrupt!!!"
                players_all.remove(player)
                print(player.status(message))

        next_turn = input(str(turns) + ": Do you wish to continue? Y or N ")
        if next_turn == "N":
            break
    else:
        #this is the winner's graphic
        print(f"{players_all[0].piece} has won")

#this is the end of game
print("Thank you for playing mono-poly")
