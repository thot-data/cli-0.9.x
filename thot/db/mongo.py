
# coding: utf-8

# # Mongo Config
# Configuration MongoDB

# In[4]:


import os
from pymongo import MongoClient


# In[8]:


class MongoDB():
    """
    Hold a Mongo DB connection.
    """
    
    _connection_string = None

    def __init__( self, connection_string = None, database = 'thot' ):
        """
        :param connection_string: Connection string to use or None.
            If None will attempt to get connection string from 
            environement variable THOT_DB_URI. If not found
            will default to 'mongodb://localhost:27017'.
            [Default: None]
            
        :param database: Name of the database to use. [Default: thot]
        """
        #TODO [2]: Share connection across instances
        self.__set_connection_string( connection_string )
        
        client = MongoClient( self._connection_string )
        self.__db = client[ database ]
        
        
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
        
        
    def __set_connection_string( self, connection_string = None ):
        """
        Sets the connection string.
        
        :param connection_string: If None will attempt to get 
            connection string from environement variable THOT_DB_URI. 
            If not found will default to 'mongodb://localhost:27017'.
            [Default: None]
        """
        if connection_string is not None:
            self._connection_string = connection_string
            return
        
        # connection string not passed
        try:
            self._connection_string = os.environ[ 'THOT_DB_URI' ]
            
        except KeyError as err:
            # environment variable not set
            # use default
            self._connection_string = 'mongodb://localhost:27017'


# # Work

# In[9]:


# db = MongoDB()

