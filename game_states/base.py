from abc import ABC, abstractmethod
from typing import List
import pygame

#abstract base class defining the interface for all game states (menu, play, pause)
class GameState(ABC):
    @abstractmethod
    def handle_events(self, events: List[pygame.event.Event]) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        pass
