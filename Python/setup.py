from setuptools import setup

setup(
        name="openetran_py3",
        version="1.0.0",
        license="GPL v3 License",
        packages=["openetran_py3"],
		package_data={"openetran_py3": ["win/*"]},
        description="OpenEtran executable and GUI",
        author="Matthieu Bertin",
        author_email="MAB522@pitt.edu",
		url="https://github.com/MAB522/OpenETran",
        install_requires=[
            "PyQt5>=5.6",
            "matplotlib==2.0.2"
        ],
		entry_points={"console_scripts": "openetran_py3 = openetran_py3.GUI:main"},
		scripts={"postinst.py"},
		zip_safe=False
     )