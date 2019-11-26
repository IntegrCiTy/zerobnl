# Installation Instructions

## Prerequisites

ZerOBNL requires the following software to be installed on your system (follow the links for instructions):

 * [Python 3](https://wiki.python.org/moin/BeginnersGuide/Download) (including the Python package manager [pip](https://pip.pypa.io/en/stable/))
   * **Linux**: install via the native package management system
 (e.g., *apt-get install python3 python3-pip*)
   * **Windows**: download and install from the [Python homepage](https://www.python.org/download)
 * [Docker Engine - Community](https://docs.docker.com/install/#supported-platforms)
 * [Docker Compose](https://docs.docker.com/compose/install/)
 * [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)


## Installation on Linux ([Instructions for Windows below](#Windows))

It is recommended to install ZerOBNL in an isolated Python environment.
This can be done with the help of the [virtualenv package](https://virtualenv.pypa.io/en/stable/), which can be installed with the help of *pip* from the command line:
```bash
$ pip3 install virtualenv
```

Create a Python virtual environment called *zero*:
```bash
$ virtualenv -p python3 zero
```

Activate the virtual environment:
```bash
$ source zero/bin/activate
```

Download the ZerOBNL source code:
```bash
(zero)$ git clone https://github.com/IntegrCiTy/zerobnl.git
```

Install ZerOBNL as an editable project from its root directory:
```bash
(zero)$ cd zerobnl
(zero)$ pip install -e .
```

To run the examples, also install [Jupyter Notebook](http://jupyter.org/):
```bash
(zero)$ pip install jupyter
```

### Troubleshooting

In case the Jupyter notebooks do not work properly within the virtual environment, try one of the following:
* https://stackoverflow.com/questions/37891550/jupyter-notebook-running-kernel-in-different-env
* https://anbasile.github.io/programming/2017/06/25/jupyter-venv/

### Verified Linux Setups

ZerOBNL has been successfully installed on the following Linux setups:

**Ubuntu** (recommended Linux setup):
 * Ubuntu 18.04.3 LTS (bionic, GNU/Linux 4.15.0-70-generic x86_64)
 * Docker Engine Community 19.03.5
 * Docker Compose 1.24.1
 * Python 3.6.8

**Debian**:
 * Debian 4.9.0-8-amd64 
 * Docker Engine Community 18.09.6
 * Docker Compose 1.24.1
 * Python 3.5.3


## <a name="Windows"></a> Installation on Windows

Use [Git for Windows](https://git-scm.com/download/win) to clone the [zerobnl repository](https://github.com/IntegrCiTy/zerobnl).
For instance, when using *Git Bash* type the following on the command line:
```winbatch
> git clone https://github.com/IntegrCiTy/zerobnl
```

Use *pip* in the Windows command line to install [virtualenv](https://virtualenv.pypa.io/en/stable/) and [virtualenvwrapper-win](https://pypi.python.org/pypi/virtualenvwrapper-win):
```winbatch
> pip install virtualenv
> pip install virtualenvwrapper-win
```

Use *mkvirtualenv* in the Windows command line to create and start a Python (3.X) virtual environment called *zero* and acivate it:
```winbatch
> mkvirtualenv -p C:\path\to\python.exe zero
```

*Optional*: In the virtual environment, set the working directory to the *zerobnl* root directory:
```winbatch
(zero) setprojectdir C:\path\to\zerobnl
```

Install ZerOBNL as an editable project from its root directory:
```winbatch
(zero) cd zerobnl
(zero) pip install -e .
```

To run the examples, also install [Jupyter Notebook](http://jupyter.org/):
```winbatch
(zero) pip install jupyter
```

### Troubleshooting

In case ZerOBNL does not produce any results, check file *nodes.log* for error messages like the following:
```
python: can't open file 'main.py': [Errno 2] No such file or directory
```
In this case, make sure that Docker can properly access the hard drive (see [here](https://stackoverflow.com/questions/50018812/docker-for-windows-volumes-are-empty) for instructions).

### Verified Windows Setups

ZerOBNL has been successfully installed on the following Windows setup:
 * Windows 10 (build 1607)
 * Docker Desktop for Windows 2.0.0.3
   * Docker Engine Community 18.09.02
   * Docker Compose 1.23.2
 * Python 3.6.4


[HOME](./index.md)
