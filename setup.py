from pathlib import Path

from setuptools import setup


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

with open("remotecv/__init__.py", encoding="utf-8") as f:
    ns = {}
    exec(f.read(), ns)  # pylint: disable=exec-used
    version = ns["__version__"]


TESTS_REQUIREMENTS = [
    "black==22.*,>=22.1.0",
    "celery==5.*,>=5.2.7",
    "coverage==6.*,>=6.3.2",
    "flake8==4.*,>=4.0.1",
    "pre-commit==2.*,>=2.20.0",
    "preggy==1.*,>=1.4.4",
    "pylint==2.*,>=2.13.8",
    "pyssim==0.*,>=0.4",
    "pytest-asyncio==0.*,>=0.18.0",
    "pytest-cov==3.*,>=3.0.0",
    "pytest==7.*,>=7.0.0",
    "thumbor==7.*",
]

RUNTIME_REQUIREMENTS = [
    "opencv-python-headless==4.*,>=4.2.0",
    "Pillow>=9.0.0",
    "pyres==1.*,>=1.5.0",
    "redis==4.*,>=4.2.0",
    "sentry-sdk==0.*,>=0.14.2",
    "click==8.*",
    "click-option-group==0.5.*",
]

setup(
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="remotecv",
    version=version,
    description="remotecv is an OpenCV worker for facial and feature recognition",
    python_requires="==3.*,>=3.7.0",
    author="Bernardo Heynemann",
    author_email="heynemann@gmail.com",
    license="MIT",
    entry_points={"console_scripts": ["remotecv = remotecv.worker:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Multimedia :: Graphics :: Presentation",
    ],
    packages=[
        "remotecv",
        "remotecv.detectors",
        "remotecv.detectors.complete_detector",
        "remotecv.detectors.face_detector",
        "remotecv.detectors.feature_detector",
        "remotecv.detectors.glasses_detector",
        "remotecv.detectors.profile_detector",
        "remotecv.metrics",
        "remotecv.result_store",
    ],
    package_dir={"": "."},
    package_data={
        "remotecv.detectors.face_detector": ["*.xml"],
        "remotecv.detectors.glasses_detector": ["*.xml"],
        "remotecv.detectors.profile_detector": ["*.xml"],
    },
    install_requires=[RUNTIME_REQUIREMENTS],
    extras_require={"dev": [RUNTIME_REQUIREMENTS + TESTS_REQUIREMENTS]},
)
