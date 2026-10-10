<?php

namespace StrontiumCorp\PackageTemplate\Tests;

use Illuminate\Contracts\Config\Repository;
use Orchestra\Testbench\TestCase as Orchestra;
use StrontiumCorp\PackageTemplate\PackageTemplateServiceProvider;
use StrontiumCorp\PackageTemplate\Tests\Fixtures\User;

/**
 * Rules for every test (see CLAUDE.md, "Testing rules"):
 *
 * - No process-global state. A parallel worker runs many test files in one
 *   PHP process, so a class declared in a test file, a class_alias() or a
 *   require'd class leaks into later files. Fixtures live under Tests\Fixtures
 *   (autoloaded); per-app state goes on the app instance.
 * - Never write into Testbench's vendor/ skeleton: parallel workers share it.
 *   Use a temp dir.
 * - Config read while the providers boot needs rebootWith([...]).
 */
abstract class TestCase extends Orchestra
{
    /**
     * Config applied before the providers boot, for settings read at boot
     * (e.g. package-template.routes.enabled). Set, then rebootWith().
     *
     * @var array<string, mixed>
     */
    public static array $bootConfig = [];

    protected function getPackageProviders($app): array
    {
        return [PackageTemplateServiceProvider::class];
    }

    protected function defineEnvironment($app): void
    {
        tap($app['config'], function (Repository $config) {
            $config->set('app.key', 'base64:'.base64_encode(str_repeat('k', 32)));
            $config->set('database.default', 'testing');
            // Testbench turns SQLite foreign keys off; production databases
            // enforce them, so cascades and constraints must be tested.
            $config->set('database.connections.testing.foreign_key_constraints', true);
            $config->set('auth.providers.users.model', User::class);
            $config->set('cache.default', 'array');
            $config->set('session.driver', 'array');
            $config->set(static::$bootConfig);
        });
    }

    protected function defineDatabaseMigrations(): void
    {
        $this->loadMigrationsFrom(__DIR__.'/Fixtures/migrations');
    }

    /** @param  array<string, mixed>  $attributes */
    protected function makeUser(array $attributes = []): User
    {
        static $n = 0;
        $n++;

        return User::create($attributes + [
            'name' => "User {$n}",
            'email' => "user{$n}@example.com",
            'password' => 'password',
        ]);
    }

    /**
     * Rebuild the app with boot-time config, with a migrated database.
     *
     * @param  array<string, mixed>  $config
     */
    protected function rebootWith(array $config): static
    {
        static::$bootConfig = $config;

        try {
            $this->refreshApplication();
        } finally {
            static::$bootConfig = [];
        }

        $this->defineDatabaseMigrations();
        $this->artisan('migrate');

        return $this;
    }
}
