import setuptools

with open( 'README.md', 'r' ) as f:
	long_desc = f.read()

setuptools.setup(
	name='thot-data',
	version = '0.0.3',
	author='Brian Carlsen',
	author_email = 'carlsen.bri@gmail.com',
	description = 'Thot data analysis and management.',
	long_description = long_desc,
	long_description_content_type = 'text/markdown',
	# url = 'https://github.com/bicarlsen/thot.git',
	packages = setuptools.find_packages(),
	
	classifiers = [
		"Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
	],
	
	package_data = {
	},

	entry_points = {
		'console_scripts': [
		]
	}
)