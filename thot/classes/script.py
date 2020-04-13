
# coding: utf-8

# # Script

# In[ ]:


from .base_object import BaseObject
from .resource import Resource


# In[ ]:


class Script( Resource ):
    """
    A Script.
    """
    
    def __init__( self, **kwargs ):
        """
        Creates a new Asset.
        
        :param **kwargs: Initial property values.
        """
        defaults = {
            'file':         None,
            'language':     None,
            'description':  None,
            'version':      0
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
            'autorun':  True
        }
        
        super().__init__( kwargs, defaults )
        
        
    def __lt__( self, other ):
        """
        Defines comparison based on priority.
        
        :param other: ScriptAssociation for comparison.
        :returns: True if priority is less than other, False otherwise.
        """
        return ( self.priority < other.priority )
        

