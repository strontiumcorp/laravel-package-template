<?php

arch('no debugging leftovers')
    ->expect(['dd', 'dump', 'ray', 'var_dump', 'print_r', 'die'])
    ->not->toBeUsed();

arch('env() is only read in config files (config:cache safe)')
    ->expect('StrontiumCorp\PackageTemplate')
    ->not->toUse('env');
