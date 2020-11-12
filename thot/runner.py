
# coding: utf-8

# # Runner

# In[ ]:


import os
import sys
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor

from thot_core.runner import eval_tree
from thot_core.classes.container import Container

from .db.local import LocalDB


# In[ ]:


def script_info( root ):
    """
    Creates a function to return a Script's id and path.
    For use with thot_core.runner#eval_tree.
    
    :param root: Path to root Container.
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
            os.path.join( root, script_id )
        )

        # script id and path are the same
        return ( script_id, script_id )
    
    return _script_info 


def run_local( root, **kwargs ):
    """
    Runs programs bottom up for local projects.
    
    :param root: Path to root.
    :param kwargs: Arguments passed to #eval_tree 
    """
    db = LocalDB( root )

    # parse scripts if present
    if kwargs[ 'scripts' ] is not None:
        kwargs[ 'scripts' ] = [ db.parse_path( path ) for path in kwargs[ 'scripts' ] ]
    
    si = script_info( root )
    eval_tree( root, db, si, **kwargs )


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
    
    parser.add_argument(
        '-u', '--user',
        type = str,
        help = 'User ID. Required for hosted environment.'
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
    
    parser.add_argument(
        '-d', '--driver',
        type = str,
        required = False,
        help = 'Driver used to retrieve scripts.'
    )
    
    
    args = parser.parse_args()
    
    scripts = json.loads( args.scripts ) if args.scripts else None

    run_local( 
        os.path.abspath( args.root ), 
        scripts       = scripts,
        ignore_errors = args.ignore_errors, 
        multithread   = args.multithread,
        verbose       = args.verbose 
    )


# # Work

# In[ ]:


# root = os.path.normpath(
#     os.path.join( os.getcwd(), '../_tests/projects/inclined-plane' )
# )

# run_local( root )

