
# coding: utf-8

# # Project Utilities

# In[ ]:


import os
import json

from .classes.base_object import BaseObjectJSONEncoder
from .classes.container import Container
from .classes.script import ScriptAssociation
from .classes.asset import Asset
from .db import local


# In[ ]:


class ThotUtilities():
    """
    Utility functions for manipulating and exploring local Thot projects.
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
        
    
    def remove_scripts( self, scripts, search = {} ):
        """
        Removes scripts from containers.
        
        :param scripts: List of or single scripts to remove.
        :param search: A dictionary to filter containers. [Default: {}]
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
        assets = { _id: Asset( **asset ) for _id, asset in assets.items() } 
        return self.add_objects( assets, search, overwrite = overwrite )
    
        
    def remove_assets( self, assets, search = None, removed_name = '_asset_removed' ):
        """
        Remove Assets matching the given criteria.
        This does not delete anything, but only changes 
        the name of the _asset.json file to <removed_name>.json.
        
        :param assets: Dictionary of criteria to match Assets.
        :param search: Dictionary of criteria to match Containers. [Default: {}]
        :param removed_name: Name of file to move _assest.json to. [Default: '_asset_removed']
        :returns: List of removed Assets.
        """
        return self.remove_objects( assets, Asset, search )
    
    
    def add_containers( self, containers, search, overwrite = False ):
        """
        Add children Containers to the matched Containers.
        
        :param containers: Dictionary keyed by ids with Container values.
        :param search: Dictionary to filter Containers.
        :param overwrite: Whether to overwrite an already existing child. [Default: False]
        :returns: List of modified children.
        """
        containers = { _id: Container( **container ) for _id, container in containers.items() }
        return self.add_objects( containers, search, overwrite = overwrite )
    
    
    def remove_containers( self, containers, search = None ):
        """
        Remove Containers.
        This does not delete anythign, but only modifies the name of the 
        _container.json file.
        
        :param containers: Dictionary of criteria to remove Containers.
        :param search: Dictionary to filter parent Containers.
        :returns: List of removed Containers. This does not include any children that were
            indirectly removed because their parent was removed.
        """
        return self.remove_objects( containers, Container, search )
    
    
    def print_tree( self, properties = None, assets = False, scripts = False, root = None, level = 0 ):
        """
        Prints the tree.
        
        :param properties: List of properties to print. [Default: None]
        :param root: Root Contianer of the tree to print, or None to use database root.
            [Default: None]
        :assets: True to print Asset ids or a list of Asset properties.
            Does not print otherwise. [Default: False]
        :scripts: True to print Script ids or a list of Script Association properties.
            Does not print otherwise. [Default: False]
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
            
        if assets:
            for asset in root.assets:
                out += '\n' + '\t'* ( level + 1 ) + '+ '
                out += asset._id
                
                if isinstance( assets, list ):
                    props = { prop: asset[ prop ] for prop in assets }
                    out += ' {}'.format( props )
                    
        if scripts:
            for script in root.scripts:
                out += '\n' + '\t'* ( level + 1 ) + '- '
                out += script[ 'script' ]
                
                if isinstance( assets, list ):
                    props = { prop: script[ prop ] for prop in scripts }
                    out += ' {}'.format( props )
            
        print( out )      
        
        # recurse on children
        for child in root.children:
            self.print_tree( 
                properties = properties, 
                assets = assets,
                scripts = scripts,
                root = child, 
                level = level + 1 
            )
          
        
    # helper functions    
            
    def add_objects( self, objects, search, overwrite = False ):
        """
        Add objects to the matched Containers.
        
        :param objects: Dictionary keyed by ids with object properties as values.
            ids can be a string or list of strings to create multiple instances of the objects.
        :param search: Dictionary to filter containers.
        :param overwrite: Whether to overwrite an already existing Asset. [Default: False]
        :returns: List of modified Assets.
        """        
        new_objects = []
        containers = self._db.containers.find( search )
        
        for _ids, obj in objects.items():
            # iterate over new objects
            obj_kind = self.get_object_class( obj )
            object_collection = self.get_object_collection( obj_kind )
            
            if not isinstance( _ids, list ):
                # convert _id to list for iteration
                _ids = [ _ids ]
            
            for container in containers: 
                new_obj = None
                container_objects = self.get_container_objects( container, obj_kind )
                container_objects = [ obj._id for obj in container_objects ]
            
                object_ids = [ os.path.join( container._id, _id ) for _id in _ids ]
                
                for object_id in object_ids:
                    # iterate over ids, adding object for each
                    
                    if object_id in container_objects:
                        # object already in container
                        if ( overwrite ):
                            # replace with new object
                            new_obj = object_collection.replace_one( object_id, obj )

                    else:
                        # script does not exist yet
                        new_obj = object_collection.insert_one( object_id, obj )

                    if new_obj is not None:
                        new_objects.append( new_obj )
                    
        return new_objects
    
    
    def remove_objects( 
        self, 
        objects, 
        klass,
        search = None, 
        removed_name = lambda name: '{}_removed.json'.format( name ) 
    ):
        """
        Remove objects matching the given criteria.
        This does not delete anything, but only changes 
        the name of the object file.
        
        :param objects: Dictionary of criteria to match objects.
        :param klass: The class of object to be removed.
            Values [ Container, Asset ]
        :param search: Dictionary of criteria to match Containers. [Default: None]
        :param removed_name: Name of file to move object file to,
            or a function accepting the current name as the input and returning the desired name.
            [Default: lambda name: '{}_removed.json'.format( name )]
        :returns: List of removed objects.
        """
        object_collection = self.get_object_collection( klass )
        objects = object_collection.find( objects )
        
        if search is not None:
            # filter assets by container
            object_ids = [ obj._id for obj in objects ]
            
            remove_assets = []
            containers = self._db.containers.find( search )
            for container in containers:
                container_objects = self.get_container_objects( container, klass )
                
                remove_assets += filter( 
                    lambda obj: ( obj._id in object_ids ),
                    container_objects
                )
                    
            objects = remove_assets
        
        for obj in objects:
            # modify asset names to remove
            object_path = obj._object_file_path
            ( head, tail ) = os.path.split( object_path )
            
            if callable( removed_name ):
                # removed name is function
                name, _ = os.path.splitext( tail ) 
                of_name = removed_name( name )
                
            else:
                of_name, _ = removed_name
            
            removed_path = os.path.join( head, of_name )
            os.rename( object_path, removed_path )
        
        return objects
    
    
    def get_object_class( self, obj ):
        """
        Returns the class of the object passed in.

        :param obj: The object to examine.
        :returns: The class of the object: Container, Asset.
        """
        if isinstance( obj, Container ):
            return Container

        elif isinstance( obj, Asset ):
            return Asset

        # not a valid type
        raise TypeError( 'Invalid object type.' ) 


    def get_object_collection( self, kind ):
        """
        Returns the collection of the given kind.

        :param kind: Kind of collection.
            Values: [ Container, Asset ]
        :returns: Database collection of the given kind.
        """
        if kind is Container:
            return self._db.containers

        elif kind is Asset:
            return self._db.assets

        raise TypeError( 'Invalid kind.' )


    def get_container_objects( self, container, kind ):
        """
        Gets the objects of the given kind of the container.

        :param container: Container.
        :param kind: Kind of object to receive.
            Values: [ Container, Asset ]
        :returns: List of objects of the given kind.
        """
        if kind is Container:
            return container.children

        elif kind is Asset:
            return container.assets

        # not a valid kind
        raise TypeError( 'Invalid kind.' )


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
        '--containers',
        type = str,
        help = 'Containers object. Format depends on function.'
    )
    
    parser.add_argument(
        '-w', '--overwrite',
        action = 'store_true',
        help = 'Allows overwriting objects if they already exist.'
    )
    
    
    # TODO [0]: Fix parse errors for Windows machines
    args = parser.parse_args()
    fcn  = args.function
    modified = None
    util = ThotUtilities( os.path.abspath( args.root ) )

    if fcn == 'add_scripts':
        scripts = json.loads( args.scripts )
        search  = json.loads( args.search )
        
        modified = util.add_scripts( scripts, search, overwrite = args.overwrite )
        
    elif fcn == 'remove_scripts':
        try:
            scripts = json.loads( args.scripts )
        
        except json.decoder.JSONDecodeError as err:
            # single script passed in
            scripts = args.scripts
        
        search = (
            {}
            if ( args.search is None ) else
            json.loads( args.search )
        )
        
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
        search = (
            None
            if ( args.search is None ) else
            json.loads( args.search )
        )
        
        modified = util.remove_assets( assets, search )
        
    elif fcn == 'add_containers':
        containers = json.loads( args.containers )
        search = json.loads( args.search )
        
        modified = util.add_containers( containers, search, overwrite = args.overwrite )
        
    elif fcn == 'remove_containers':
        containers = json.loads( args.containers )
        search = (
            None
            if ( args.search is None ) else
            json.loads( args.search )
        )
        
        modified = util.remove_containers( containers, search )
        
    elif fcn == 'print_tree':
        properties = ( 
            json.loads( args.containers )
            if args.containers is not None else
            None
        )
        
        assets = (
            None
            if ( args.assets is None ) else
            json.loads( args.assets )
        )    
        
        scripts = (
            None
            if ( args.scripts is None ) else
            json.loads( args.scripts )
        )
        
        util.print_tree( properties = properties, assets = assets, scripts = scripts )
        
    else:
        raise ValueError( 'Invalid function {}. Use `python -m thot.utilities -h` for help.' )
    
    
    if modified:
        for obj in modified:
            print( obj._id )
            


# # Work

# In[ ]:


# util = ThotUtilities( os.path.abspath( '../../_tests/projects/inclined-plane' ) )


# In[ ]:


# util.add_scripts( [{ 'script': 'new', 'priority': 0, 'autorun': True}], { 'type': 'project'} )

