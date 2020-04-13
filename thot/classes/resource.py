
# coding: utf-8

# In[ ]:


import random
from datetime import datetime
from json import JSONEncoder

from .base_object import BaseObject
from .role import Role
from .note import Note
from .metadata import Metadata


# In[ ]:


class Resource( BaseObject ):
    
    def __init__( self, properties, defaults ):
        """
        Creates a new Resource.
        
        :param properties: Initial property values. 
        :param defaults: Default property values.
        """       
        resource_defaults = {
            '_id':          None,
            'created':      datetime.now(),
            'type':         None,
            'name':         None,
            'description':  None,
            'roles':        [],
            'tags':         [],
            'notes':        [],
            'metadata':     {}
        }
        
        # merge defaults
        defaults = { **resource_defaults, **defaults }
        
        super().__init__( properties, defaults )
        
        
    def __json__( self ):
        """
        Returns a dictionary to write to JSON.
        """        
        obj = dict( self )
        
        if isinstance( obj[ 'created' ], datetime ):
            # convert datetime to string
            time_format = '%Y-%m-%dT%H:%M:%S%Z' # yyyy-mm-ddThh:mm:ss+/-<UTC offset>
            obj[ 'created' ] = obj[ 'created' ].strftime( time_format )
        
        return obj


# In[ ]:


class ResourceJSONEncoder( JSONEncoder ):
    """
    JSON encoder for Base Objects.
    """
    
    def default( self, obj ):
        if isinstance( obj, Resource ):
            return obj.__json__()
        
        else:
            super().default()

