
# coding: utf-8

# # Driver interface

# In[3]:


from abc import ABC, abstractmethod


# In[4]:


class DriverInterface( ABC ):
    """
    Interface for drivers.
    """
    
    @abstractmethod
    def output_asset( self, asset ):
        """
        Modifies asset coming from the database, going to the user.
        
        :param asset: Assets to modify.
        :returns: Modified asset.
        """
        pass
    
    
    @abstractmethod
    def output_assets( self, assets ):
        """
        Modifies Assets coming from the database, going to the user.
        
        :param assets: List of Assets to modify.
        :returns: List of modified Assets.
        """
        pass
    
    
    @abstractmethod
    def input_asset( self, asset ):
        """
        Modifies an asset coming from the user, going to the database.
        
        :param asset: Asset to be modified.
        :returns: The modified asset.
        """
        pass
    
    
    @abstractmethod
    def get_script( self, script ):
        """
        Gets the specified script if needed, returning the local path to it.
        
        :param script: Path to the script.
        :returns: Local path.
        """
        pass

