import math
import pyxel  # Please refer to the following link for the documentation: https://github.com/kitao/pyxel
import random


# Handles the falling boulder
class Boulder:
    def __init__(self) -> None:  # '->' The return type to expect from a function
        # The x value for the boulder is set to randomly choose between a set range
        self.x = random.randrange(0, pyxel.width - 16)

        # Flag to register a collision with the player
        self.collision = False

        # The y value for the boulder
        self.y = 0

        # The default falling speed of the boulder
        self.fall_speed = 1

    # Draws the boulder to the screen
    def draw(self) -> None:
        # Draws the image created in the image editor to screen (usage: pyxel edit YOUR_FILENAME.pyxres)
        # x and y are the (x, y) values in the game window. Top left corner is (0, 0).
        # img refers to the image bank in the image editor
        # u and v refers to the (x, y) coordinates in the top right corner of the image editor
        # w and h sets the size of the image, each square is 8 by 8
        # colkey makes the specified colour appear transparent in game (anything WHITE appears transparent with below settings)
        pyxel.blt(
            x=self.x, y=self.y, img=1, u=16, v=16, w=16, h=16, colkey=pyxel.COLOR_WHITE
        )

    # Loads a boulder to screen at the given x and y values
    def spawn(self, x: int, y: int) -> None:
        pyxel.play(ch=0, snd=0)
        self.x = x
        self.y = y

    # Makes the boulder fall at the current fall speed
    def drop(self) -> None:
        self.y += self.fall_speed

    # Checks whether the boulder collides with the player
    def player_collision(self, x: int, y: int, player_x: int, player_y: int) -> bool:
        # Calculate the distance from the centre of the boulder and player using Pythagorean theorem
        distance_from_centre = math.sqrt(
            pow((x - player_x), 2) + pow((y - player_y), 2)
        )

        # Check if the distance from the centre of the boulder is within at least half the player width
        if distance_from_centre < 16:
            return True
        return False


# Handles the player
class Player:
    def __init__(self, x: int, y: int) -> None:
        # The x value for the player
        self.x = x

        # The default number of lives
        self.lives = 3

        # Flag to render player invulnerable to the boudler when true
        self.invulnerable = False

        # The y value for the player
        self.y = y

        # The direction the player is facing. Neutral = facing forward.
        self.direction = "neutral"

    # Handles the movement of the player.
    def move(self, key_left: int, key_right: int) -> None:
        # Checks if key left is pressed and moves the player to the left
        if pyxel.btn(key_left):
            self.x -= 2
            self.direction = "left"
            if not self.valid_position(x=self.x):
                self.x += 2

        # Checks if key right is pressed and moves the player to the right
        elif pyxel.btn(key_right):
            self.x += 2
            self.direction = "right"
            # If x value goes beyond boundaries, set the value to a valid position
            if not self.valid_position(x=self.x):
                self.x -= 2
        else:
            self.direction = "neutral"

    # Ensures player stays within the game boundaries
    def valid_position(self, x: int) -> bool:
        return 0 < x < pyxel.width - 15

    # Draws the player to the screen. Different sprite based on direction facing.
    def draw(self) -> None:
        if self.direction == "neutral":
            pyxel.blt(self.x, self.y, 1, 0, 0, 16, 16, pyxel.COLOR_WHITE)

        elif self.direction == "left":
            pyxel.blt(self.x, self.y, 1, 0, 16, -16, 16, pyxel.COLOR_WHITE)

        elif self.direction == "right":
            pyxel.blt(self.x, self.y, 1, 0, 16, 16, 16, pyxel.COLOR_WHITE)


# Handles the game
class BoulderBilk:
    def __init__(self) -> None:
        # Settings for the Pyxel application
        pyxel.init(width=180, height=150, title="Evade", fps=60)

        # Loads the Pyxel image/sound/music editor into the application
        pyxel.load("assets.pyxres")
        self.setup()
        pyxel.run(self.update, self.draw)

    # Initial setup for the game
    def setup(self) -> None:
        self.game_state = "running"
        self.score = 0
        self.boulder = Boulder()
        self.player = Player(x=pyxel.width * 0.5, y=pyxel.height - 16)

    # Handles game logic. Checks every frame for changes.
    def update(self) -> None:
        # Quits the application
        if pyxel.btn(key=pyxel.KEY_Q):
            pyxel.quit()

        # Resets the application to initial setup
        if pyxel.btnr(key=pyxel.KEY_R):
            self.setup()

        # Pauses or resumes the game
        if pyxel.btnr(key=pyxel.KEY_P):
            if self.game_state == "running":
                self.game_state = "paused"
            else:
                self.game_state = "running"

        # Checks for game updates if the game is running
        if self.game_state == "running":
            self.player.move(key_left=pyxel.KEY_A, key_right=pyxel.KEY_D)

            # If the boulder collides with the player game over
            if self.boulder.player_collision(
                x=self.boulder.x,
                y=self.boulder.y,
                player_x=self.player.x,
                player_y=self.player.y,
            ):

                # SFX for collision
                pyxel.play(ch=1, snd=1)

                # If the collision flag is false and the player is not invulnerable
                # take one life and make the player invulnerable during the rest
                # of the collision
                if not self.boulder.collision and not self.player.invulnerable:
                    self.boulder.collision = True
                    self.player.invulnerable = True
                    self.player.lives -= 1

            # If the boulder is not colliding set player invlunerability and
            # boulder collision flags to false
            else:
                self.player.invulnerable = False
                self.boulder.collision = False

            # Game over if player lives reach 0
            if self.player.lives == 0:
                self.game_state = "stopped"

            # If the boulder goes past the bottom of the screen, spawn another one
            if self.boulder.y > pyxel.height:
                self.score += 1
                self.boulder.spawn(
                    x=random.randrange(0, pyxel.width - 16),
                    y=0,
                )

                # Update the speed of the boulder after 5 points. Max speed is 5.
                if self.boulder.fall_speed < 5 and self.score % 5 == 0:
                    self.boulder.fall_speed *= 1.1

            # Drops the boulder
            self.boulder.drop()

    # Draws the game to the screen
    def draw(self) -> None:
        pyxel.cls(pyxel.COLOR_WHITE)
        self.display_info()
        if self.player.invulnerable:
            if pyxel.frame_count % 10 == 0:
                self.player.draw()
        else:
            self.player.draw()
        self.boulder.draw()

    # Displays the score, pause and gameover text
    def display_info(self) -> None:
        pyxel.text(
            x=pyxel.width * 0.025, y=10, s=f"SCORE: {self.score}", col=pyxel.COLOR_BLACK
        )

        pyxel.text(
            x=pyxel.width * 0.80,
            y=10,
            s=f"LIVES: {self.player.lives}",
            col=pyxel.COLOR_BLACK,
        )

        if self.game_state == "paused":
            pyxel.text(
                x=pyxel.width * 0.5 - 10,
                y=pyxel.height * 0.5,
                s="PAUSED",
                col=pyxel.COLOR_BLACK,
            )

        elif self.game_state == "stopped":
            pyxel.text(
                x=pyxel.width * 0.5 - 20,
                y=pyxel.height * 0.5,
                s="GAME OVER!",
                col=pyxel.COLOR_BLACK,
            )


if __name__ == "__main__":
    BoulderBilk()


# TODO: Increase the difficulty by adding more falling boulders
# TODO: Add power ups, power downs and bonus items to add complexity
