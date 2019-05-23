# Easy install

ZerOBNL is a Python package so you need [Python 3.X](https://www.python.org/downloads/).

TODO: Docker support install windows ...

## Linux ([Windows version below](#Windows))

Install Docker and Docker-Compose (More on [docker installation](https://docs.docker.com/install/linux/docker-ce/ubuntu/))

```
$ sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose
```

Manage Docker as a non-root user ([Docker - post installation steps](https://docs.docker.com/install/linux/linux-postinstall/))

```
$ sudo groupadd docker
$ sudo usermod -aG docker $USER
```

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

Install zerobnl (in the zerobnl folder) as an editable project in current directory

```
(zero)$ pip install -e .
```

Install [Jupyter Notebook](http://jupyter.org/) (recommended)
```
(zero)$ pip install jupyter
```

### Jupyter with VirtualEnv

- https://stackoverflow.com/questions/37891550/jupyter-notebook-running-kernel-in-different-env
- https://anbasile.github.io/programming/2017/06/25/jupyter-venv/

#### Define default Jupyter kernel:

```bash
source venv/bin/activate
(venv) python -m ipykernel install --user
(venv) jupyter notebook
```

#### Or create a new one:

```bash
source venv/bin/activate
(venv) ipython kernel install --user --name=projectname
(venv) jupyter notebook
```

## <a name="Windows"></a> Windows

Use [Git for Windows](https://git-scm.com/download/win) to clone the [zerobnl repository](https://github.com/IntegrCiTy/zerobnl).
For instance, when using *Git Bash* type the following on the command line:
```
$ git clone https://github.com/IntegrCiTy/zerobnl
```

Use *pip* in the Windows command line to install [virtualenv](https://virtualenv.pypa.io/en/stable/) and [virtualenvwrapper-win](https://pypi.python.org/pypi/virtualenvwrapper-win):
```
$ pip install virtualenv
$ pip install virtualenvwrapper-win
```

Use *mkvirtualenv* in the Windows command line to create and start a Python (3.X) virtual environment called *zero* and acivate it:
```
$ mkvirtualenv -p C:\path\to\python35.exe zero
```

*Optional*: In the virtual environment, set the working directory to the *zerobnl* root directory:
```
(zero)$ setprojectdir C:\path\to\zerobnl
```

In the virtual environment, install dependencies (in the zerobnl folder):
```
(zero)$ pip install -r requirements.txt
```

Install zerobnl (in the zerobnl folder) using the `install` command

```
(zero)$ python setup.py install
```

Install [Jupyter Notebook](http://jupyter.org/) (recommended)
```
(zero)$ pip install jupyter
```

[HOME](./index.md)
