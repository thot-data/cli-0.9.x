
# coding: utf-8

# # Asset

# In[28]:


from .resource import Resource


# In[25]:


class Asset( Resource ):
    """
    An Asset.
    """
    
    def __init__( self, **kwargs ):
        """
        Creates a new Asset.
        
        :param **kwargs: Initial property values.
        """
        defaults = {
            'file':         None,
            'parent':       None,
            'creator':      None,
            'creator_type': None,
        }
        
        super().__init__( kwargs, defaults )

