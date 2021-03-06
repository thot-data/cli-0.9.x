from argparse import ArgumentParser

# import commands
from .commands.run import Run
from .commands.utils import Utils


def main():
    parser = _get_cmdline_parser()
    args = parser.parse_args()

    args._fn( args )


def _get_cmdline_parser():
    parser = ArgumentParser( description = 'thot' )
    subparsers = parser.add_subparsers()

    cmd_parser = subparsers.add_parser( 'run', description = 'Thot project runner.' )
    Run( cmd_parser )

    cmd_parser = subparsers.add_parser( 'utils', description = 'Thot utilities.' )
    Utils( cmd_parser )

    return parser
