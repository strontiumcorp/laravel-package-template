<?php

use StrontiumCorp\PackageTemplate\Support\ConfigMerge;

it('deep-merges nested settings but replaces lists wholesale', function () {
    $defaults = ['a' => ['x' => 1, 'y' => 2], 'list' => ['one', 'two', 'three'], 'scalar' => true];
    $app = ['a' => ['x' => 9], 'list' => ['mine'], 'extra' => 'kept'];

    expect(ConfigMerge::merge($defaults, $app))->toBe([
        'a' => ['x' => 9, 'y' => 2],
        'list' => ['mine'],          // not ['mine', 'two', 'three']
        'scalar' => true,
        'extra' => 'kept',
    ]);
});

it('lets an app explicitly empty a list or null a value', function () {
    expect(ConfigMerge::merge(['list' => ['a'], 'v' => 'x'], ['list' => [], 'v' => null]))
        ->toBe(['list' => [], 'v' => null]);
});
