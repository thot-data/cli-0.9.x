
# coding: utf-8

# # Project Utilities

# In[ ]:


import os
import json

from .classes.base_object import BaseObjectJSONEncoder
from .classes.script import ScriptAssociation
from .classes.asset import Asset
from .db import local


# In[ ]:


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
        :returns: List of effected containers.
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
        :returns: List of effected containers.
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
    
    
    def add_assets( self, assets, search, overwrite = False ):
        """
        Add Assets to the matched Containers.
        
        :param assets: Dictionary keyed by ids with Asset values.
        :param search: Dictionary to filter containers.
        :param overwrite: Whether to overwrite an already existing Asset. [Default: False]
        :returns: List of modified Assets.
        """
        # create assets
        assets = { _id: Asset( **asset ) for _id, asset in assets.items() } 
        
        new_assets = []
        containers = self._db.containers.find( search )
        for container in containers: 
            asset_added = False
            container_assets = [ asset._id for asset in container.assets ]
            
            for _id, asset in assets.items():
                asset_id = os.path.join( container._id, _id )
                
                if asset_id in container_assets:
                    # asset already in container
                    if ( overwrite ):
                        # replace with new asset
                        self._db.assets.replace_one( _id, asset )
                        asset_added = True
                    
                else:
                    # script does not exist yet
                    self._db.assets.insert_one( asset_id, asset )
                    asset_added = True
                    
                if asset_added:
                    new_assets.append( new_asset )
                    
        return modified_containers
        
        
    def remove_assets( self, assets, search = None, removed_name = '_asset_removed' ):
        """
        Remove Assets matching the given criteria.
        This does not delete anything, but only changes 
        the name of the _asset.json file to <removed_name>.json.
        
        :param assets: Dictionary of criteria to match Assets.
        :param search: Dictionary of criteria to match Containers. [Default: None]
        :param removed_name: Name of file to move _assest.json to. [Default: '_asset_removed']
        :returns: List of removed Assets.
        """
        assets = self._db.assets.find( assets )
        
        if search is not None:
            # filter assets by container
            asset_ids = [ asset._id for asset in assets ]
            
            remove_assets = []
            containers = self._db.containers.find( search )
            for container in containers:
                remove_assets += filter( 
                    lambda asset: ( asset._id in asset_ids ),
                    container.assets
                )
                    
            assets = remove_assets
        
        for asset in assets:
            # modify asset names to remove
            object_path = asset._object_file_path
            ( head, tail ) = os.path.split( object_path )
            removed_path = os.path.join( head, removed_name + '.json' )
            
            os.rename( object_path, removed_path )
        
        return assets
    
    
    def print_tree( self, properties = None, root = None, level = 0 ):
        """
        Prints the tree.
        
        :param properties: List of properties to print. [Default: None]
        :param root: Id of the root of the tree to print, or None to use database root.
            [Default: None]
        :param level: The current tree level. [Default: 0]
        """
        
        if root is None:
            root = self._db.containers.find_one( { '_id':  self._db.root } )
        
        # DFT printing
        out = '\t'* level # indent 
        out += root._id # print id
        
        if properties is not None:
            # add properties
            props = { prop: root[ prop ] for prop in properties }
            out += ' {}'.format( props )
            
        print( out )
        
        # recurse on children
        for child in root.children:
            self.print_tree( properties = properties, root = child, level = level + 1 )


# ## Main

# In[ ]:


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
        help = 'Scripts object. Format depends on function.'
    )
    
    parser.add_argument(
        '--assets',
        type = str,
        help = 'Assets object. Format depends on function.'
    )
    
    parser.add_argument(
        '-w', '--overwrite',
        action = 'store_true',
        help = 'Allows overwriting objects if they already exist.'
    )
    
    parser.add_argument(
        '--properties',
        type = str,
        help = 'List of properties. Use depends on function.'
    )
    
    args = parser.parse_args()
    fcn  = args.function
    modified = None
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
        
    elif fcn =='add_assets':    
        assets = json.loads( args.assets )
        search = json.loads( args.search )
        
        modified = util.add_assets( assets, search, overwrite = args.overwrite )
        
    elif fcn == 'remove_assets':
        assets = json.loads( args.assets )
        search = json.loads( args.search )
        
        modified = util.remove_assets( assets, search )
        
    elif fcn == 'print_tree':
        properties = ( 
            json.loads( args.properties )
            if args.properties is not None else
            None
        )    
        
        util.print_tree( properties = properties )
        
    
    if modified:
        for container in modified:
            print( container._id )
            
            
    


# # Work

# In[ ]:


# util = ThotUtilities( os.path.abspath( '../../_tests/projects/inclined-plane' ) )


# In[ ]:


# util.add_scripts( [{ 'script': 'new', 'priority': 0, 'autorun': True}], { 'type': 'project'} )

