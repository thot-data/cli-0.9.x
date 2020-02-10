
# coding: utf-8

# # Asset

# In[28]:


from datetime import datetime

from .base_object import BaseObject
from .role import Role
from .note import Note
from .metadata import Metadata


# In[25]:


class Asset( BaseObject ):
    """
    An Asset.
    """
    
    def __init__( self, **kwargs ):
        """
        Creates a new Asset.
        
        :param **kwargs: Initial property values.
        """
        defaults = {
            'created':      datetime.now(),
            'type':         None,
            'name':         None,
            'file':         None,
            'description':  None,
            'creator':      None,
            'creator_type': None,
            'roles':        [],
            'notes':        [],
            'metadata':     {}
        }
        
        super().__init__( kwargs, defaults )
        
    
    @classmethod
    def by_name( name, many = False ):
        """
        Get Assets by name.
        
        :param name: Asset name.
        :param many: Return a List even if only one result is found. [Default: False]
        :returns: List of, or single Asset.
        """
        pass
    
    
    @classmethod
    def by_type( kind, many = False ):
        """
        Get Assets by type.
        
        :param kind: Kind of Asset.
        :param many: Return a List even if only one result is found. [Default: False]
        :returns: List of, or single Asset.
        """
        pass
    
    
    @classmethod
    def by_metadata( metadata, many = False ):
        """
        Gets Assets by metadata.
        
        :param metadata: Dictionary of metadata filter.
        :param many: Return a List even if only one result is found. [Default: False]
        :returns: List of, or single Asset.
        """
        pass
    

