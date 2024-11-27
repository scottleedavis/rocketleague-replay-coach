from setuptools import setup, find_packages

setup(
    name="rocketleague-replay-coach",
    version="0.1.0",
    author="Scott Lee Davis",
    description="A tool for analyzing Rocket League replays with player performance insights.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/scottleedavis/rocketleague-replay-coach",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=[
        "openai",
        "numpy",
        "pandas",
        "matplotlib",
    ],
    entry_points={
        "console_scripts": [
            "rocketleague-replay-coach=rocketleague_replay_coach.main:main",
        ]
    },
)
