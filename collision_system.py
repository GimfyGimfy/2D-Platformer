import pygame
from entities.player import Player
from level import Level
from game_states.state_manager import StateManager
from constants import COLORS

class CollisionSystem: #check for touching objects
    @staticmethod
    def handle_collisions(player: Player, level: Level, state_manager: StateManager) -> None:
        teleporters = pygame.sprite.spritecollide(player, level.teleporters, False)
        if teleporters:
            teleporter=teleporters[0]
            state_manager.pop_state()
            from game_states.story import GameStateStory
            state_manager.push_state(GameStateStory(state_manager, teleporter.target_level))

        if pygame.sprite.spritecollide(player, level.spikes, False):
            player.reset_position()

        for orb in pygame.sprite.spritecollide(player, level.orbs, False):
            if orb.active and player.charged == False:
                orb.deactivate()
                player.charged = True
                player.image.fill(COLORS["GREEN"])
        level.active_sign = None
        for sign in level.signs:
            distance = pygame.math.Vector2(sign.rect.center).distance_to(player.rect.center)
            if distance < sign.detection_radius:
                level.active_sign = sign
                break
