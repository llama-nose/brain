from setuptools import setup


setup(name='lln-brain',
      version='0.1',
      description='',
      author='Edwin Pan',
      author_email='edwinpan@cs.stanford.edu',
      license='',
      packages=[],
      python_requires='>=3.11',
      install_requires=[
          'boto3', 'requests', 'numpy', 'guardrails-ai', 'openai', 'scipy', 
          'scikit-learn', 'matplotlib', 'pandas'
      ])