#!/bin/bash

/bin/bash /home/schems-fun/site/mk_anvilapp_symlinks.sh

anvil-app-server \
    --app schematic_capture \
    --data-dir /home/schems-fun/anvil.data \
    --auto-migrate \
    --config-file schems_fun.anvil-config.yaml
