# Easy install

## Linux ([Windows version](#Windows))

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

Install zerobnl (in the zerobnl folder) using the `install` command

```
(zero)$ python setup.py install
```

## <a name="Windows"></a> Windows

Use [Git for Windows](https://git-scm.com/download/win) to clone the [zerobnl repository](https://github.com/IntegrCiTy/zerobnl).
For instance, when using *Git Bash* type the following on the command line:
```
> git clone https://github.com/IntegrCiTy/zerobnl
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
(zero)> setprojectdir C:\path\to\zerobnl
```

In the virtual environment, install dependencies:
```
(zero)> pip install -r requirements.txt
```

Install zerobnl (in the zerobnl folder) using the `install` command

```
(zero)> python setup.py install
```


[HOME](./index.md)