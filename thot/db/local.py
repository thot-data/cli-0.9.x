
# coding: utf-8

# # Local Database

# In[ ]:


import os
import re
import json
from datetime import datetime
from glob import glob
from functools import partial
from collections.abc import Mapping

from ..classes.resource import Resource, ResourceJSONEncoder


# ## Helper Functions

# In[ ]:


def _load_json( path ):
    """
    Loads a JSON file.
    
    :param path: Path of JSON file.
    :returns: Dictionary of JSON file.
    :raises json.decoder.JSONDecodeError: If JSON is invalid.
    """
    with open( path, 'r' ) as f:
        try:
            return json.load( f )

        except json.decoder.JSONDecodeError as err:
            raise json.decoder.JSONDecodeError( '{} of {}'.format( err, path ), err.doc, err.pos )


# ## Document Objects

# In[ ]:


class LocalObject( Mapping ):
    """
    Implements a local object.
    
    Id is absolute path to directory.
    """
    
    _object_file_format = '_{}.json'
    kinds = [ # valid object types
        'container',
        'asset'
    ]
    
    
    @classmethod
    def get_object_file( klass, path ):
        """
        :param path: Path to object folder.
        :returns: Path of object file.
        :raises RuntimeError: If there is not one and only one property file.
        """
        # valid kinds
        obj_files = [ 
            klass._object_file_format.format( kind ) 
            for kind in klass.kinds 
        ] 
        
        # get property files
        contents = os.listdir( path )
        obj_file = [ 
            obj_file 
            for obj_file in obj_files 
            if ( obj_file in contents ) 
        ]
        
        # check only only one property file
        if len( obj_file ) is not 1:
            # not only one property file found
            raise RuntimeError( 
                '{} object file(s) found. Must have one and only one'.format( len( obj_file ) )
            )
            
        return obj_file[ 0 ]
    
    
    @classmethod
    def load_object_file( klass, path ):
        """
        :returns: Dictionary of the object file.
        """
        obj_file = klass.get_object_file( path )
        obj_path = os.path.join( path, obj_file )
        
        return _load_json( obj_path )
    
    
    @classmethod
    def get_kind( klass, path ):
        """
        :param path: Path to object folder.
        :returns: Kind of the object, as determined from its property file.
        """
        # for trimming file name
        off   = klass._object_file_format
        start = off.find( '{}' )
        end   = off.find( '.' ) - len( off )
        
        # get object file
        object_file = klass.get_object_file( path )
        
        return object_file[ start : end ]
        
    
    def __init__( self, path, parent = None ):
        """
        :param path: Path to the object.
        :param parent: Parent Object, or None if root. [Default: None]
        """
        self.__path = os.path.normpath( path )
        self.__parent = parent
        self.__object_file = self.get_object_file( self.path )
        
        # get properties
        self.meta = self.load_object_file( self.path )
        if 'metadata' not in self.meta:
            # add metadata container
            self.meta[ 'metadata' ] = {}
            
        # save self metadata separately
        self.__own_metadata_keys = self.meta[ 'metadata' ].keys()
            
        # default name
        if ( 'name' not in self.meta ) or ( not self.meta[ 'name' ] ):
            self.meta[ 'name' ] = os.path.basename( self.path )
        
        # inherit metadata from project parents
        inherited = self.inherited_metadata()
        self.meta[ 'metadata' ] = { **inherited, **self.meta[ 'metadata' ] }
        
        # get notes
        self.__notes = []
        notes_path = os.path.join( self.path, '_notes/' )
        if os.path.exists( notes_path ):
            for note in os.listdir( notes_path ):
                note_path = os.path.join( notes_path, note )
                stats = os.stat( note_path )
                created = datetime.fromtimestamp( stats.st_mtime ).isoformat( ' ' )

                with open( note_path, 'r' ) as f:
                    content = f.read()

                self.__notes.append( {
                    'title':   os.path.splitext( note )[ 0 ],
                    'created': created,
                    'content': content
                } )
        
        
    @property
    def _id( self ):
        return self.path
    
        
    @property
    def path( self ):
        return self.__path
    
    
    @property
    def kind( self ):
        """
        :returns: Kind of the object, as determined from its property file.
        """
        off   = self._object_file_format
        start = off.find( '{}' )
        end   = off.find( '.' ) - len( off )
        
        return self.__object_file[ start : end ]
    
    
    @property
    def parent( self ):
        if self.__parent:
            return self.__parent._id
        
        return None
    
    
    @property
    def own_metadata_keys( self ):
        return self.__own_metadata_keys
    
    
    @property
    def notes( self ):
        return self.__notes
    
    
    @property
    def _object_file_path( self ):
        """
        Returns the path to the object file for the object.
        """
        return os.path.join( self._id, '_{}.json'.format( self.kind ) )
    
    
    def get_project_root( self ):
        """
        Get's the ultimate root of the container.
        
        :returns: Path of the ultimate project root.
        """
        path = self.path
        while True: 
            parent = os.path.split( path )[ 0 ]
            try:
                if ( self.get_kind( parent ) == 'container' ):
                    # parent is container
                    path = parent
                    
            except RuntimeError as err:
                # parent was not a container, exited project
                return path
    
    
    def inherited_metadata( self ):
        """
        :returns: Dictionary of inherited metadata.
        """
        root = self.get_project_root()
        path = self.path
        
        inherited = {}
        while path != root:
            path = os.path.split( path )[ 0 ] # get parent
            parent_meta = self.load_object_file( path )
            if 'metadata' in parent_meta:
                parent_meta = parent_meta[ 'metadata' ]
                
                # keep lower level metadata, add higher level if it doesn't exist yet
                inherited = { **parent_meta, **inherited } 
        
        return inherited
    
    
    def _parse_path( self, path ):
        """
        Returns the parsed path accounting for `root:` directive.
        """
        root_pattern = '^(root|ROOT):'
        
        if re.search( root_pattern, path ):
            # root in path, absolute path
            # get root_path
            root_path = self.get_project_root()
            path = re.sub( root_pattern, root_path, path )
            path = os.path.normpath( path )
        
        else:
            # root not in path, relative path
            path = os.path.normpath( os.path.join( 
                self._id, path 
            ) )
            
        return path
    
    
    def __getitem__( self, item ):
        if item == '_id':
            return self.path
        
        elif item == 'notes':
            return self.notes
        
        elif item == 'parent':
            return self.parent
        
        else:    
            return self.meta[ item ]
        
    
    def __iter__( self ):
        items = self.meta.copy()
        items[ '_id' ]      = self.path
        items[ 'notes' ]    = self.notes
        items[ 'parent' ]   = self.get( 'parent' )
    
        yield from items
    
    
    def __len__( self ):
        # account for parent, notes, and meta
        count = len( self.meta ) + 2
        
        return count


