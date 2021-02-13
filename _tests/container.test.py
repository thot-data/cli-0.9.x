import os
import unittest

import thot
from thot.container import Container

class TestContainer( unittest.TestCase ):

	def test_by_id( self ):
		container = Container.by_id( '5dc20ac5034ebe60c8e34fbc' )
		self.assertTrue( container )


if __name__ == '__main__':
	unittest.main()