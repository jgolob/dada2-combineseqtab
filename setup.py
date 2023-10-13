from setuptools import setup

setup(
    name='dada2-fast-combineseqtab',
    version='0.6.5',
    description="""Fast combination of sequence tables from DADA2
      """,
    url='',
    author='Jonathan Golob',
    author_email='j-dev@golob.org',
    license='MIT',
    packages=['dada2_combineseqtab'],
    zip_safe=False,
    install_requires=[
        'rpy2>=3.5.14',
        'numpy>=1.15.0',
        'pandas>=0.23.4',
        'scipy>=1.11.3',
        'pyreadr>=0.4.9',
    ],
    entry_points={
        'console_scripts': [
            'combine_seqtab=dada2_combineseqtab.combine_seqtab:main',
        ],
    }
)
