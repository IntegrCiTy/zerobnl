# FAQ

### Why is ZerOBNL developed in Python?

The main developer worships Guido van Rossum.

### Is there any alternative to ZerOBNL?

 - [Mosaik](https://mosaik.offis.de/)
 - [OpenBuildNet](https://sites.google.com/site/buildnetproject/software)
 - [FUMOLA](http://fumola.sourceforge.net)
 - [Building Controls Virtual Test Bed](https://simulationresearch.lbl.gov/bcvtb/FrontPage)
 - and many more ...

### What does ZerOBNL stand for?

We developed ZerOBNL to simplify and combine the strengths of [Mosaik](https://mosaik.offis.de/) and [OpenBuildNet](https://sites.google.com/site/buildnetproject/software). 
We even started our development process by creating a "light" Python version of the latter, called *OpenBuildNet Light* (OBNL), and which was later renamed to [OBvious Node Link](https://github.com/IntegrCiTy/obnl) (for obvious IP reasons).

The OBNL tool was using [Rabbit MQ](https://www.rabbitmq.com/) as message broker. 
During a complete re-factoring and simplification of the code we switched to [ZeroMQ](http://zguide.zeromq.org/) and decided to change the name to ZerOBNL.


[Home](./index.md)