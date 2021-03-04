#!/usr/bin/env python
# coding: utf-8

# Runner Local

import os
import sys
import json
import logging

from thot_core import Runner
from thot_core.runners.runner_multithread import Runner as RunnerMultithread

from .db.local import LocalDB


class LocalRunner( Runner ):
    """
    Local project runner.
    """

    def __init__( self, db ):
        """
        Creates a new Local Runner.
        Registers built in hooks.

        :param db: Database to use.
        """
        super().__init__()
        self.db = db

        # register runner hooks
        self.register( 'get_container', self.get_container() )
        self.register( 'get_script_info', self.script_info() )


    def script_info( self ):
        """
        Creates a function to return a Script's id and path.
        Uses the Runner's database.

        :returns: Function that accepts a Script's id as input,
            and returns a tuple of ( <script id>, <script path> ).
        """

        def _script_info( script_id ):
            """
            Gets information for the Script.
            For use with thot_core.runner#eval_tree.

            :param script_id: Script id.
            :returns: Tuple of ( <script id>, <script path> ).
            """
            # local project script paths are prefixed by path id
            script_id = os.path.normpath(  # path to script
                os.path.join( self.db.root, script_id )
            )

            # script id and path are the same
            return ( script_id, script_id )

        return _script_info


    def get_container( self ):
        """
        Creates a Container getter function.
        Uses the Runner's database.

        :returns: Function that accepts a root id and returns the corresponding Container.
        """

        def _get_container( _id ):
            """
            Gets a Container by id.

            :param _id: Id of Container.
            :returns: Container.
            :raises: Error if Container is not found.
            """
            _id = os.path.normpath( _id )
            root = self.db.containers.find_one( { '_id': _id } )

            if root is None:
                raise RuntimeError( 'Could not find Container at {}.'.format( _id ) )

            return root

        return _get_container


class LocalRunnerMultithread( RunnerMultithread ):
    """
    Local project runner.
    """

    def __init__( self, db ):
        """
        Creates a new Local Runner.
        Registers built in hooks.

        :param db: Database to use.
        """
        super().__init__()
        self.db = db

        # register runner hooks
        self.register( 'get_container', self.get_container() )
        self.register( 'get_script_info', self.script_info() )


    def script_info( self ):
        """
        Creates a function to return a Script's id and path.
        Uses the Runner's database.

        :returns: Function that accepts a Script's id as input,
            and returns a tuple of ( <script id>, <script path> ).
        """

        def _script_info( script_id ):
            """
            Gets information for the Script.
            For use with thot_core.runner#eval_tree.

            :param script_id: Script id.
            :returns: Tuple of ( <script id>, <script path> ).
            """
            # local project script paths are prefixed by path id
            script_id = os.path.normpath(  # path to script
                os.path.join( self.db.root, script_id )
            )

            # script id and path are the same
            return ( script_id, script_id )

        return _script_info


    def get_container( self ):
        """
        Creates a Container getter function.
        Uses the Runner's database.

        :returns: Function that accepts a root id and returns the corresponding Container.
        """

        def _get_container( _id ):
            """
            Gets a Container by id.

            :param _id: Id of Container.
            :returns: Container.
            :raises: Error if Container is not found.
            """
            _id = os.path.normpath( _id )
            root = self.db.containers.find_one( { '_id': _id } )

            if root is None:
                raise RuntimeError( 'Could not find Container at {}.'.format( _id ) )

            return root

        return _get_container


def run( root, **kwargs ):
    """
    Runs programs bottom up for local projects.

    :param root: Path to root.
    :param kwargs: Arguments passed to #eval_tree
    """
    py_version = sys.version_info.major + 0.1* sys.version_info.minor

    db = LocalDB( root )
    runner = (
        LocalRunner( db )
        if py_version >= 3.7 else
        LocalRunnerMultithread( db )
    )

    if ( 'verbose' in kwargs ) and kwargs[ 'verbose' ]:
        logging.basicConfig( level = logging.INFO )

    # parse scripts if present
    if (
        ( 'scripts' in kwargs ) and
        ( kwargs[ 'scripts' ] is not None )
    ):
        kwargs[ 'scripts' ] = [ db.parse_path( path ) for path in kwargs[ 'scripts' ] ]

    if isinstance( runner, LocalRunner ):
        runner.eval_tree_sync( root, **kwargs )

    else:
        runner.eval_tree( root, **kwargs )


if __name__ == '__main__':
    """
    Runs a Thot Project from console.
    """
    from argparse import ArgumentParser

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

    py_version = sys.version_info.major + 0.1* sys.version_info.minor
    parser = ArgumentParser( description = 'Thot project runner for Python.' )

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


    args = parser.parse_args()
    scripts = json.loads( args.scripts ) if args.scripts else None

    if py_version >= 3.7:
        # tasks
        if args.tasks is False:
            # tasks not provided
            tasks = None

        else:
            # tasks provided
            tasks = parse_optional_int_arg( args.tasks )
            if tasks is True:
                # default value
                tasks = 16

        run(
            os.path.abspath( args.root ),
            scripts       = scripts,
            tasks         = tasks,
            ignore_errors = args.ignore_errors,
            verbose       = args.verbose
        )

    else:
        multithread  = parse_optional_int_arg( args.multithread )
        multiprocess = parse_optional_int_arg( args.multiprocess )

        run(
            os.path.abspath( args.root ),
            scripts       = scripts,
            ignore_errors = args.ignore_errors,
            multithread   = multithread,
            asynchronous  = vars( args )[ 'async' ], # must retrieve as dictionary because async is reserved keyword.
            multiprocess  = multiprocess,
            verbose       = args.verbose
        )
