
# coding: utf-8

# # Container

# In[ ]:


from .resource import Resource
from .script import ScriptAssociation
from .role import Role


# In[ ]:


class Container( Resource ):
    """
    A Container.
    """
    
    def __init__( self, **kwargs ):
        """
        Creates a new Container.
        
        :param **kwargs: Initial property values.
        """
        defaults = {
            'parent':       None,
            'children':     [],
            'assets':       [],
            'scripts':      []
        }
        
        super().__init__( kwargs, defaults )
        
        # roles
        for index, role in enumerate( self.roles ):
            self.roles[ index ] = Role( **role )
    
        # scripts
        for index, script in enumerate( self.scripts ):
            self.scripts[ index ] = ScriptAssociation( **script )
    
    
    
#     def find_descendants( self, search = {}, level = None ):
#         """
#         Gets descendents.
        
#         :param match: Dictionary filter or None for no filter. [Default: None]
#         :param level:
#         :returns: List of Containers.
#         """
#         pass
    
    
#     def find_assets( self, search = {} ):
#         """
        
#         """
#         pass
    
    
#     def find_scritps( self, search = {} ):
#         """
        
#         """
#         pass

