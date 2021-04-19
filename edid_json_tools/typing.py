# Copyright (c) 2019-2021 The EDID JSON Tools authors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

# TODO when we can say "python 3.8 required" we can use this
# from typing import Literal
# EdidVersion = Literal['1.3', '1.4']

from typing import Dict, List


EdidVersion = str

ByteList = List[int]
# OverscanBehavior = NewType('OverscanBehavior', str)
OverscanBehavior = str
BoolDict = Dict[str, bool]
