
# coding: utf-8

# # Mongo Config
# Configuration MongoDB

# In[1]:


from pymongo import MongoClient


# In[8]:


class MongoDB():
    """
    Hold a Mongo DB connection.
    """
    
    _connection_string = 'mongodb://localhost:27017/thot'

    def __init__( self ):
        """
        """
        # TODO [2]: Share connection across instances
        client = MongoClient( self._connection_string )
        self.__db = client.thot
        
        
    def __getattr__( self, item ):
        """
        Only expose desired collections.
        
        :param item: 
        """
        visible = [ 
            'containers', 
            'assets' 
        ]
        
        hidden = [ # must be prefixed by underscore
            '_scripts'
        ]
        
        if item in visible:
            return getattr( self.__db, item )
        
        elif item in hidden:
            return getattr( self.__db, item[ 1: ] )
        
        # item was not white listed
        raise AttributeError( 'Attribute {} is not accessible.'.format( item ) )


# # Work

# In[9]:


# db = MongoDB( None )

