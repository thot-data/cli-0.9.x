from abc import ABC


class Command( ABC ):
    """
    A Command line interface command.
    """
    def __init__( self, parser ):
        """
        :param parser: Argument parser.
        """
        self.init_parser( parser )
    

    def run( self, args ):
        """
        Run the command.

        :param args: Parsed arguments.
        """
        pass


    def init_parser( self, parser ):
        """
        Create command line arguemnts parser.

        :param parser: ArgumentParser.
        """
        parser.set_defaults( _fn = self.run )
        return parser
