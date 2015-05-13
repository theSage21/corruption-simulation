import random
from itertools import combinations


class Person:
    mu = 0.5
    sigma = 0.2
    initial_amount = 100
    max_money = 100
    max_children = 5

    def __init__(self, police=False, criminal=False, stoicity=None):
        if stoicity is None:
            self.stoicity = random.gauss(Person.mu, Person.sigma)
        else:
            self.stoicity = stoicity
        self.police = police
        self.criminal = criminal
        self.money = Person.initial_amount

    def update_money(self, change):
        self.money += change
        if self.money < 0:
            self.money = 0
        if self.money > Person.max_money:
            Person.max_money = self.money

    def get_children(self):
        fraction = self.money / Person.max_money
        children_needed = int(fraction * Person.max_children)
        children = []
        for i in range(children_needed):
            child = Person(self.police, self.criminal, self.stoicity)
            children.append(child)
        return children

    def __update_stoicity(self, increase):
        fraction = self.stoicity * random.random()
        if increase:
            self.stoicity += fraction
        else:
            self.stoicity -= fraction

    def give_bribe(self):
        mark = random.random()
        if mark < self.stoicity:
            # honest
            self.__update_stoicity(True)
            return False
        else:
            # dishonest
            self.__update_stoicity(False)
            return True

    def take_bribe(self):
        mark = random.random()
        if mark < self.stoicity:
            # honest
            self.__update_stoicity(True)
            return False
        else:
            # dishonest
            self.__update_stoicity(False)
            return True


class Society:
    def __init__(self,
                 pop_size,
                 criminal_fraction,
                 police_fraction,
                 reproduction_step,
                 criminal_fine,
                 police_reward,
                 bribe_fine
                 ):
        self.pop_size = pop_size
        self.criminal_fraction = criminal_fraction
        self.police_fraction = police_fraction
        self.reproduction_step = reproduction_step
        self.criminal_fine = criminal_fine
        self.police_reward = police_reward
        self.bribe_fine = bribe_fine
        # datastructures
        self.population = self.__generate_population()
        self.__initiate_counters()
        self.time = 0

    def run(self):
        self.time = 0
        print('time|pop|pol|cri|sit|of_c|of_n|of_p|br_ac|inter')
        for i in range(1000):
            self.__iteration()

    def __initiate_counters(self):
        self.bribe_situations = 0
        self.bribe_offers_c = 0
        self.bribe_offers_n = 0
        self.bribe_offers_p = 0
        self.bribe_accepted = 0
        self.interactions = 0

    def __record_state_of_population(self):
        time = self.time
        pop = self.pop_size
        pol = sum((1 for i in self.population if i.police))
        crim = sum((1 for i in self.population if i.criminal))
        sit = self.bribe_situations
        of_c = self.bribe_offers_c
        of_n = self.bribe_offers_n
        of_p = self.bribe_offers_p
        br_ac = self.bribe_accepted
        inter = self.interactions
        print('%d|' * 10 % (time, pop, pol, crim, sit, of_c, of_n, of_p, br_ac, inter))

    def __determine_briber(self, org1, org2):
        if not org1.police:  # org1 not police
            briber, police = org1, org2
        elif not org2.police:  # org2 not police
            briber, police = org2, org1
        elif org1.police and org2.police:
            pair = [org1, org2]
            random.shuffle(pair)
            briber, police = pair
        return briber, police

    def __calculate_transaction(self, bribe_given, bribe_accepted, briber_criminal):
        briber_update, police_update = 0, 0
        if not bribe_given:
            if briber_criminal:
                briber_update, police_update = -self.criminal_fine, self.police_reward
        else:
            # bribe corrupt officer
            briber_update, police_update = self.bribe_fine, self.bribe_fine
            # bribe honest officer
            briber_update, police_update = self.bribe_fine, self.police_reward
            pass
        return briber_update, police_update

    def __iteration(self):
        self.__initiate_counters()
        # Round robin tournament
        for org1, org2 in combinations(self.population, 2):
            self.interactions += 1
            if org1.police or org2.police:
                self.bribe_situations += 1
                # determine who must bribe whom
                briber, police = self.__determine_briber(org1, org2)
                bribe_given, bribe_accepted = False, False
                # ask bribe if he wants to bribe
                if briber.give_bribe():
                    bribe_given = True
                    if briber.criminal:
                        self.bribe_offers_c += 1
                    elif not briber.criminal:
                        self.bribe_offers_n += 1
                    if briber.police:
                        self.bribe_offers_p += 1
                    # ask if police accepts
                    if police.take_bribe():
                        bribe_accepted = True
                        self.bribe_accepted += 1
                briber_update, police_update = self.__calculate_transaction(bribe_given, bribe_accepted, briber.criminal)
                briber.update_money(briber_update)
                police.update_money(police_update)
        self.__record_state_of_population()
        if self.time % self.reproduction_step == 0:
            self.__reproduce_population()
        self.time += 1

    def __reproduce_population(self):
        new_pop = []
        for org in self.population:
            children = org.get_children()
            new_pop.extend(children)
        self.pop_size = len(new_pop)
        criminals = sum((1 for i in new_pop if i.criminal))
        police = sum((1 for i in new_pop if i.police))
        self.criminal_fraction = float(criminals) / self.pop_size
        self.police_fraction = float(police) / self.pop_size
        # simulate the random deaths by truncating 30 %
        random.shuffle(new_pop)
        mark = int(0.7 * self.pop_size)
        self.population = new_pop[:mark]

    def __generate_population(self):
        size = self.pop_size
        population = []
        for i in range(size):
            mark = random.random()
            if mark < self.criminal_fraction:
                criminal = True
            else:
                criminal = False
            mark = random.random()
            if mark < self.police_fraction:
                police = True
            else:
                police = False
            person = Person(police, criminal)
            population.append(person)
        return population

if __name__ == '__main__':
    soc = Society(100, 0.1, 0.1, 1, 5, 4, 6)
    soc.run()
