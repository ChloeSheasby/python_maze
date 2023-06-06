from setuptools import find_packages, setup

setup(
    name="maze_game",
    version="1.0.0",
    description="This project generates a maze using multiple different AI tools.",
    author="Chloe Sheasby",
    # author_email="your.email@example.com",
    # url="https://github.com/yourusername/my_project",
    packages=find_packages(include=["maze_generator", "maze_generator.*"]),
    # install_requires=[
    #     "numpy>=1.19.0",
    #     "pandas>=1.1.0",
    # ],
    tests_require=["pytest"],
    
)
