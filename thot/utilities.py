
# coding: utf-8

# # Project Utilities

# In[1]:


import os
import json

from .classes.base_object import BaseObjectJSONEncoder
from .classes.script import ScriptAssociation
from .db import local


# In[5]:


class ThotUtilities():
    """
    """
    
    def __init__( self, root ):
        """
        :param root: Either a LocalDB or root path to create one.
        """
        self._db = local.LocalDB( root )
        
        
    def add_scripts( self, scripts, search, overwrite = False ):
        """
        Add scripts to all containers that match search.

        :param scripts: A list of or individual script associations to add.
        :param search: A dictionary to filter containers.
        :param overwrite: True to overwrite already existing scripts. [Default: False] 
        :returns: List of containers to which the scripts were added.
        """
        if not isinstance( scripts, list ):
            # single script passed in
            scripts = [ scripts ]
        
        # create script associations
        for index, script in enumerate( scripts ):
            scripts[ index ] = ScriptAssociation( **script )
        
        modified = []
        containers = self._db.containers.find( search )
        for container in containers:
            container_modified = False
            
            try:
                path = container._scripts_path()
                
            except FileNotFoundError as err:
                # scripts file does not exist
                path = err.filename

            container_scripts = [ script[ 'script' ] for script in container.scripts ]
            for script in scripts:
                if script.script in container_scripts:
                    # script already in scripts
                    if ( overwrite ):
                        # replace with new script
                        index = container_scripts.index( script.script )
                        container.scripts[ index ] = script
                        container_modified = True
                    
                else:
                    # script does not exist yet
                    container.scripts.append( script )
                    container_modified = True
                    
            if container_modified:
                modified.append( container )
                
                # save changes
                with open( path, 'w' ) as f:
                    json.dump( container.scripts, f, cls = BaseObjectJSONEncoder, indent = 4 )
    
        return modified
        
    
    def remove_scripts( self, scripts, search ):
        """
        Removes scripts from containers.
        
        :param scripts: List of or single scripts to remove.
        :param search: A dictionary to filter containers.
        :returns: List of affected containers.
        """
        if not isinstance( scripts, list ):
            # single script passed in
            scripts = [ scripts ]
        
        modified = []
        containers = self._db.containers.find( search )
        for container in containers:
            container_modified = False
            
            try:
                path = container._scripts_path()

            except FileNotFoundError as err:
                # scripts file does not exist
                path = err.filename
            
            container_scripts = [ script[ 'script' ] for script in container.scripts ]
            for index in range( len( container_scripts ) - 1, -1, -1 ):
                # iterate from back to front so deletes do not disturb order
                
                if container_scripts[ index ] in scripts:
                    # script exists, remove it
                    del container.scripts[ index ]
                    container_modified = True
                    
            if container_modified:
                modified.append( container )
                
                # save changes
                with open( path, 'w' ) as f:
                    json.dump( container.scripts, f, cls = BaseObjectJSONEncoder, indent = 4 )
                
        return modified
    
    
    def set_scripts( self, scripts, search ):
        """
        Sets scripts for Containers.
        
        :param scripts: List of or single scripts.
        :param search: A dictionary to filter containers.
        :returns: List of affected containers.
        """
        if not isinstance( scripts, list ):
            # single script passed in
            scripts = [ scripts ]
        
        containers = self._db.containers.find( search )
        for container in containers:
            # get path to scripts file
            try:
                path = container._scripts_path()

            except FileNotFoundError as err:
                # scripts file does not exist
                path = err.filename
            
            
            with open( path, 'w' ) as f:
                # set scripts
                json.dump( scripts, f, cls = BaseObjectJSONEncoder, indent = 4 )
                
        return containers


# ## Main

# In[3]:


if __name__ == '__main__':
    """
    Provides utilities for building a Thot Local Project.
    """
    from argparse import ArgumentParser
    parser = ArgumentParser( description = 'Thot project utilities.' )
    
    parser.add_argument(
        'function',
        type = str,
        default = '.',
        help = 'Function to run.'
    )
    
    parser.add_argument(
        '-r', '--root',
        type = str,
        default = '.',
        help = 'Path or ID of the root Container.'
    )
    
    parser.add_argument(
        '-s', '--search',
        type = str,
        help = 'JSON object describing Containers to target.'
    )
    
    parser.add_argument(
        '--scripts',
        type = str,
        help = 'List of scripts to add. Format depends on function.'
    )
    
    parser.add_argument(
        '-w', '--overwrite',
        action = 'store_true',
        help = 'Allows overwriting objects if they already exist.'
    )
    
    args = parser.parse_args()
    fcn  = args.function
    output = True
    util = ThotUtilities( os.path.abspath( args.root ) )

    if fcn == 'add_scripts':
        scripts = json.loads( args.scripts )
        search  = json.loads( args.search  )
        
        modified = util.add_scripts( scripts, search, overwrite = args.overwrite )
        
    elif fcn == 'remove_scripts':
        try:
            scripts = json.loads( args.scripts )
        
        except json.decoder.JSONDecodeError as err:
            # single script passed in
            scripts = args.scripts
        
        search = json.loads( args.search )
        
        modified = util.remove_scripts( scripts, search )
      
    elif fcn == 'set_scripts':
        scripts = json.loads( args.scripts )
        search  = json.loads( args.search )
        
        modified = util.set_scripts( scripts, search )
        
    
    if output:
        for container in modified:
            print( container._id )
            
            
    


# # Work

# In[6]:


# util = ThotUtilities( os.path.abspath( '../../_tests/projects/inclined-plane' ) )


# In[7]:


# util.add_scripts( [{ 'script': 'new', 'priority': 0, 'autorun': True}], { 'type': 'project'} )

