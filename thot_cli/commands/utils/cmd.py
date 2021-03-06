import os
import json

from ..command import Command
from .utilities import ThotUtilities


class Utils( Command ):
    """
    Thot utilities commands.
    """

    def run( self, args ):
        """
        """

        def _arg_to_json( arg, default = None ):
            """
            :param arg: None or string to parse.
            :param default: Value to return if arg is None. [Defualt: None]
            :returns: Default value if arg is None, otherwise attempts to parse args as JSON.
            """
            return (
                default
                if ( arg is None ) else
                json.loads( arg )
            )


        def set_defaults( params, defaults, whitelist = True ):
            """
            :param params: Dictionary of input parameters.
            :param defaults: Dictionary of default parameters or list if all values are None.
            :param whitelist: Remove any fields not listed in defaults. [Default: True]
            :returns: Dictionary with defaults set.
            """
            if isinstance( defaults, list ):
                defaults = { key: None for key in defaults }

            if params is None:
                params = {}

            params = {  **defaults, **params }
            if whitelist:
                # sanitize params based on defaults
                params = { key: val for key, val in params.items() if key in defaults }

            return params
        

        # TODO [0]: Fix parse errors for Windows machines
        modified = None
        util = ThotUtilities( os.path.abspath( args.root ) )
        fcn  = args.function

        if fcn == 'add_scripts':
            scripts = json.loads( args.scripts )
            search  = json.loads( args.search )

            modified = util.add_scripts( scripts, search, overwrite = args.overwrite )

        elif fcn == 'remove_scripts':
            try:
                scripts = json.loads( args.scripts )

            except json.decoder.JSONDecodeError as err:
                # single script passed in
                scripts = args.scripts

            search = _arg_to_json( args.search, {} )

            modified = util.remove_scripts( scripts, search )

        elif fcn == 'set_scripts':
            scripts = json.loads( args.scripts )
            search  = json.loads( args.search )

            modified = util.set_scripts( scripts, search )

        elif fcn =='add_assets':
            assets = json.loads( args.assets )
            search = json.loads( args.search )

            modified = util.add_assets( assets, search, overwrite = args.overwrite )

        elif fcn == 'remove_assets':
            assets = json.loads( args.assets )
            search = _arg_to_json( args.search )

            modified = util.remove_assets( assets, search )

        elif fcn == 'data_to_assets':
            try:
                properties = _arg_to_json( args.assets )

            except json.decoder.JSONDecodeError:
                # could not parse assets as json
                # attempt as function
                properties = eval( args.assets )

            defaults = [ '_id', 'rename' ]
            kwargs = set_defaults( args.kwargs, defaults )

            # parse _id as function
            _id = (
                eval( kwargs[ '_id' ] )
                if ( kwargs[ '_id' ] is not None ) else
                None
            )

            if kwargs[ 'rename' ] is not None:
                # parse rename as function or string
                try:
                    # parse as function
                    rename = eval( kwargs[ 'rename' ] )

                except NameError as err:
                    # rename not function, string
                    rename = kwargs[ 'rename' ]

            else:
                rename = kwargs[ 'rename' ]

            assets = util.data_to_asset(
                args.root,
                search = args.search,
                properties = properties,
                _id = _id,
                rename = rename
            )

            print( assets )

        elif fcn == 'add_containers':
            containers = json.loads( args.containers )
            search = json.loads( args.search )

            modified = util.add_containers( containers, search, overwrite = args.overwrite )

        elif fcn == 'remove_containers':
            containers = json.loads( args.containers )
            search = _arg_to_json( args.search )

            modified = util.remove_containers( containers, search )

        elif fcn == 'print_tree':
            properties = _arg_to_json( args.containers )
            assets     = _arg_to_json( args.assets )
            scripts    = _arg_to_json( args.scripts )

            util.print_tree( properties = properties, assets = assets, scripts = scripts )

        else:
            raise ValueError( 'Invalid function {}. Use `python -m thot.utilities -h` for help.' )


        if modified:
            for obj in modified:
                print( obj._id )




    def init_parser( self, parser ):
        """
        Initializes a parser for the `utils` command.

        :returns: Utilities parser.
        """
        parser.add_argument(
            'function',
            type = str,
            default = '.',
            help = 'Function to run.'
        )

        parser.add_argument(
            '-r', '--root',
            type = str,
            default = '.',
            help = 'Path or ID of the root Container.'
        )

        parser.add_argument(
            '-s', '--search',
            type = str,
            help = 'JSON object or glob describing Containers to target. Format depends on function.'
        )

        parser.add_argument(
            '--scripts',
            type = str,
            help = 'Scripts object. Format depends on function.'
        )

        parser.add_argument(
            '--assets',
            type = str,
            help = 'Assets object. Format depends on function.'
        )

        parser.add_argument(
            '--containers',
            type = str,
            help = 'Containers object. Format depends on function.'
        )

        parser.add_argument(
            '-w', '--overwrite',
            action = 'store_true',
            help = 'Allows overwriting objects if they already exist.'
        )

        parser.add_argument(
            '--kwargs',
            type = json.loads,
            help = 'Additional keyword arguments. Allowed values depends on the function being called.'
        )


        return super().init_parser( parser )
        # parser.set_defaults( _fn = self.run )
        # return parser
