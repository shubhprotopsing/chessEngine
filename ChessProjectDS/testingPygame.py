import pygame


def setup():
    global screen, clock
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    clock = pygame.time.Clock()


def main():
    done = False
    isBlue = True
    while not done:
        screen.fill((0, 0, 0))
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                done = True
                print("Program quit")

            if e.type == pygame.KEYDOWN:
                isBlue = not isBlue

        print(isBlue)

        clock.tick(30)
        pygame.display.flip()

setup()
main()
