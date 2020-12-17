#!/usr/bin/env python
# coding: utf-8

# # Runner Local

# In[ ]:


import os
import sys
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor

from thot_core.runner import Runner
from thot_core.classes.container import Container

from .db.local import LocalDB


# In[ ]:


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
        Runner.__init__( self )
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
            script_id = os.path.normpath( # path to script
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
            root = self.db.containers.find_one( { '_id': _id } )

            if root is None:
                raise Error( 'Could not find Container at {}.'.format( _id ) )

            return root

        return _get_container


# In[ ]:


def run( root, **kwargs ):
    """
    Runs programs bottom up for local projects.
    
    :param root: Path to root.
    :param kwargs: Arguments passed to #eval_tree 
    """
    db = LocalDB( root )
    runner = LocalRunner( db )    
    
    # parse scripts if present
    if (
        ( 'scripts' in kwargs ) and 
        ( kwargs[ 'scripts' ] is not None )
    ):
        kwargs[ 'scripts' ] = [ db.parse_path( path ) for path in kwargs[ 'scripts' ] ]
    
    runner.eval_tree( root, **kwargs )


# In[ ]:


if __name__ == '__main__':
    """
    Runs a Thot Project from console.
    """
    from argparse import ArgumentParser
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
        '--multithread',
        action = 'store_true',
        help = 'Execute tree using multiple threads. CAUTION: May lock system, can not force quit.'
    )
    
    parser.add_argument(
        '--verbose',
        action = 'store_true',
        help = 'Print evaluation information.'
    )
       
    args = parser.parse_args()
    
    scripts = json.loads( args.scripts ) if args.scripts else None

    run( 
        os.path.abspath( args.root ), 
        scripts       = scripts,
        ignore_errors = args.ignore_errors, 
        multithread   = args.multithread,
        verbose       = args.verbose 
    )


# # Work
