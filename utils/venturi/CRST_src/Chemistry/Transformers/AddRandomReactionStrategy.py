import Environment as Env

from .AAddReactionStrategy import AAddReactionStrategy
from Chemistry.Entities.Reaction import Reaction

from logging import getLogger
from math import log
from random import choice, choices


class AddRandomReactionStrategy(AAddReactionStrategy):
    """
    Class defining a strategy to add random reactions to an existing Chemical Reaction System (CRS)
    """


    LOGGER = getLogger(__name__)


    def apply(self) -> int:
        """
        Apply the strategy to add a random reaction to the current reaction system
        
        The reaction type, reagents, products and catalyzers are chosen randomly
        The strategy needs to be calibrated on a specific CRS before attempting to apply it
        :return: the number of reactions added;
            in case the call returns 0, it can be assumed the CRS can't hold any more reactions
        """

        if not self._can_be_applied():
            return 0
        
        new_reaction = None
        # choose the reactions type randomly with the weights specified
        r_type = choices(self.supported_react_types, self._weights)[0]
        self.LOGGER.debug(f"Reaction type {r_type} chosen")
        
        # calculate the maximum number of random creation attempts
        max_n_creation_attempts = self._max_rr_creation_attempts()
            
        # attempt to create a reaction only up to the maximum number of attempts
        n_attempts = 0
        for _ in range(max_n_creation_attempts):
            n_attempts += 1
            # define the catalysts, the number is chosen randomly in the catalysts number range specified via config
            catalyst_names = []
            n_catalysts = choice(range(self._cat_range[0], self._cat_range[1]+1))
            for _ in range(n_catalysts):
                catalyst_name = choice(self._catalyzers_names)
                catalyst_names.append(catalyst_name)
            self.LOGGER.debug(f"Catalysts chosen: {list(catalyst_names)}")
            if r_type in {Env.R_CLEAVE, Env.R_COND}:
                # get valid species names for condensations and cleavages
                for _ in range(len(self._CRS.get_all_species_names())**2):
                    name_A = choice(self._reactive_species_names)
                    name_B = choice(self._reactive_species_names)
                    if name_A+name_B in self._reactive_species_names:
                        break
                # disambiguate the reaction type
                if r_type == Env.R_CLEAVE:
                    new_reaction = Reaction([name_A+name_B, *catalyst_names], [name_A, name_B, *catalyst_names])
                else:
                    new_reaction = Reaction([name_A, name_B, *catalyst_names], [name_A+name_B, *catalyst_names])
            elif r_type == Env.R_EXCH:
                # get valid species names for exchanges
                name_C = None
                name_D = None
                ch_species_names_not_len1 = [name for name in self._reactive_species_names if len(name) > 1]
                max_name_len = max(len(name) for name in ch_species_names_not_len1)
                for _ in range(len(self._CRS.get_all_species_names())**2):
                    name_A = choice(ch_species_names_not_len1)
                    name_B = choice(ch_species_names_not_len1)
                    # split the two names
                    i, j = (choice(range(1, len(name_A))), choice(range(1, len(name_B))))
                    name_A_LR = [name_A[:i], name_A[i:]]
                    name_B_LR = [name_B[:j], name_B[j:]]
                    # combine casually the splitted names
                    # start by taking 2 random indexes from 0 and 1
                    name_C_indexes = [choice([0, 1]) for _ in range(2)]
                    # and getting their mirror indexes
                    name_D_indexes = [abs(i-1) for i in name_C_indexes]
                    # build the names
                    name_C = name_A_LR[name_C_indexes[0]]+name_B_LR[name_C_indexes[1]]
                    name_D = name_A_LR[name_D_indexes[0]]+name_B_LR[name_D_indexes[1]]
                    if (all((x in self._reactive_species_names and x not in {name_A, name_B} and len(x) <= max_name_len)
                            for x in {name_C, name_D})):
                        break

                new_reaction = Reaction([name_A, name_B, *catalyst_names], [name_C, name_D, *catalyst_names])

            else:   # eventual future reactions types
                break

            # if the new reaction already exists in the CRS restart
            if new_reaction != None and self._CRS.get_reaction(new_reaction.key) == None:
                break
            else:
                new_reaction == None

        ## add the reaction if it can be done
        if new_reaction != None:
            self.LOGGER.debug(
                f"New random reaction {new_reaction.key} found in {n_attempts}/{max_n_creation_attempts} maximum attempts")
            if self._CRS.add_reaction(new_reaction):
                return 1
            else:
                return 0
        else:
            self.LOGGER.debug(f"No random reaction found in {n_attempts}/{max_n_creation_attempts} maximum attempts")
            return 0


    def _max_rr_creation_attempts(self) -> int:
        """
        Calculate the maximum number of random reaction creation attempts

        Private method used by the strategy to define a maximum number of attempts that is coherent
        with the level of exhaustion of the system
        :return: the maximum number of random reaction creation attempts
        """
        
        # if the current number of reactions is equal to the upper bound, the system is exhausted
        # the check is necessary since the upper bound could be reached in some occasions and then the number of attempts
        # calculation would return a wrong value
        current_n_reactions = len(self._CRS.get_all_reactions())
        if current_n_reactions == self.n_react_upper_bound:
            return 0
        # the maximum number of attempts needs to keep track of the level of exhaustion of the system
        # in terms of ratio of reactions present on the upperbound
        level_of_exhaustion = current_n_reactions/self.n_react_upper_bound
        # an absolute minimum and maximum values for the number of creation attempts are also enforced
        MINNTRIES = 10
        MAXTRIES = int(self.n_react_upper_bound/10)
        # the reaction creation is like a roll of a dice, if the new reaction is not present in the system it is added,
        # instead if it corresponds to an already existing reaction, the choice was just a "failed" attempt;
        # this last event can be called "failing the roll" or "getting a bad roll"
        # and it is the base event for which a probability can be calculated
        base_fail_probability = max(level_of_exhaustion, 0.0001)
        # in order to find a suitable number N of rolls, a target fail probability is determined
        # which is the probability of getting N bad rolls consecutively
        target_fail_probability = float(1/(self.n_react_upper_bound*100))
        # the rolls are unrelated, so the probability of getting N bad rolls consecutively is base_fail_probability^N
        # to get N, a logarithm is used
        calculated_n_choice_attempts = int(log(target_fail_probability, base_fail_probability))
        ### debug TO BE REMOVED
        self.LOGGER.debug(
            f"CRS exhaustion = {current_n_reactions}:{self.n_react_upper_bound}, base fail chance = {base_fail_probability},"
            f" target fail chance = {target_fail_probability}, attempts = {calculated_n_choice_attempts}")
        max_n_creation_attempts = max(calculated_n_choice_attempts, MINNTRIES)
        if max_n_creation_attempts > MAXTRIES:
            max_n_creation_attempts = MAXTRIES
        return max_n_creation_attempts