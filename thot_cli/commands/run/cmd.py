import os
import sys
import json

from ..command import Command
from . import runner


py_version = sys.version_info.major + 0.1* sys.version_info.minor


class Run( Command ):
    """
    Thot utilities commands.
    """

    def run( self, args ):
        """
        """

        scripts = json.loads( args.scripts ) if args.scripts else None

        if py_version >= 3.7:
            # tasks
            if args.tasks is False:
                # tasks not provided
                tasks = None

            else:
                # tasks provided
                tasks = self.parse_optional_int_arg( args.tasks )
                if tasks is True:
                    # default value
                    tasks = 16

            runner.run(
                os.path.abspath( args.root ),
                scripts       = scripts,
                tasks         = tasks,
                ignore_errors = args.ignore_errors,
                verbose       = args.verbose
            )

        else:
            multithread  = self.parse_optional_int_arg( args.multithread )
            multiprocess = self.parse_optional_int_arg( args.multiprocess )

            runner.run(
                os.path.abspath( args.root ),
                scripts       = scripts,
                ignore_errors = args.ignore_errors,
                multithread   = multithread,
                asynchronous  = vars( args )[ 'async' ],  # must retrieve as dictionary because async is reserved keyword.
                multiprocess  = multiprocess,
                verbose       = args.verbose
            )


    def init_parser( self, parser ):
        """
        Initializes an ArgumentParser for the `run` command.

        :returns: Run parser.
        """
        parser.add_argument(
            '-r', '--root',
            type = str,
            default = '.',
            help = 'Path or ID of the root Container.'
        )

        # TODO [1]
    #     parser.add_argument(
    #         '-s', '--search',
    #         type = str,
    #         help = 'Search filter for Containers to run. Exclude for all.'
    #     )

        # TODO [1]
    #     parser.add_argument(
    #         '-d', '--depth',
    #         type = number,
    #         help = 'Maximum depth of the tree to run. Exclude for all.'
    #     )

        parser.add_argument(
            '--scripts',
            type = str,
            help = 'List of scripts to run. Exclude for all.'
        )

        parser.add_argument(
            '--ignore-errors',
            action = 'store_true',
            help = 'Ignore exceptions, continuing evaluation.'
        )

        parser.add_argument(
            '--verbose',
            action = 'store_true',
            help = 'Print evaluation information.'
        )


        if py_version < 3.7:
            parser.add_argument(
                '--multithread',
                nargs = '?',
                default = False,
                action = 'store',
                help = 'Execute tree using multiple threads. CAUTION: May lock system, can not force quit.'
            )

            parser.add_argument(
                '--async',
                action = 'store_true',
                help = 'Execute tree asynchronously. CAUTION: May lock system, can not force quit.'
            )

            parser.add_argument(
                '--multiprocess',
                nargs = '?',
                default = False,
                action = 'store',
                help = 'Execute tree using multiple processes. CAUTION: May lock system, can not force quit.'
            )

        else:
            parser.add_argument(
                '-t', '--tasks',
                nargs = '?',
                default = False,
                action = 'store',
                help = 'Limit the number of concurrent tasks. If flag is not provided no limit is used. If flag is provided but no value is given, default values is 16.'
            )

        return super().init_parser( parser )
        # parser.set_defaults( _fn = self.run )
        # return parser


    @staticmethod
    def parse_optional_int_arg( arg ):
        """
        Parses an argument value if it takes an optional integer argument.

        :param arg: Argument value.
        :returns: True if arg is None, False is arg is False, arg as integer otherwise.
        """
        if arg is None:
            # indicates flag was present, but no value passed
            return True

        if arg is False:
            return False

        return int( arg )
