import unittest

class TestThot( unittest.TestCase ):

	def test_import( self ):
		from thot import thot
		self.assertTrue( thot._root_container )


if __name__ == '__main__':
	unittest.main()