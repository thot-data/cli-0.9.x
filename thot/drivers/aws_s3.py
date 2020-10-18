
# coding: utf-8

# In[1]:


import os
import re
import json
import boto3

from .driver_interface import DriverInterface


# In[9]:


class ThotS3Driver( DriverInterface ):
    """
    Allows data access from AWS S3 servers.
    """
    
    def __init__( 
        self, 
        aws_access_key_id, 
        aws_secret_access_key,
        bucket = None
    ):
        """
        Initializes the client.
        """
        
        if not ( aws_access_key_id and aws_secret_access_key ):
            raise Exception( 'Credentials not provided' )
            
        # initilaize client
        self._s3 = boto3.client(
            's3',
            aws_access_key_id = aws_access_key_id,
            aws_secret_access_key = aws_secret_access_key
        )
        
        self._bucket = bucket or os.environ[ 'AWS_S3_BUCKET' ]
        
        # added assets
        self.added_assets = []

        # AWS S3 UR
        self.aws_s3_url = 'https://{}.s3.amazonaws.com/'.format( self._get_bucket() )
        
        # RegEx for the AWS S3 URL. First group is path name.
        self.aws_s3_url_pattern = re.compile( '^{}(.*)'.format( self.aws_s3_url ) )
        
        # run upload and download in main thread for blocking
        self.transfer_config = boto3.s3.transfer.TransferConfig(
            use_threads = False
        )
    
        
        
    def output_asset( self, asset ):
        """
        Modifies an asset coming from the database, going to the user.
        Checks if file matches a valid AWS S3 URL.
        If not, does not modify tha file.
        If it does, verfies the file is available locally,
        downloading it if necessary.
        Modifies the asset's file to the local path.
        
        :param assets: Assets to modify.
        :returns: Modified assets.
        """
        
        match = self.aws_s3_url_pattern.match( asset[ 'file' ] )
        if match is None:
            # did not match, do not modify
            return asset

        # valid aws s3 url
        local_path = match.group( 1 )

        # download file if necessary
        if not os.path.isfile( local_path ):
            self.download_file( local_path, local_path )

        # valid aws s3 url, strip url leaving path only
        asset[ 'file' ] = local_path
        return asset
        
        
    def output_assets( self, assets ):
        """
        Modifies assets coming from the database, going to the user.
        Checks if file matches a valid AWS S3 URL.
        If not, does not modify tha file.
        If it does, verfies the file is available locally,
        downloading it if necessary.
        Modifies the Asset's file to the local path.
        
        :param assets: List of Assets to modify.
        :returns: List of modified Assets.
        """
        return [ self.output_asset( asset ) for asset in assets ]
    
    
    def input_asset( self, asset ):
        """
        Modifies an asset coming from the user, going to the database.
        Modifies the path to be a valid 
        
        :param asset: Asset to be modified.
        :returns: The modified asset.
        """
        # add path to added assets
        added = {
            'path':  asset[ 'file' ],
            'base':  self.normalize_asset_path( asset[ 'file' ] ),
            'saved': False 
        }
        
        self.added_assets.append( added )
        
        # output path for collection
        print( json.dumps( added ) )
        
        # modify asset file to be an aws s3 url
        asset[ 'file' ] = self.to_aws_s3_url( asset[ 'file' ] ) 
        
        return asset
    
    
    def get_script( self, script ):
        """
        Gets the specified script if needed, returning the local path to it.
        
        :param script: Path to the script.
        :returns: Local path.
        """
        match = self.aws_s3_url_pattern.match( script )
        if match is None:
            # did not match, do not modify
            return script

        # valid aws s3 url
        local_path = match.group( 1 )

        # download file if necessary
        if not os.path.isfile( local_path ):
            self.download_file( local_path, local_path )
            
        return local_path
    
    
    def normalize_asset_path( self, path ):
        """
        Normalizes an assset path.
        Takes basename of the path and prepends the canonical asset directory.
        
        :param path: Path to normalize.
        :returns: Normalized path.
        """
        # get file name form path
        file_name = os.path.split( path )
        file_name = file_name[ 1 ] or file_name[ 0 ]
        
        # get asset directory
        try:
            asset_dir = os.environ[ 'THOT_ASSET_DIRECTORY' ]
        
        except KeyError as err:
            # asset directory does not exist
            return file_name
        
        # asset directory exists
        # prepend asset directory
        return os.path.join( asset_dir, file_name )
        
    
    def to_aws_s3_url( self, path ):
        """
        Prepends the AWS S3 URL to the path.
        
        :param path: Local path of resource.
        :returns: Corresponding AWS S3 URL.
        """
        path = self.normalize_asset_path( path )
        return '{}{}'.format( self.aws_s3_url, path )
        
        
    def get_file( self, path, bucket = None ):
        """
        Retreives a file.
        
        :param path: Path to the object.
        :param bucket: S3 Bucket or None to use default. [Default: None]
        :returns: Contents of the retrieved file.
        """
        bucket = self._get_bucket( bucket )
        obj = self._s3.get_object( Bucket = bucket, Key = path )
        
        content = obj[ 'Body' ].read()
        return content.decode()
    
    
    def download_file( self, file, path, bucket = None ):
        """
        Downloads a file.
        
        :param file: Download path.
        :param path: Path to file.
        :param bucket: S3 Bucket or None to use default. [Default: None]
        """
        file = os.path.join( os.environ[ 'THOT_SERVER_ROOT' ], file )
        bucket = self._get_bucket( bucket )
        
        try:
            self._s3.download_file( 
                Bucket = bucket, 
                Key = path, 
                Filename = file,
                Config = self.transfer_config
            )
        
        except botocore.exceptions.ClientError as err:
            err.cmd = 'While retrieving {}: {}'.format( self.to_aws_s3_url( path ), err )
    
    
    def upload_file( self, file, path, bucket = None ):
        """
        Uploads a file.
        
        :param file: File to upload.
        :param path: Upload path.
        :param bucket: S3 Bucket or None to use default. [Default: None]
        :returns: Response from the upload.
        """
        bucket = self._get_bucket( bucket )
        self._s3.upload_file( 
            Bucket = bucket, 
            Key = path, 
            Filename = file,
            Config = self.transfer_config
        )
    
    
    def flush_added_assets( self ):
        for asset in self.added_assets:
            if not asset[ 'saved' ]:
                self.upload_file( asset[ 'path' ], asset[ 'base' ] )
                asset[ 'saved' ] = True
        
        
    def _get_bucket( self, bucket = None ):
        """
        Returns the bucket passed if valid, otherwise the default bucket.
        
        :param bucket: The bucket to be checked. [Default: None]
        :returns: Passed bucket if defined or default bucket.
        :raises: Error if neither the passed bucket or default bucket are defined.
        """
        valid = ( bucket or self._bucket )
        
        if not valid:
            raise ValueError( 'Invalid bucket.' )
            
        return valid
        


# # Work
