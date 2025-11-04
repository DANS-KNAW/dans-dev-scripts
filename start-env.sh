#!/usr/bin/env bash
#
# Copyright (C) 2021 DANS - Data Archiving and Networked Services (info@dans.knaw.nl)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

ETCDIR=etc
DATADIR=data
INIT_DEBUG_ENV_SCRIPT=./debug-init-env.sh

echo -n "(Re-)creating $ETCDIR..."
rm -fr $ETCDIR
cp -r src/test/resources/debug-etc $ETCDIR
echo "OK"

if [ -e $DATADIR ]; then
    DATADIR_BACKUP=$DATADIR-$(date  +"%Y-%m-%d@%H:%M:%S")
    echo -n "Backing up existing data directory to $DATADIR_BACKUP..."
    mv $DATADIR $DATADIR_BACKUP
    echo "OK"
fi

mkdir $DATADIR

if [ -f $INIT_DEBUG_ENV_SCRIPT ]; then
    echo "START: project specific initialization in $INIT_DEBUG_ENV_SCRIPT..."
    # shellcheck disable=SC1090
    source $INIT_DEBUG_ENV_SCRIPT
    echo "DONE: project specific initialization."
    echo
fi

echo "The debug environment has been reinitialized."

echo "Config directory at: $ETCDIR"
echo "Data and logging directory at: $DATADIR"
