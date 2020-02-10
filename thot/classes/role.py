
# coding: utf-8

# # Role

# In[1]:


from .base_object import BaseObject


# In[ ]:


class Role( BaseObject ):
    """
    Represents a role.
    """
    
    def __init__( self, **kwargs ):
        """
        :params **kwargs: Initial parameters
        """
        defaults = {
            '_id':    None, # remove _id field
            'user': None,
            'role': None
        }
        
        super().__init__( kwargs, defaults )

