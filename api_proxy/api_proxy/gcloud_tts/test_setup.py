from setuptools import setup, find_packages

setup(
    name="gcloud-tts",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "google-cloud-texttospeech>=2.0.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.5.0"
    ],
)
