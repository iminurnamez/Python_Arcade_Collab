"""
The main function is defined here. It creates an instance of
Control and starts up the main program.
"""

import cProfile
import pstats

import data.core.control

# Importing prepare sets up the screen and processes command line arguments.
from data.core import prepare


def main():
    """
    Creates an instance of our primary application, initializes some
    things based on supplied command line arguments, and starts the program.
    Use argument -h for details on accepted arguments.
    """
    default_state = "snake_splash"
    straight = prepare.ARGS['straight']
    state = straight or default_state
    app = data.core.control.Control()
    app.show_fps = prepare.ARGS["FPS"]
    app.start(state)
    if not prepare.ARGS['profile']:
        app.main()
    else:
        # Run with profiling turned on - produces a 'profile' file
        # with stats and then dumps this to the screen.
        cProfile.runctx('app.main()', globals(), locals(), 'profile')
        p = pstats.Stats('profile')
        p.sort_stats('cumulative').print_stats(100)
