from setuptools import setup, find_packages

setup(
    name="dual-process-lm",
    version="0.1.0",
    description="Dual-process language model: masked diffusion (System 1) + autoregressive (System 2)",
    packages=find_packages(),
    python_requires=">=3.11",
)
