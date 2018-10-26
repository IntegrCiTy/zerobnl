# FAQ

- Why ZerOBNL is developed in Python ?

The main developer worships Guido van Rossum.

- Is there any alternative to ZerOBNL ? 

	- [Mosaik](https://mosaik.offis.de/)
	- [OpenBuildNet](https://sites.google.com/site/buildnetproject/software)
	- [Building Controls Virtual Test Bed](https://simulationresearch.lbl.gov/bcvtb/FrontPage) 

- What does ZerOBNL stand for ?

We tried to build ZerOBNL to simplify and combine the strengths of Mosaik and OpenBuildNet. We even started our development process by creating a "light" Python version of the last one called OpenBuildNet Light (OBNL) that we renamed OBvious Node Link for obvious IP reasons. Our tool was using [Rabbit MQ](https://www.rabbitmq.com/) as message broker. During a complete re-factoring and simplification of the code we switched to [ZeroMQ](http://zguide.zeromq.org/) and decided to change the name to ZerOBNL.

[Home](./index.md)