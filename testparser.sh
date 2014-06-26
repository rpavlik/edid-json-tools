#!/bin/bash

# Copyright (c) 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


for i in $(ls edids); do
    if [[ $i != *.txt && ! -d $i ]]; then
        ./edidparser parse -v edids/$i #> edids/extEdids/$i.txt
        printf "\n\n\n\n\n"
    fi
done
