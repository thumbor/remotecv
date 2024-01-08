from pathlib import Path

from setuptools import setup


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

with open("remotecv/__init__.py", encoding="utf-8") as f:
    ns = {}
    exec(f.read(), ns)  # pylint: disable=exec-used
    version = ns["__version__"]


TESTS_REQUIREMENTS = [
    "black==23.*,>=23.12.1",
    "celery==5.*,>=5.3.6",
    "coverage==7.*,>=7.4.0",
    "flake8==7.*,>=7.0.0",
    "pre-commit==3.*,>=3.6.0",
    "preggy==1.*,>=1.4.4",
    "pylint==3.*,>=3.0.3",
    "pyssim==0.*,>=0.7",
    "pytest-asyncio==0.*,>=0.23.0",
    "pytest-cov==4.*,>=4.1.0",
    "pytest==7.*,>=7.4.0",
    "thumbor==7.*,>=7.7.2",
]

RUNTIME_REQUIREMENTS = [
    "opencv-python-headless==4.*,>=4.9.0.80",
    "Pillow==10.*,<10.1.0",
    "pyres==1.*,>=1.5",
    "redis==5.*,>=5.0.1",
    "sentry-sdk==1.*,>=1.39.1",
    "click==8.*,>=8.1.7",
    "click-option-group==0.*,>=0.5.6",
]

setup(
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="remotecv",
    url="https://github.com/thumbor/remotecv",
    version=version,
    description="remotecv is an OpenCV worker for facial and feature recognition",
    python_requires="==3.*,>=3.9.0",
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
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
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
