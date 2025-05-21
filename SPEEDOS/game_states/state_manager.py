from typing import List
from game_states.base import GameState

class StateManager:
    def __init__(self):
        self._states: List[GameState] = []
        self.resize_callback = None
    
    def push_state(self, state: GameState) -> None:
        self._states.append(state)
    
    def pop_state(self) -> None:
        if self._states:
            self._states.pop()
    
    @property
    def current_state(self) -> GameState:
        return self._states[-1] if self._states else None
        
    def set_resize_callback(self, callback):
        self.resize_callback = callback
        
    def on_resize(self):
        if self.resize_callback:
            self.resize_callback()