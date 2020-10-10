
# coding: utf-8

# # Thot
# Library for data analysis and management.

# In[ ]:


import os
import random

from .db.local import LocalObject, LocalDB
from .db.mongo import MongoDB # TODO [2]: Only required for hosted version, remove package dependency
from bson.objectid import ObjectId

from .classes.thot_interface import ThotInterface
from .classes.container      import Container
from .classes.asset          import Asset
from .classes.script         import ScriptAssociation


# ## Local

# In[ ]:


class LocalProject( ThotInterface ):
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
        
        container = LocalProject._object_to_container( result )
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
            containers.append( LocalProject._object_to_container( res ) )
    
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
        # check file is defined
        if 'file' not in asset:
            _id = str( random.random() )[ 2: ]
        
        if _id is None:
            _id = str( random.random() )[ 2: ]
        
        # set properties
        asset[ 'creator_type' ] = 'script'
        asset[ 'creator' ] = (
            os.environ[ 'THOT_SCRIPT_ID' ]
            if 'THOT_SCRIPT_ID' in os.environ else
            __file__
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
        kinds = LocalProject._sort_objects( obj.children )

        container[ 'children' ] = [ child._id  for child  in kinds[ 'container' ] ]
        container[ 'assets' ]   = [ asset._id  for asset  in kinds[ 'asset' ] ]
        container[ 'scripts' ]  = [  
            ScriptAssociation( **script )
            for script in obj.scripts 
        ]
        
        container = Container( **container )
        
        return container


# ## Hosted

# In[ ]:


class ThotProject( ThotInterface ):
    
    def __init__( self, root = None, user = None ):
        """
        :param root: Root Container or None to use environment variable THOT_CONTAINER_ID.
            [Default: None]
        :param user: User id or None to use environment variable THOT_USER_ID.
            [Default: None]
        """
        super().__init__( root )
        self._db = MongoDB()
        
        # set up environment
        self._user = (
            os.environ[ 'THOT_USER_ID' ]
            if user is None else
            user
        )
        
        try:
        	self._data_path = os.environ[ 'THOT_ASSET_DIRECTORY' ]

        except KeyError as err:
	        self._data_path = os.path.join( 
	            '_resources', 
	            'assets',
        	)
        
        if not os.path.exists( self._data_path ):
            os.makedirs( self._data_path )
        
        os.chdir( self._data_path )
        
    
    def find_container( self, search = {} ):
        """
        Gets a single Container matching search criteria.
        
        :param search: Dictionary of search criteria.
            [Default: {}]
        :returns: Container matching search criteria or None.
        """
        containers = self.find_containers( search )
        
        if len( containers ) is 0:
            return None
        
        return containers[ 0 ]
    

    def find_containers( self, search = {} ):
        """
        Gets Containers matching search criteria.
        
        :param search: Dictionary of search criteria.
            [Default: {}]
        :returns: List of Containers matching search.
        """
        search = self._restrict_search( 
            self._convert_ids( search ) 
        )
        
        # TODO [5]: Make more efficient
        # bottom-up search
        containers = self._db.containers.aggregate( [ 
            { # search for matching documents user has access to
                '$match': search
            },
            
            { # recurse to get ancestors
                '$graphLookup': {
                    'from': 'containers',
                    'startWith': '$parent',
                    'connectFromField': 'parent',
                    'connectToField': '_id',
                    'as': 'ancestors'
                }
            }
        ] )
        
        # ancestors are ordered oldest to youngest
        # prune ancestors to _id field only, add self to ancestors
        # retrieve inherited metadata
        projected = []
        for container in containers:
            # collect metadata of ancestors
            inherited_keys = []
            inherited_metadata = []
            for ancestor in reversed( container[ 'ancestors' ] ) :
                # iterate from youngest to oldest
                for datum in ancestor[ 'metadata' ]:
                    if datum[ 'name' ] not in inherited_keys:
                        # datum not inherited yet
                        inherited_metadata.append( datum )
                        inherited_keys.append( datum[ 'name' ] )
            
            local_keys = [ datum[ 'name' ] for datum in container[ 'metadata' ] ]
            container[ 'metadata' ] += [ # add inherited metadata if not already defined 
                inherited 
                for inherited in inherited_metadata 
                if ( inherited[ 'name' ] not in local_keys ) 
            ]
            
            # prune ancestors
            ancestors = [ str( ancestor[ '_id' ] ) for ancestor in container[ 'ancestors' ] ]
            ancestors.append( str( container[ '_id' ] ) )
            container[ 'ancestors' ] = ancestors
            projected.append( container )
        
        
        containers = filter( # keep only those with root as an ancestor
            lambda container: self._root in container[ 'ancestors' ],
            projected
        )
        
        containers = [
            Container( **container )
            for container in containers
        ]
        
        return containers
    
    
    def find_asset( self, search = {} ):
        """
        Gets a single Asset matching search criteria.
        
        :param search: Dictionary of search criteria.
            [Default: {}]
        :returns: Asset matching search criteria or None.
        """
        assets = self.find_assets( search )
        
        if len( assets ) is 0:
            return None
        
        return assets[ 0 ]
    
    
    def find_assets( self, search = {} ):
        """
        Gets Assets matching search criteria.
        
        :param search: Dictionary of search criteria.
            [Default: {}]
        :returns: List of Assets matching search.
        """
        search = self._restrict_search( 
            self._convert_ids( search ) 
        )
        
        # get all assets under root
        root = self._db.containers.aggregate( [ 
            { # get root
                '$match': { '_id': ObjectId( self._root ) }
            },

            { # recurse to get descendants
                '$graphLookup': {
                    'from': 'containers',
                    'startWith': '$children',
                    'connectFromField': 'children',
                    'connectToField': '_id',
                    'as': 'descendants'
                }
            }
        ] )

        # reshape root
        root = list( root )
        if len( root ) is not 1:
            raise RuntimeError( '{} roots found. Must have exactly one.'.format( len( root ) ) )
                
        # combine all containers 
        containers = root + root[ 0 ][ 'descendants' ] 

        if '_id' not in search:
           # get all assets under root
           # collect assets
            assets = []
            for container in containers:
                assets += container[ 'assets' ]

            # restrict search
            search[ '_id' ] = { '$in': assets }
            
        result = self._db.assets.find( search )
        assets = []
        for asset in result:
            # modify file to be relative to running script location
            asset[ 'file' ] = os.path.relpath( 
                os.path.join( os.environ[ 'THOT_SERVER_ROOT' ], asset[ 'file' ] )
            )
            
            # find parent container
            parent = None
            for container in containers:
                if asset[ '_id' ] in container[ 'assets' ]:
                    # parent found
                    parent = container
                    break
            
            if parent is None:
                # parent not found
                raise RuntimeError( "Asset's parent not found. Cannot retrieve metadata." )

            # initialize metadata if necessary
            if 'metadata' not in asset:
                asset[ 'metadata' ] = []

            # traverse up ancestor tree to collect metadata
            while parent is not None:
                # get existing metadata keys
                keys = [ datum[ 'name' ] for datum in asset[ 'metadata' ] ]
                asset[ 'metadata' ] += [ 
                    datum 
                    for datum in parent[ 'metadata' ] 
                    if datum[ 'name' ] not in keys 
                ]

                # get next ancestor
                parent = [ 
                    p 
                    for p in containers 
                    if p[ '_id' ] == parent[ 'parent' ]
                ]

                num_parents = len( parent )
                if num_parents == 0:
                    # no parent found
                    parent = None

                elif num_parents == 1:
                    parent = parent[ 0 ]

                else:
                    # multiple parents found
                    raise RuntimeError( 'More than one parent found with id {}.'.format( container[ 'parent' ] ) )
            
            
            assets.append( asset )
        
            
        assets = [ Asset( **asset ) for asset in assets ]
        
        return assets
    
    
    def add_asset( self, asset, _id = None, overwrite = True ):
        """
        Creates a new Asset.
        
        :param asset: Dictionary of information about the Asset.
        :param _id: Ignored. Included for compatibility with LocalProject.
        :param overwrite: (NOT IMPLEMENTED) Allow Asset to be overwritten if it already exists.
            [Default: True]
        :returns: Path to Asset file.
        """
        # TODO [0]: Ensure file is safe
        # modify asset properties
        
        # file
        # rename asset file to avoid conflicts
        file_name = os.path.join( 
            os.getcwd(),
            str( random.random() )[ 2: ]
        )
        
        if ( 'file' in asset ):
            # test if normal file name
            extension = os.path.splitext( asset[ 'file' ] )[ 1 ] # extension
            
            if not extension:
                # file was not normal name
                # check if extension only
                if asset[ 'file' ][ 0 ] == '.':
                    # file is extension type
                    extension = asset[ 'file' ][ 1: ]
        
        asset[ 'file' ] = '{}.{}'.format( file_name, extension )
        
        # user role
        asset[ 'roles' ] = [ {
            'user': ObjectId( self._user ),
            'role': 'owner'
        } ]
        
        # creator
        asset[ 'creator_type' ] = 'script'
        asset[ 'creator' ] = os.environ[ 'THOT_SCRIPT_ID' ]
        
        # create asset
        result = self._db.assets.insert_one( asset )
        
        # add to container
        self._db.containers.find_one_and_update( 
            { '_id': ObjectId( self._root ) },
            { '$push': { 'assets': result.inserted_id } }
        )
        
        return asset[ 'file' ]
    
    
    @staticmethod
    def _convert_ids( search ):
        """
        Converts keys named _id to have values of type ObjectId.
        
        :param search: Dictionary.
        :returns: Dictionary with keys named _id values converted to ObjectIds
        """
        for key, val in search.items():
            if key == '_id':
                # convert _id
                search[ key ] = ObjectId( val )
                
            elif isinstance( val, dict ):
                search[ key ] = self._convert_ids( val )
                
            elif isinstance( val, list ):
                search[ key ] = [ self._convert_ids( elm ) for elm in val ]
            
        return search
    
        
    def _restrict_search( self, search ):
        """
        Restricts search to user accessible items.
        
        :params search: Dictionary.
        :returns: Dictionary with restricted search.
        """
        search[ 'roles.user' ] = ObjectId( self._user )
        search[ 'roles.role' ] = { '$ne': 'blocked' }
        
        return search
        
        
    def _filter_to_root( self, result ):
        """
        Filters query result to include only decendants of root Container.
        
        :param result: Result filtered to tree of root.
        """
        
        def in_tree( obj ):
            """
            Check whether object is in the project tree.
            
            :param obj: Object to check.
            :returns: True if objet is a member of the project tree, False otherwise.
            """
            if str( obj._id ) == str( self._root._id ):
                # result is root
                return True
            
            elif not obj.parent:
                # object is not root, and doesn't have a parent
                return False
            
            # recurse on parent
            parent = self._db.containers.find( { '_id': ObjectId( obj.parent ) } )
            return in_tree( parent )

        
        if isinstance( result, list ):
            return list( filter( in_tree, result ) )
        
        else:
            return ( result if in_tree( result ) else None )


# # Work

# In[ ]:


# root = os.path.join( os.getcwd(), '_tests/data/inclined-plane' )
# thot = LocalProject( root )


# In[ ]:


# result = thot.find_container( { 'type': 'sample' } )

