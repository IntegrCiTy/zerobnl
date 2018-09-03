# zerobnl

Distributed co-simulation tool based on ZeroMQ, Docker (Swarm and Compose) developped in Python.

## Getting Started

### Installing

#### Linux

Install git (if not already done) (More info on [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git))

If you’re on a Debian-based distribution like Ubuntu, try apt-get:

```
$ sudo apt-get install git-all
```

Install virtualenv (if not already done) (More info on [virtualenv](https://virtualenv.pypa.io/en/stable/installation/))

```
$ pip install virtualenv
```

Create a Python (3.X) virtual env

```
$ virtualenv -p python3 zero
```

Activate the created virtual env (zero)

```
$ source link/to/ict/bin/activate
```

Download source code

```
(zero)$ git clone https://github.com/IntegrCiTy/zerobnl.git
```

Install dependencies (in the zerobnl folder)

```
(zero)$ pip install -r requirements.txt
```

Install zerobnl (in the zerobnl folder) using the `develop` command

```
(zero)$ python setup.py develop
```

A full scale demo with real data and complex models is available [here](https://github.com/IntegrCiTy/zerobnl-examples).

#### Windows

Use [Git for Windows](https://git-scm.com/download/win) to clone the [zerobnl repository](https://github.com/IntegrCiTy/zerobnl).
For instance, when using *Git Bash* type the following on the command line:
```
$ git clone https://github.com/IntegrCiTy/zerobnl
```

Use *pip* in the Windows command line to install [virtualenv](https://virtualenv.pypa.io/en/stable/) and [virtualenvwrapper-win](https://pypi.python.org/pypi/virtualenvwrapper-win):
```
> pip install virtualenv
> pip install virtualenvwrapper-win
```

Use *mkvirtualenv* in the Windows command line to create and start a Python (3.X) virtual environment called *zero*:
```
> mkvirtualenv -p C:\path\to\python35.exe zero
```

*Optional*: In the virtual environment, set the working directory to the *zerobnl* root directory:
```
(zero) setprojectdir C:\path\to\zerobnl
```

In the virtual environment, install dependencies:
```
(zero) pip install -r requirements.txt
```

Install zerobnl (in the zerobnl folder) using the `develop` command

```
(zero) python setup.py develop
```

A full scale demo with real data and complex models is available [here](https://github.com/IntegrCiTy/zerobnl-examples).

## Running the tests

Pytest (https://docs.pytest.org/en/latest/) is used in this project.
To run tests just run `pytest` from a terminal in the dedicated environment inside the root folder of this package.

## Authors

* **Pablo Puerto** - *Initial work*

## License

You should have received a copy of the Apache License Version 2.0 along with this program.
If not, see http://www.apache.org/licenses/LICENSE-2.0.

## Acknowledgments

* TO DO ...

