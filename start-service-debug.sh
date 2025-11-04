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

print_usage() {
  echo "start-service-debug.sh [--suspend]"
  echo "Start a DANS module as a micro-service."
  echo
  echo "--suspend suspend execution at the start of the program"
  exit
}

[[ $1 == "--help" ]] && print_usage
[[ $1 == --suspend ]]  && SUSPEND=y || SUSPEND=n
set -x
MAVEN_OPTS="-agentlib:jdwp=transport=dt_socket,server=y,address=8000,suspend=$SUSPEND" \
start.sh server etc/config.yml
