<?php

use Illuminate\Support\Facades\DB;
use StrontiumCorp\PackageTemplate\PackageTemplateServiceProvider;

it('gives apps with an older published config the newer nested keys', function () {
    // An app published the config before routes.middleware existed.
    config(['package-template' => ['routes' => ['prefix' => 'mine']]]);

    (new PackageTemplateServiceProvider(app()))->register();

    expect(config('package-template.routes.prefix'))->toBe('mine')             // app value kept
        ->and(config('package-template.routes.middleware'))->toBe(['web'])    // new key filled in
        ->and(config('package-template.enabled'))->toBeTrue();
});

it('serves its routes under the configured prefix', function () {
    $this->getJson('/package-template/ping')->assertOk()->assertExactJson(['ok' => true]);

    $this->rebootWith(['package-template.routes.prefix' => 'elsewhere']);

    $this->getJson('/elsewhere/ping')->assertOk();
    $this->getJson('/package-template/ping')->assertNotFound();
});

it('registers no routes when they are turned off', function () {
    $this->rebootWith(['package-template.routes.enabled' => false]);

    $this->getJson('/package-template/ping')->assertNotFound();
});

it('publishes its config', function () {
    expect(PackageTemplateServiceProvider::pathsToPublish(PackageTemplateServiceProvider::class, 'package-template-config'))
        ->toHaveCount(1);
});

it('adds a section to php artisan about', function () {
    $this->artisan('about')
        ->expectsOutputToContain('Package Template')
        ->assertSuccessful();
});

it('runs SQLite with foreign keys on, like production databases', function () {
    expect(DB::selectOne('PRAGMA foreign_keys')->foreign_keys)->toBe(1);
});
