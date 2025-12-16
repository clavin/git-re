from args import Args
import sys


class Log:
    """
    Simple "print" wrapper.

    Supports info, error, and debug messages. Debug messages are only printed if
    verbose mode is enabled.
    """

    def __init__(self, args: Args) -> "Log":
        self.verbose = args.verbose or args.dry_run

    def info(self, *args, **kwds):
        """Informational message."""
        print(*args, **kwds)

    def error(self, *args, **kwds):
        """Error message."""
        print(*args, file=sys.stderr, **kwds)

    def debug(self, *args, **kwds):
        """Debug message. Only printed if verbose mode is enabled."""
        if self.verbose:
            print(*args, **kwds)
