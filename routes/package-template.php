<?php

use Illuminate\Support\Facades\Route;

// Loaded by PackageTemplateServiceProvider when `package-template.routes.enabled`
// is on. Delete this file if the package has no routes.

Route::middleware(config('package-template.routes.middleware'))
    ->prefix(config('package-template.routes.prefix'))
    ->as('package-template.')
    ->group(function () {
        Route::get('ping', fn () => response()->json(['ok' => true]))->name('ping');
    });
