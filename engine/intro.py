"""Intro sequence and ASCII art."""

import time
from engine.terminal import C, styled


def show_intro():
    print("\033[2J\033[H", end="", flush=True)

    skull = r"""
                      ______
                   .-"      "-.
                  /            \
                 |              |
                 |,  .-.  .-.  ,|
                 | )(__/  \__)( |
                 |/     /\     \|
                 (_     ^^     _)
                  \__|IIIIII|__/
                   | \IIIIII/ |
                   \          /
                    `--------`
"""
    for line in skull.split('\n'):
        if line.strip():
            print(styled(line, C.RED))
            time.sleep(0.08)

    time.sleep(0.5)

    lines = [
        (styled("\n  In an age of shadow and ruin...", C.DIM, C.WHITE), 1.2),
        (styled("  The realm has fallen to darkness.", C.DIM, C.WHITE), 1.0),
        (styled("  Ancient evils stir in forgotten places.", C.WHITE), 1.0),
        (styled("  A dragon of terrible power has awakened.", C.RED), 1.2),
    ]
    for line, delay in lines:
        print(line)
        time.sleep(delay)

    dragon = r"""
                           ______________
                     ,===:'.,            `-._
                          `:.`---.__         `-._
                            `:.     `--.         `.
                              \.        `.         `.
                      (,,(,    \.         `.   ____,-`.,
                   (,'     `/   \.   ,--.___`.'
               ,  ,'  ,--.  `,   \.;'         `
                `{D, {    \  :    \;
                  V,,'    /  /    //
                  j;;    /  ,' ,-//.    ,---.      ,
                  \;'   /  ,' /  _  \  /  _  \   ,'/
                         \   `'  / \  `'  / \  `.' /
                          `.___,'   `.__,'   `.__,'
"""
    print()
    for line in dragon.split('\n'):
        if line.strip():
            print(styled(line, C.RED))
            time.sleep(0.05)

    time.sleep(0.5)

    lines2 = [
        (styled("\n  Its shadow stretches across the dying land.", C.RED), 1.0),
        (styled("\n  But one soul remains...", C.YELLOW), 1.5),
        (styled("  A lone wanderer. Scarred. Determined. Unyielding.", C.YELLOW), 1.2),
        (styled("\n  You.", C.BOLD, C.WHITE), 2.0),
    ]
    for line, delay in lines2:
        print(line)
        time.sleep(delay)

    sword = r"""
                         /\
                        /  \
                       /    \
                      /  **  \
                     /________\
                         ||
                         ||
                         ||
                        _||_
                       |    |
                       |____|
"""
    for line in sword.split('\n'):
        if line.strip():
            print(styled(line, C.YELLOW))
            time.sleep(0.06)

    lines3 = [
        (styled("\n  The King awaits at the capital.", C.DIM), 0.8),
        (styled("  The quest will find you.", C.DIM), 2.0),
    ]
    for line, delay in lines3:
        print(line)
        time.sleep(delay)

    print()
    try:
        input(styled("  Press Enter to begin your journey...", C.BOLD, C.YELLOW))
    except (EOFError, KeyboardInterrupt):
        pass
