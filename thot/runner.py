#!/usr/bin/env python
# coding: utf-8

# # Runner

# In[ ]:


import os
import sys
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor

from bson.objectid import ObjectId

from .db.local import LocalDB
from .db.mongo import MongoDB
from .classes.container import Container


# In[ ]:


def run_script( script_id, script_path, container_id ):
    """
    Runs the given program form the given Container.
    
    :param script_id: ID of the script.
    :param script_path: Path to the script.
    :param container: ID of the container to run from.
    """
    # setup environment
    env = os.environ.copy()
    env[ 'THOT_CONTAINER_ID' ] = container_id # set root container to be used by thot library
    env[ 'THOT_SCRIPT_ID' ]    = script_id    # used in project for adding Assets
    
    # TODO [0]: Ensure safely run
    # run program
    try:
        subprocess.check_output(
            'python {}'.format( script_path ),
            shell = True,
            env = env
        )
        
    except subprocess.CalledProcessError as err:
        err.cmd = '[{}] '.format( container_id ) + err.cmd
        raise err
    
    
# TODO [2]: Allow running between certain depths.
def eval_tree( 
    root, 
    db, 
    scripts = None,
    ignore_errors = False, 
    multithread = False, 
    verbose = False 
):
    """
    Runs scripts on the Container tree.
    Uses DFS, running from bottom up.
    
    :param root: Container.
    :param db: Database
    :param scripts: List of scripts to run, or None for all. [Default: None]
    :param ignore_errors: Continue running if an error is encountered. [Default: False]
    :param multithread: Evaluate tree using multiple threads. [Default: False]
        CAUTION: May decrease runtime, but also locks system and can not kill.
    :param verbose: Print evaluation information. [Default: False]
    """
    hosted = isinstance( db, MongoDB )
    
    if hosted:
        root = ObjectId( root )
        
    root = db.containers.find_one( { '_id': root } )
    root = Container( **root )
    
    # eval children
    if multithread:
        with ThreadPoolExecutor( max_workers = 10 ) as executer:
            executer.map( 
                lambda child: eval_tree( child, db, verbose = verbose ), 
                root.children 
            )
        
    else:
        for child in root.children:
            eval_tree( 
                child, 
                db, 
                scripts       = scripts,
                ignore_errors = ignore_errors,
                multithread   = multithread,
                verbose       = verbose 
            )

    # TODO [1]: Check filtering works for local projects.
    # filter scripts to run
    root.scripts.sort()
    run_scripts = (
        root.scripts
        if scripts is None else
        filter( lambda assoc: assoc.script in scripts, root.scripts ) # filter scripts
    )
    
    # eval self
    for association in run_scripts:
        if not association.autorun:
            continue

        if hosted:
            script_id = association.script
            
            # get script path
            script = db._scripts.find_one( { 
                '_id': ObjectId( script_id ) 
            } )

            script_path = script[ 'file' ]
            
        else:
            # local project script paths are prefixed by path id
            script_id = script_path = os.path.normpath( # path to script
                os.path.join( root._id, association.script )
            )
            
        if verbose:
            print( 'Running script {} on container {}'.format( script_id, root._id )  )
            
        try:
            run_script( 
                str( script_id ), # convert ids from ObjectId, if necessary
                script_path, 
                str( root._id ) 
            ) 
            
        except Exception as err:
            if ignore_errors:
                # TODO [2]: Only return errors after final exit.
                # collect errors for output at end
                print( '[{}] {}'.format( root._id, err ) )
                
            else:
                raise err


# In[ ]:


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
    
    eval_tree( root, db, **kwargs )
    
    
def run_hosted( user, root, **kwargs ):
    """
    Runs a hosted project.
    
    :param user: ID of user.
    :param root: ID of root Container.
    :param kwargs: Arguments passed to #eval_tree.
    """
    os.environ[ 'THOT_USER_ID' ] = user
    
    db = MongoDB()
    eval_tree( root, db, **kwargs )


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
        '-env', '--environment',
        type = str,
        choices = [ 'local', 'hosted' ],
        default = 'local',
        help = 'Environment of the runner.'
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
    
    args = parser.parse_args()
    
    scripts = json.loads( args.scripts ) if args.scripts else None

    if args.environment == 'local':
        run_local( 
            os.path.abspath( args.root ), 
            scripts       = scripts,
            ignore_errors = args.ignore_errors, 
            multithread   = args.multithread,
            verbose       = args.verbose 
        )
        
    elif args.environment == 'hosted':
        if not args.user:
            raise RuntimeError( 'User is required for runner in a hosted environment.' )
        
        run_hosted( 
            args.user, 
            args.root,
            scripts = scripts,
            verbose = args.verbose 
        )


# # Work

# In[ ]:


# root = os.path.normpath(
#     os.path.join( os.getcwd(), '../_tests/projects/inclined-plane' )
# )

# run_local( root )


# In[ ]:




