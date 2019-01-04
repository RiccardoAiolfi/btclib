# btclib: a bitcoin cryptography library

[![Build Status](https://travis-ci.org/dginst/BitcoinBlockchainTechnology.svg)](https://travis-ci.org/dginst/BitcoinBlockchainTechnology)
[![Coverage Status](https://coveralls.io/repos/github/dginst/BitcoinBlockchainTechnology/badge.svg)](https://coveralls.io/github/dginst/BitcoinBlockchainTechnology)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/btclib.svg)](https://pypi.python.org/pypi/btclib/)
[![PyPI version fury.io](https://badge.fury.io/py/btclib.svg)](https://pypi.python.org/pypi/btclib/)
[![Documentation Status](https://readthedocs.org/projects/btclib/badge/?version=latest)](https://btclib.readthedocs.io/)

btclib is a python library intended for teaching and demonstration of the cryptography used in bitcoin.

To install (and upgrade) `btclib`:

```shell
python3 -m pip install --upgrade btclib
```

Algorithms are not to be used in production environments: they could be broken using side-channel attacks. Moreover, they will probably have major refactorings without care for backward compatibility.
