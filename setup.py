from setuptools import setup, find_namespace_packages

setup(
    name='NLL_anomaly_detection',
    packages=find_namespace_packages(include=["anomaly_detection", "anomaly_detection.*"]),
    version='0.0.1',
    description='A simple anomaly detection algorithm for medical imaging based on multi-atlas image registration and negative log likelihood.',
    author='Chenghao Liu',
    author_email='3120190681@bit.edu.cn, liuchenghao1652@gmail.com',
    install_requires=[
        'numpy==1.18.5',
        'nibabel==3.1.1',
        'scikit-image==0.18.1',
        'scipy==1.6.2'
    ],
    entry_points={
        'console_scripts':[
            'NLL_anomaly_detection = anomaly_detection.nll_analysis:main'
        ]
    },
    keywords=['image segmentation', 'lesion segmentation' , 'unsupervised learning', 
        'medical image segmentation', 'unsupervised lesion segmentation', 'anomaly detection', 'NLL', 
        'negative log likelihood']
)
