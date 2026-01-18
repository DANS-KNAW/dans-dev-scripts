dans-dev-scripts
================

A collection of scripts to help with the development of DANS software.

Installation
------------

To install the development scripts, clone this repository and add the checkout directory to your PATH environment variable. For example:

```bash
git clone https://github.com/DANS-KNAW/dans-dev-scripts.git
export PATH="$PATH:/path/to/dans-dev-scripts"
```

### Locally testing microservices and command-line tools

Most of the scripts in this project are intended to be used from the checkout directory of a DANS microservice or command-line tool.

The `start-env.sh` script will create a `data` and `etc` directory in the checkout directory. It also copies configuration files to `etc` and, for some
projects, also copies test data to `data`. These directories are ignored by Git, so you can safely modify their content. Together they form a local development
environment needed to run the other `start-*.sh` scripts.

`start.sh` is a generic wrapper around the Maven `exec:java` goal; it can be used for CLI modules. `start-service.sh` starts a microservice. There are also
`*-debug.sh` versions of these scripts which start Java with a debug port enabled.
