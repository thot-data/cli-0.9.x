import os

import pandas as pd

from thot.thot import LocalProject

thot = LocalProject()

sample 		= thot.find_container( { 'type': 'sample'  } )
data 		= thot.find_asset( { 'type': 'times' } )
reference 	= thot.find_asset( { 'type': 'reference' } )

df 	= pd.read_csv( data.file )
rdf = pd.read_csv( reference.file )

stats = df.mean()

stats_props = {
	'file': 'stats.csv',
	'type': 'stats',
	'name': '{} Stats'.format( sample.name )
}

stats.to_csv( 
	thot.add_asset( stats_props, 'stats', overwrite = True )
)

	
