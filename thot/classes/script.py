
# coding: utf-8

# # Script

# In[1]:


from datetime import datetime

from .base_object import BaseObject
from .role import Role
from .note import Note
from .metadata import Metadata


# In[ ]:


class Script( BaseObject ):
    """
    A Script.
    """
    
    def __init__( self, **kwargs ):
        """
        Creates a new Asset.
        
        :param **kwargs: Initial property values.
        """
        defaults = {
            'created':      datetime.now(),
            'name':         None,
            'file':         None,
            'language':     None,
            'description':  None,
            'version':      0,
            'tags':         [],
            'roles':        [],
            'notes':        []
        }
        
        super().__init__( kwargs, defaults )


# In[ ]:


class ScriptAssociation( BaseObject ):
    """
    A ScriptAssociation
    """
    
    def __init__( self, **kwargs ):
        """
        :param **kwargs: Initial property values.
        """
        defaults = {
            'script': None,
            'priority': 0,
            'autorun':  False
        }
        
        super().__init__( kwargs, defaults )
        del self._id # remove _id field
        
        
    def __lt__( self, other ):
        """
        Defines comparison based on priority.
        
        :param other: ScriptAssociation for comparison.
        :returns: True if priority is less than other, False otherwise.
        """
        return ( self.priority < other.priority )
    
    
    def __json__( self ):
        """
        :returns: Dictionary to write to JSON.
        """
        return {
            'script': self.script,
            'priority': self.priority,
            'autorun': self.autorun
        }
        

