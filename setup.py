from setuptools import setup

setup(
    name="PythonChess",
    version="0.2",
    packages=["PythonChess"],
    package_dir={"PythonChess": "PythonChess"},
    install_requires=["pythonchess", "tqdm", "pyqt5"],
    # package_data={"figletgui": ["ru/LC_MESSAGES/*.mo"]},
)
