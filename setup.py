from setuptools import setup, find_packages

requirements:list = []
with open("requirements.txt", "r") as file:
	requirements = file.readlines()

setup(
	name="cclr",
	version="0.0.0B",
	author="Blaze the Star",
	author_email="startheblaze@gmail.com",
	packages=find_packages(),
	install_requires=requirements,
	entry_points={
		"console_scripts":[
			"cclr = cclr.entry:main"
		]
	}
)