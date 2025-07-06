import abc
from typing import List, Dict, Optional

class BaseMemory(abc.ABC):
    """
    Abstract Base Class for all memory components.
    Defines the interface that all memory systems (STM, LTM, EpTM, Sensory) should implement.
    """

    @abc.abstractmethod
    def store_fact(self, fact_text: str, fact_type: str) -> str:
        """
        Stores a fact in memory.
        """
        pass

    @abc.abstractmethod
    def search_facts(self, query: str, fact_type: Optional[str] = None) -> List[Dict]:
        """
        Searches for facts in memory.
        """
        pass

    @abc.abstractmethod
    def get_facts_by_type(self, fact_type: str) -> List[Dict]:
        """
        Retrieves facts by type.
        """
        pass 