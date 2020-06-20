from setuptools import setup

setup(
    name="PythonChess",
    version="0.2",
    packages=["PythonChess"],
    package_dir={"PythonChess": "PythonChess"},
    install_requires=["tqdm", "pyqt5"],
    package_data={"PythonChess": ["./*.dat", "./styles.qss", "ru/LC_MESSAGES/*.mo",
                                  "./images/*", "./images/beat/*", "./images/merida/*",
                                  "./images/moved/*", "./images/pressed/*", "./images/default/*"]},
)
