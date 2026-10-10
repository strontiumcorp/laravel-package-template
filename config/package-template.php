<?php

// Defaults for strontiumcorp/laravel-package-template. Apps publish this file
// with `php artisan vendor:publish --tag=package-template-config`; their copy
// is deep-merged over these defaults (Support\ConfigMerge), so every new key
// needs its default here. Don't add config('…', fallback) defaults in code,
// and never put closures here (they break `config:cache`).

return [

    /*
    | Turn the package off without uninstalling it.
    */
    'enabled' => env('PACKAGE_TEMPLATE_ENABLED', true),

    /*
    | The package's routes (routes/package-template.php). Read while the
    | providers boot, so tests change them with rebootWith().
    */
    'routes' => [
        'enabled' => true,
        'prefix' => 'package-template',
        'middleware' => ['web'],
    ],

];
