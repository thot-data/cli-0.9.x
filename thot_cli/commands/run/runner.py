#!/usr/bin/env python
# coding: utf-8

# Runner Local

import os
import sys
import logging

from thot_core import Runner
from thot_core.runners.runner_multithread import Runner as RunnerMultithread

from thot.db.local import LocalDB


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