# In[ ]:


class LocalAsset( LocalObject ):
    """
    An Asset for a Local project.
    """
    
    def __init__( self, path, parent ):
        """
        :param path: Path to the object.
        :param parent: Parent Container.
        """
        super().__init__( path, parent )

        # convert asset file to absolute path
        self.meta[ 'file' ] = self._parse_path( self.meta[ 'file' ] )
        
        
    @property
    def kind( self ):
        return 'asset'
    
    

class LocalContainer( LocalObject ):
    """
    A Container for a Local project.
    """
    
    def __init__( self, path, parent = None ):
        """
        :param path: Path to the object.
        :param parent: Parent Object, or None if root. [Default: None]
        """
        super().__init__( path, parent )
        
        # sort subobjects
        self.__children = []
        self.__assets = []
        for child in glob( os.path.join( self.path, '*/' ) ):
            # iterate over subfolders
            try:
                kind = LocalObject.get_kind( child )
                    
            except RuntimeError as err:
                # child was not an object, ignore
                continue
                                       
            if kind == 'container':
                # convert to container
                self.__children.append( LocalContainer( child, self ) )
            
            elif kind == 'asset':
                # convert to asset
                self.__assets.append( LocalAsset( child, self ) )
         
        # get scripts
        try:
            scripts = _load_json( self._scripts_path() )
            
        except FileNotFoundError as err:
            # scripts file does not exist
            scripts = []
            
        for index, script in enumerate( scripts ):
            # resolve script path
            script[ 'script' ] = self._parse_path( script[ 'script' ] )
            scripts[ index ] = script
            
        self.__scripts = scripts
            
    
    @property
    def is_root( self ):
        """
        :returns: If container is root.
        """
        return ( self.parent is None )
             
    
    @property
    def kind( self ):
        return 'container'
    
        
    @property
    def children( self ):
        return self.__children
    
    
    @property
    def assets( self ):
        return self.__assets
    

    @property
    def scripts( self ):
        return self.__scripts
    
    
    def _scripts_path( self ):
        """
        :returns: Path to the scripts file.
        :raises FileNotFoundError: If file does not exist. 
            Expected path in 'filename' attribute.
        """
        path = os.path.join( 
            self.path, self._object_file_format.format( 'scripts' ) 
        )
        
        if os.path.exists( path ):
            return path
        
        # scripts file does not exist
        raise FileNotFoundError( 2, 'File {} does not exist'.format( path ), path )
    
    
    def __getitem__( self, item ):
        # attempt to retrieve specific attributes first
        if item == 'children':
            return [ child.path for child in self.children ]

        elif item == 'assets':
            return [ asset.path for asset in self.assets ]

        elif item == 'scripts':
            return self.scripts
        
        else:
            return super().__getitem__( item )
                            
    
    def __iter__( self ):
        # TODO [4]: Can refer to super?
        items = self.meta.copy()
        items[ '_id' ]      = self.path
        items[ 'notes' ]    = self.notes
        items[ 'parent' ]   = self.get( 'parent' )
        items[ 'assets' ]   = self.get( 'assets' )
        items[ 'children' ] = self.get( 'children' )
        items[ 'scripts' ]  = self.get( 'scripts' )
        
        yield from items
    
    
    def __len__( self ):
        # account for children, assets, and scripts
        return ( super().__len__() + 3 )
    


