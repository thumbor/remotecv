from setuptools import setup

readme = ""

TESTS_REQUIREMENTS = [
    "celery==4.*,>=4.4.1",
    "flake8==3.*,>=3.7.9",
    "pylint==2.*,>=2.4.4",
    "black==22.*,>=22.1.0",
    "preggy==1.*,>=1.4.4",
    "pyssim==0.*,>=0.4",
    "pytest==7.*,>=7.0.0",
    "pytest-cov==3.*,>=3.0.0",
    "pytest-asyncio==0.*,>=0.18.0",
]

RUNTIME_REQUIREMENTS = [
    "opencv-python-headless==4.*,>=4.2.0",
    "Pillow>=9.0.0",
    "pyres==1.*,>=1.5.0",
    "sentry-sdk==0.*,>=0.14.2",
]

setup(
    long_description=readme,
    name="remotecv",
    version="3.1.0",
    description="remotecv is an OpenCV worker for facial and feature recognition",
    python_requires="==3.*,>=3.7.0",
    author="Bernardo Heynemann",
    author_email="heynemann@gmail.com",
    license="MIT",
    entry_points={"console_scripts": ["remotecv = remotecv.worker:main"]},
    packages=[
        "remotecv",
        "remotecv.detectors",
        "remotecv.detectors.complete_detector",
        "remotecv.detectors.face_detector",
        "remotecv.detectors.feature_detector",
        "remotecv.detectors.glasses_detector",
        "remotecv.detectors.profile_detector",
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
