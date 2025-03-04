import Environment as Env

from .AAddReactionStrategy import AAddReactionStrategy
from .ATransformer import ATransformer
from Chemistry.Entities.AAutocatSet import AAutocatSet
from Chemistry.Entities.ACRS import ACRS
from Performance.Decorators import time_function

from abc import abstractmethod
from logging import getLogger
from math import floor, log10
from random import randrange
from time import time


class ASubsetifier(ATransformer):
    """
    Class to build an autocatalytic subset from a starting Chemical Reaction System (CRS) by adding reactions in steps
    """


    LOGGER = getLogger(__name__)
    

    def __init__(self, transforming_CRS:ACRS, strategy:AAddReactionStrategy, reactions_goal:int=0) -> None:
        """
        Initializer
        
        Aims to build an autocatalytic subset passing through an intermediate CRS with a certain number of reactions;
        two criteria can be followed to construct the intermediate CRS:
        1. the aim is to build an autocatalytic set with the minimal number of reactions,
        in this case the algorithm verifies if an autocatalytic set is present at every n reactions added to the intermediate CRS;
        2. the aim is to build an autocatalytic set after a specific number of reactions has been added to the intermediate system.
        
        :param transforming_CRS: the starting CRS, which is not modified
        :param reactions_goal: the number of reactions requested to be in the intermediate CRS;
        if the value of this argument is different than 0, then criterion 2 is adopted;
        instead, if the argument is 0 or it exceeds the reactions upper bound, criterion 1 is adopted.
        :return: None
        """

        super().__init__(transforming_CRS)

        self.strategy = strategy
        """The strategy to add reactions to the system"""
        self.strategy.calibrate(self._CRS)
        
        self.subset_class:AAutocatSet = None
        """The class corresponding to the subset type required"""
        self._init_subset_class()

        # check the reactions goal, if set, against the upper bound of the maximum number of reactions
        if not reactions_goal < self.strategy.n_react_upper_bound:
            self.LOGGER.warning(
                f"Reactions goal of {reactions_goal} not reachable with a max number of reactions of {self.strategy.n_react_upper_bound}, "
                "stopping adding reactions at the first autocat set found")
            reactions_goal = 0
        self.reactions_goal = reactions_goal
        """The reactions goal requested"""

        self._reactions_created = 0
        """Counter for reactions created"""

        self._set_divisor()
        """
        Divisor used to prompt an autocat presence check in case criterion 1:
            the check is run only when the reactions added by the alchemist are a multiple of the divisor,
            and the divisor is increment dinamically with the number of total reactions
        """
        self._subset = None
        """The subset resulting from transformation"""


    @abstractmethod
    def _init_subset_class(self) -> None:
        """Initialize subset class"""
        pass


    def _set_divisor(self) -> None:
        """Set the divisor used in criterion 1 to prompt autocat set check presence"""
        curr_n_react = len(self._CRS.get_all_reactions())
        self.divisor = 10 if curr_n_react == 0 else 10**floor(log10(curr_n_react))

    
    def getSubset(self) -> AAutocatSet|None:
        """
        Get the autocatalytic set produced with transformation

        :return: the produced autocatalytic set, or None if transformation failed or was not performed
        """
        return self._subset
    

    @time_function
    def transform(self) -> ACRS|None:
        """
        Tries to transform the CRS into a new one which is also an autocatalytic set by iteratively adding reactions to the system
        
        :return: a new chemical reaction system which is an autocatalytic set, or None if the generation was not successfull
        """
        
        # check if the system already contains a subset
        try:
            self._subset = self.subset_class(self._CRS)
        except ValueError as err:
            self.LOGGER.info(err.args[0])
        try_add = False if self._subset != None else True

        CRS_exhausted = False
        self.LOGGER.info(
            f"Started transformation, goal = {self.reactions_goal}, "
            f"max N of reactions = {self.strategy.n_react_upper_bound}")
        ###
        start = time()
        while (try_add):
            attempt_subset_creation = False
            n_react_added = self.strategy.apply()
            if n_react_added > 0:
                self.LOGGER.info(f"{n_react_added} reactions added to the CRS")
                self._reactions_created += n_react_added
            else:
                # if the reaction addition fails, it can be assumed the system is unlikely to host any more reactions
                self.LOGGER.info("No more reactions can be added to the CRS")
                CRS_exhausted = True
            if CRS_exhausted:
                attempt_subset_creation = True
            # check if a reaction goal was set
            if self.reactions_goal > 0:
                # if it is set, criterion 2 is adpoted, so the autocatalytic set is created only before exiting the cycle
                if self._reactions_created == self.reactions_goal:
                    self.LOGGER.info(f"Reaction goal of {self.reactions_goal} was met")
                    attempt_subset_creation = True
            elif self._reactions_created > 0 and self._reactions_created%self.divisor == 0:
                # if it is not set, criterion 1 is adopted, and an autocat set creation is attempted every time a reaction is added
                # if a reaction is never added there can be no autocat set in the system and the subset remains empty
                self._set_divisor()
                attempt_subset_creation = True
            # check the new CRS for the presence of an autocatalytic set
            if attempt_subset_creation:
                ### performance check
                self.LOGGER.info(
                    f"Attempting autocatalytic set creation at {self._reactions_created} reactions added "
                    f"(upper bound = {self.strategy.n_react_upper_bound})")
                end=time()
                if end-start > Env.MAX_WTIME:
                    time_elapsed = '%.2f' % (end-start)
                    self.LOGGER.warning(f"{time_elapsed} seconds to add new reactions")
                try:
                    ### performance check
                    start = time()
                    self._subset = self.subset_class(self._CRS)
                    end = time()
                    if end-start > Env.MAX_WTIME:
                        time_elapsed = '%.2f' % (end-start)
                        self.LOGGER.warning(f"{time_elapsed} seconds to check autocatalytic set presence")
                except ValueError as err:
                    self.LOGGER.info(err.args[0])
                start=time()
                if self._subset != None or self._reactions_created == self.reactions_goal:
                    try_add = False
            if CRS_exhausted:
                try_add = False

        self.LOGGER.info(f"New non-inert CRS built with {self._reactions_created} reactions\n{self._CRS.to_string()}")
        if self._subset != None:
            self.LOGGER.info(f"An autocatalytic set with {len(self._subset.reaction_set)} reactions is present")
            return self._CRS
        else:
            return None
