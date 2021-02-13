import os

import pandas as pd

from thot.thot import ThotProject

thot = ThotProject()

sample = thot.find_container( { 'type': 'sample'  } )
data = thot.find_asset( { 'type': 'roll-times' } )

df = pd.read_csv( data.file )
stats = df.mean()

stats_props = {
	'type': 'stats',
	'name': '{} Stats'.format( sample.name ),
	'file': '.csv'
}

stats.to_csv( 
	thot.add_asset( stats_props )
)

	
