#!/usr/bin/env python3

# Copyright (C) 2020 The btclib developers
#
# This file is part of btclib. It is subject to the license terms in the
# LICENSE file found in the top-level directory of this distribution.
#
# No part of btclib including this file, may be copied, modified, propagated,
# or distributed except according to the terms contained in the LICENSE file.

from typing import Optional, Tuple

from . import bip32
from .alias import BIP32Key, PrvKey, String
from .base58 import b58decode
from .curve import Curve
from .curves import secp256k1
from .network import (
    NETWORKS,
    network_from_key_value,
    network_from_xkeyversion,
    xprvversions_from_network,
)
from .utils import bytes_from_octets


def int_from_prvkey(prvkey: PrvKey, ec: Curve = secp256k1) -> int:
    """Return a verified-as-valid private key integer.

    It supports:

    - WIF (bytes or string)
    - BIP32 extended keys (bytes, string, or BIP32KeyDict)
    - SEC Octets (bytes or hex-string, with 02, 03, or 04 prefix)
    - integer (native int or hex-strin)

    Network and compressed informations from the input key
    are not used.
    """

    if isinstance(prvkey, int):
        q = prvkey
    elif isinstance(prvkey, dict):
        q, network, _ = _prvkeyinfo_from_xprvwif(prvkey)
        # q has been validated on the xprv/wif network
        ec2 = NETWORKS[network]["curve"]
        assert ec == ec2, f"ec / network ({network}) mismatch"
        return q
    else:
        try:
            q, network, _ = _prvkeyinfo_from_xprvwif(prvkey)
        except Exception:
            pass
        else:
            # q has been validated on the xprv/wif network
            ec2 = NETWORKS[network]["curve"]
            assert ec == ec2, f"ec / network ({network}) mismatch"
            return q

        prvkey = bytes_from_octets(prvkey, ec.nsize)
        q = int.from_bytes(prvkey, "big")

    if not 0 < q < ec.n:
        raise ValueError(f"Private key {hex(q).upper()} not in [1, n-1]")

    return q


PrvKeyInfo = Tuple[int, str, bool]


def _prvkeyinfo_from_wif(
    wif: String, network: Optional[str] = None, compressed: Optional[bool] = None
) -> PrvKeyInfo:
    """Return private key tuple(int, compressed, network) from a WIF.

    WIF is always compressed and includes network information:
    here the 'network, compressed' input parameters are passed
    only to allow consistency checks.
    """

    if isinstance(wif, str):
        wif = wif.strip()

    payload = b58decode(wif)

    network = network_from_key_value("wif", payload[0:1])
    ec = NETWORKS[network]["curve"]

    if len(payload) == ec.nsize + 2:  # compressed WIF
        compr = True
        if payload[-1] != 0x01:  # must have a trailing 0x01
            raise ValueError("Not a compressed WIF: missing trailing 0x01")
        prvkey = payload[1:-1]
    elif len(payload) == ec.nsize + 1:  # uncompressed WIF
        compr = False
        prvkey = payload[1:]
    else:
        raise ValueError(f"Wrong WIF size ({len(payload)})")

    if compressed is not None and compr != compressed:
        raise ValueError("Compression requirement mismatch")

    q = int.from_bytes(prvkey, byteorder="big")
    if not 0 < q < ec.n:
        raise ValueError(f"Private key {hex(q)} not in [1, n-1]")

    return q, network, compr


def _prvkeyinfo_from_xprv(
    xprv: BIP32Key, network: Optional[str] = None, compressed: Optional[bool] = None
) -> PrvKeyInfo:
    """Return prvkey tuple (int, compressed, network) from BIP32 xprv.

    BIP32Key is always compressed and includes network information:
    here the 'network, compressed' input parameters are passed
    only to allow consistency checks.
    """

    compressed = True if compressed is None else compressed
    if not compressed:
        raise ValueError("Uncompressed SEC / compressed BIP32 mismatch")

    if not isinstance(xprv, dict):
        xprv = bip32.deserialize(xprv)
    if xprv["key"][0] != 0:
        m = f"Not a private key: {bip32.serialize(xprv).decode()}"
        raise ValueError(m)

    q = int.from_bytes(xprv["key"][1:], byteorder="big")

    if network is not None:
        allowed_versions = xprvversions_from_network(network)
        if xprv["version"] not in allowed_versions:
            m = f"Not a key for ({network}): "
            m += f"{bip32.serialize(xprv).decode()}"
            raise ValueError(m)
        return q, network, True
    else:
        return q, network_from_xkeyversion(xprv["version"]), True


def _prvkeyinfo_from_xprvwif(
    xprvwif: BIP32Key, network: Optional[str] = None, compressed: Optional[bool] = None
) -> PrvKeyInfo:
    """Return prvkey tuple (int, compressed, network) from WIF/BIP32.

    Support WIF or BIP32 xprv.
    """

    if not isinstance(xprvwif, dict):
        try:
            return _prvkeyinfo_from_wif(xprvwif, network, compressed)
        except Exception:
            pass

    return _prvkeyinfo_from_xprv(xprvwif, network, compressed)


def prvkeyinfo_from_prvkey(
    prvkey: PrvKey, network: Optional[str] = None, compressed: Optional[bool] = None
) -> PrvKeyInfo:

    compr = True if compressed is None else compressed
    net = "mainnet" if network is None else network
    ec = NETWORKS[net]["curve"]

    if isinstance(prvkey, int):
        q = prvkey
    elif isinstance(prvkey, dict):
        return _prvkeyinfo_from_xprv(prvkey, network, compressed)
    else:
        try:
            return _prvkeyinfo_from_xprvwif(prvkey, network, compressed)
        except Exception:
            pass

        # it must octets
        prvkey = bytes_from_octets(prvkey, ec.nsize)
        q = int.from_bytes(prvkey, "big")

    if not 0 < q < ec.n:
        raise ValueError(f"Private key {hex(q).upper()} not in [1, n-1]")

    return q, net, compr
