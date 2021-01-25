#!/usr/bin/env python
# coding: utf-8

# # Thot
# Library for data analysis and management.

# In[ ]:


import os
import inspect
from uuid import uuid4 as uuid

from thot_core.classes.thot_interface import ThotInterface
from thot_core.classes.container      import Container
from thot_core.classes.asset          import Asset
from thot_core.classes.script         import ScriptAssociation

from .db.local import LocalObject, LocalDB


# ## Local

# In[ ]:


class ThotProject( ThotInterface ):
    """
    Local Thot project interface, used to retrieve Containers and Assests.
    """
    
    def __init__( self, root = None ):
        """
        :param root: Root Container or None to get from environment variable THOT_CONTAINER_ID.
        """
        # save environment
        ORIGINAL_DIR = 'THOT_ORIGINAL_DIR'
        if ( ORIGINAL_DIR not in os.environ ):
            os.environ[ ORIGINAL_DIR ] = os.getcwd()
            
        # move to original directory, so relative paths are correct
        os.chdir( os.environ[ ORIGINAL_DIR ] )
        
        if root is not None:
            root = os.path.abspath( root )
        
        super().__init__( root )
        self._db = LocalDB( self._root )
        
        # set environment
        os.chdir( self._root )
    
    
    def find_container( self, search = {} ):
        """
        Gets a single Container matching search criteria.
        
        :param search: Dictionary of search criteria.
            [Default: {}]
        :returns: Container matching search criteria or None.
        """
        result = super().find_container( search )
        
        if result is None:
            return None
        
        container = ThotProject._object_to_container( result )
        return container
    
    
    def find_containers( self, search = {} ):
        """
        Gets Containers matching search criteria.
        
        :param search: Dictionary of search criteria.
            [Default: {}]
        :returns: List of Containers matching search.
        """
        result = super().find_containers( search )
        
        containers = []
        for res in result:
            containers.append( ThotProject._object_to_container( res ) )
    
        return containers    

    
    def find_asset( self, search = {} ):
        """
        Gets a single Asset matching search criteria.
        
        :param search: Dictionary of search criteria.
            [Default: {}]
        :returns: Asset matching search criteria or None.
        """
        result = super().find_asset( search )
        
        if result is None:
            return None
        
        asset = Asset( **result )
        return asset
    
    
    def find_assets( self, search = {} ):
        """
        Gets Assets matching search criteria.
        
        :param search: Dictionary of search criteria.
            [Default: {}]
        :returns: List of Assets matching search.
        """
        result = super().find_assets( search )
    
        assets = [ Asset( **asset ) for asset in result ]
        return assets    
    
    
    def add_asset( self, asset, _id = None, overwrite = True ):
        """
        Creates a new Asset.
        
        :param asset: Dictionary of information about the Asset.
        :param _id: Id of new asset, or None to create one.
            [Default: None]
        :param overwrite: Allow Asset to be overwritten if it already exists.
            [Default: True]
        :returns: Path to Asset file.
        """
        def _get_caller_id():
            """
            :returns: File name of the caller.
            """
            caller = inspect.currentframe().f_back.f_back
            info = inspect.getframeinfo( caller )
            return info.filename
            
        
        # check file is defined
        if 'file' not in asset:
            _id = str( uuid() )
            asset[ 'file' ] = _id
        
        if _id is None:
            _id = str( uuid() )
        
        # set properties
        asset[ 'creator_type' ] = 'script'
        asset[ 'creator' ] = (
            os.environ[ 'THOT_SCRIPT_ID' ]
            if 'THOT_SCRIPT_ID' in os.environ else
            _get_caller_id()
        )
            
        path = os.path.normpath( 
            os.path.join( self.root, _id )
        )
        
        if overwrite:
            self._db.assets.replace_one( _id, asset, upsert = True )
            
        else:
            self._db.assets.insert_one( _id, asset )
    
        return os.path.normpath( 
            os.path.join( path, asset[ 'file' ] )
        )
    
    
    @staticmethod
    def dev_mode():
        """
        Whether the script is being run in development mode or not.
        
        :returns: False if being run from the runner, True otherwise.
        """
        return ( 'THOT_CONTAINER_ID' not in os.environ )
    
    
    @staticmethod
    def _sort_objects( objects ):
        """
        Sorts a list of LocalObjects by kind
        """
        # sort types of children
        kinds = { kind: [] for kind in LocalObject.kinds }
        for obj in objects:
            kinds[ obj.kind ].append( obj )
        
        return kinds
    
    
    @staticmethod
    def _object_to_container( obj ):
        """
        Converts a LocalObject to a Container.
        
        :param obj: LocalObject of kind container.
        :returns: Container.
        """
        container = dict( obj )
        
        # sort children
        kinds = ThotProject._sort_objects( obj.children )

        container[ 'children' ] = [ child._id  for child  in kinds[ 'container' ] ]
        container[ 'assets' ]   = [ asset._id  for asset  in kinds[ 'asset' ] ]
        container[ 'scripts' ]  = [  
            ScriptAssociation( **script )
            for script in obj.scripts 
        ]
        
        container = Container( **container )
        
        return container


# # Work
