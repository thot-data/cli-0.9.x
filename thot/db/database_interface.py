
# coding: utf-8

# # Database Interface

# In[1]:


from abc import ABC, abstractmethod


# In[ ]:


class DatabaseInterface( ABC ):
    
    @abstractmethod
    def insert_one( self, obj ):
        """
        Insert a single object.
        
        :param obj: Object to insert.
        """
        pass
    
    
    @abstractmethod
    def insert_many( self, objs ):
        """
        Insert a multiple objects.
        
        :param objs: List of object to insert.
        """
        pass
    
    
    @abstractmethod
    def replace_one( self, search, obj ):
        """
        Replace a single object.
        
        :param search: Dictionary to filter objects.
        :param obj: Object to insert.
        """
        pass
    
    
    @abstractmethod
    def update_one( self, search, update ):
        """
        Update a single object.
        
        :param search: Dictionary to filter objects.
        :param update: Dictionary to update.
        """
        pass
    
    
    @abstractmethod
    def update_many( self, search, update ):
        """
        Update multiple objects.
        
        :param search: Dictionary to filter objects.
        :param update: Dictionary to update.
        """
        pass
    
    
    @abstractmethod
    def delete_one( self, search, update ):
        """
        Delete a single object.
        
        :param search: Dictionary to filter objects.
        """
        pass
    
    
    @abstractmethod
    def delete_many( self, search, update ):
        """
        Delete multiple objects.
        
        :param search: Dictionary to filter objects.
        """
        pass
    
    
    @abstractmethod
    def find( self, search ):
        """
        Finds an object.
        
        :param search: Dictionary to filter objects.
        """
        pass
    
    
    @abstractmethod
    def find_one( self, search ):
        """
        Finds an object.
        
        :param search: Dictionary to filter objects.
        """
        pass

