
# coding: utf-8

# # Base Object

# In[6]:


import random
import json
from collections.abc import Mapping


# In[7]:


class BaseObject( Mapping ):
    """
    Base object.
    """
    
    def __init__( self, properties, defaults ):
        """
        Creates a new BaseObject.
        
        :param properties: Initial property values. 
        :param defaults: Default property values.
        """
        # add _id to defaults
        defaults[ '_id' ] = str( random.random() )[ :2 ]
        
        self._properties = defaults.keys() # save white listed names
        
        properties = { **defaults, **properties } # set defaults
        for prop in self._properties:
            val = properties[ prop ]
            
            if ( prop is 'metadata' ) and isinstance( val, list ):
                md = {}
                
                # convert metadata list to dictionary
                for datum in val:
                    md_val = datum.value
                    
                    # cast value to correct type, comes as string
                    if datum.type is 'number':
                        md_val = float( md_val )
                        
                    elif datum.type is 'json':
                        md_val = json.loads( md_val )
        
                    md[ datum.name ] = md_val
                
                val = md
                
            setattr( self, prop, val )
        
    
    @property
    def properties( self ):
        """
        :returns: List of valid properties.
        """
        return self._properties
    
    
    def __getitem__( self, item ):
        if item is '_properties':
            raise KeyError( item )
        
        return getattr( self, item )
        
    
    def __len__( self ):
        return len( self.__dict__ )
    

    def __iter__( self ):
        d = self.__dict__.copy()
        del d[ '_properties' ]
        
        yield from d
            
    
    def __json__( self ):
        """
        :returns: Dictionary to write to JSON.
        """
        return dict( self )


# In[8]:


class BaseObjectJSONEncoder( json.JSONEncoder ):
    """
    JSON encoder for Base Objects.
    """
    
    def default( self, obj ):
        
        if isinstance( obj, BaseObject ):
            return obj.__json__()
        
        else:
            raise TypeError( 'Object is not a BaseObject.' )
        
    


# # Work