# ## DB Objects

# In[ ]:


class LocalCollection():
    """
    Implements a local collection.
    """
    
    def __init__( self, root, kind ):
        """
        :param root: Root Container or path to root folder.
        :param kind: The collection to represent.
        """
        if not isinstance( root, LocalContainer ):
            # create project tree
            root = LocalContainer( root )
        
        self.__root = root
        self.__kind = kind
        
        # collect objects
        def collect_objects( root ):
            """
            Gets object of the same kind of the collection.
            
            :param root: Root object to search.
            :returns: List of LocalObjects with matching kind.
            """
            objs = []
            if self.kind == 'container':
                objs.append( root )
                
            elif self.kind == 'asset':
                objs += root.assets
            
            # recurse on children
            for child in root.children:
                objs += collect_objects( child )
                
            return objs
        
        self.__objects = collect_objects( self.root )
        
        
    @property
    def root( self ):
        return self.__root
        
    
    @property
    def kind( self ):
        return self.__kind
    
    
    def find_one( self, search = {} ):
        """
        Gets a single object matching search critera.
        
        :param search: Dictionary of property-value pairs to filter.
            If {} returns all objects.
            Syntax as is for MongoDB.
            [Default: {}]
        :returns: LocalObject matching search criteria or None.
        """
        result = self.find( search )
        
        return (
            None 
            if ( len( result ) is 0 ) else 
            result[ 0 ]
        )
    
    
    def find( self, search = {} ):
        """
        Gets objects matching search criteria.
        
        :param search: Dictionary of property-value pairs to filter.
            If {} returns all objects.
            Syntax as is for MongoDB.
            [Default: {}]
        :returns: List of LocalObjects matching search criteria.
        """
        def filter_prop( prop, value, obj ):
                """
                Check if object matched property filter.
                
                :param prop: Name of the property to check.
                :param value: Value to match, or Dictionary to recurse.
                :param obj: LocalObject.
                :returns: True if matches, False otherwise.
                """
                # TODO [1]: Children should inherit metadata from ancestors for searches
                # parse prop
                prop_path = prop.split( '.' )
                for part in prop_path:
                    try:
                        obj = obj[ part ]
                
                    except KeyError as err:
                        # property not contained in object
                        return False
                    
                if isinstance( value, list ):
                    # value is list, check for inclusion
                    
                    if isinstance( obj, list ):
                        # object is list, verfiy all values are in object
                        for item in value:
                            if item not in ob:
                                # search item not obj 
                                return false
                            
                        # all items present
                        return true
                        
                    else:
                        # object is not list, can not match
                        return false
                
                else:
                    # value is not list, check for direct match
                    return ( obj == value )
                
               
        
        matching = self.__objects
        for prop, value in search.items():
            obj_fltr = partial( filter_prop, prop, value )
            matching = filter( obj_fltr, matching )
            
        return list( matching )
    
    
    def insert_one( self, path, properties = {} ):
        """
        Insert a new object into the database.
        
        :param path: Path of the object relative to the root.
        :param properties: Properties of the object. [Default: {}]
        :returns: New object.
        """
        if not os.path.exists( path ):
            # create folder for object
            os.mkdir( path )
        
        # check object does not already exist
        try:
            LocalObject.get_object_file( path )
            
        except RuntimeError as err:
            # object file does not exist yet
            pass
            
        else:
            # object file already exists
            raise RuntimeError( 'Object {} already exists.'.format( path ) )
            
        # create object file
        of = LocalObject._object_file_format.format( self.kind )
        
        _id = os.path.normpath( os.path.join( 
            self.root._id, path
        ) )
        
        of_path = os.path.join( _id, of )
        
        self._to_json( of_path, properties )
        
        # Reinitialize to incorporate new object
        # TODO [1]: add object to self
        self.__init__( self.root._id, self.kind )
        
        return self.find_one( { "_id": _id } )

        
    def replace_one( self, path, properties = {}, upsert = False ):
        """
        Replaces an object.
        
        :param path: Path of the object relative to the root.
        :param properties: Properties of the object. [Default: {}]
        :param upsert: Insert new document if it doesn't yet exist.
            [Default: False]
        :returns: Replaced object.
        """
        # TODO [1]: Not working
        # check object already exists
        try:
            LocalObject.get_object_file( path )
            
        except FileNotFoundError as err:
            # object file does not exist yet
            if upsert:
                # allowed to create new object
                self.insert_one( path, properties )
                return
                 
            else:
                raise RuntimeError( 'Object {} does not exists.'.format( path ) )
            
        # create object property file
        of = LocalObject._object_file_format.format( self.kind )
        
        _id = os.path.normpath( os.path.join( 
            self.root._id, path
        ) )
        
        of_path = os.path.join( _id, of )
        
        self._to_json( of_path, properties )
            
        # Reinitialize to incorporate new object
        # TODO [1]: add object to self
        self.__init__( self.root._id, self.kind )
        
        return self.find_one( { "_id": _id } )
        
        
    def _to_json( self, path, properties ):
        """
        Writes properties as JSON to a file.
        
        :param path: Path for the JSON file.
        :param properties: The dicitonary or BaseObject to save.
        """
        json_encoder = ResourceJSONEncoder if isinstance( properties, Resource ) else None

        with open( path, 'w' ) as f:
            json.dump( properties, f, cls = json_encoder, indent = 4 )


# In[ ]:


class LocalDB():
    """
    Implements a local database.
    """
    
    def __init__( self, root ):
        """
        :param root: Path to root folder.
        """
        self.__root = os.path.normpath( root )
        tree = LocalContainer( root )
        
        self.__containers = LocalCollection( tree, 'container' )
        self.__assets     = LocalCollection( tree, 'asset' )
        
    
    @property
    def root( self ):
        return self.__root
    
    
    @property
    def containers( self ):
        return self.__containers
    
    
    @property
    def assets( self ):
        return self.__assets


# # Work

# In[ ]:


# root = os.path.join( os.getcwd(), '../../../_tests/projects/inclined-plane/deg20' )
# db = LocalDB( root )


# In[ ]:


# for asset in db.assets.find():
#     if 'metadata' in asset.meta:
#         print( asset.meta[ 'metadata' ] )


# In[ ]:


# db.containers.replace_one( os.path.join( root, 'test' ), { 'type': 'test' }, upsert = True )


# In[ ]:


# for c in db.containers.find():
#     print( c.meta )


# In[ ]:


# for c in db.assets.find():
#     print(  c.meta )
