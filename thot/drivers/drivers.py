
# coding: utf-8

# # Drivers

# In[ ]:


from .aws_s3 import ThotS3Driver


# In[ ]:


def get_driver( driver ):
        """
        Gets an asset driver.
        
        :param driver: Name of the driver to retrieve.
        :returns: Instantiation fo the driver. 
        """
        if not driver:
            return None
        
        elif driver == 'aws_s3':
            # AWS S3 driver
            return ThotS3Driver
        
        else:
            raise ValueError( 'Invalid driver name' )

