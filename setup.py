import setuptools

with open( 'README.rst', 'r' ) as f:
	long_desc = f.read()

classifiers = [
	"Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
]

project_urls = {
	'Documentation': 	'https://thot-data-docs.readthedocs.io/',
	'Source Code': 		'https://github.com/bicarlsen/thot-data',
	'Bug Tracker':		'https://github.com/bicarlsen/thot-data/issues'
}


setuptools.setup(
	name='thot-data',
	version = '0.4.6',
	author='Brian Carlsen',
	author_email = 'carlsen.bri@gmail.com',
	description = 'Thot data analysis and management.',
	long_description = long_desc,
	long_description_content_type = 'text/x-rst',
	url = 'http://www.thot-data.com',
	packages = setuptools.find_packages(),
	project_urls = project_urls,
	classifiers = classifiers,
	
	install_requires = [
		'thot-core>=0.4.5'
	],

	package_data = {
	},

	entry_points = {
		'console_scripts': []
	}
)