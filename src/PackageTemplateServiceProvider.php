<?php

namespace StrontiumCorp\PackageTemplate;

use Illuminate\Contracts\Foundation\CachesConfiguration;
use Illuminate\Foundation\Console\AboutCommand;
use Illuminate\Support\ServiceProvider;
use StrontiumCorp\PackageTemplate\Support\ConfigMerge;

class PackageTemplateServiceProvider extends ServiceProvider
{
    private const CONFIG = __DIR__.'/../config/package-template.php';

    private const ROUTES = __DIR__.'/../routes/package-template.php';

    private const MIGRATIONS = __DIR__.'/../database/migrations';

    public function register(): void
    {
        $this->mergeConfig();

        // Singletons must hold no per-request state (Octane): resolve the
        // request and auth from the live container, never from one captured
        // at boot.
    }

    /**
     * Deep merge (see ConfigMerge) instead of mergeConfigFrom(), so apps with
     * an older published config still get newly added nested keys.
     */
    private function mergeConfig(): void
    {
        if ($this->app instanceof CachesConfiguration && $this->app->configurationIsCached()) {
            return; // `config:cache` already stored the merged result.
        }

        $config = $this->app->make('config');
        $config->set('package-template', ConfigMerge::merge(require self::CONFIG, (array) $config->get('package-template', [])));
    }

    public function boot(): void
    {
        $this->registerPublishing();
        $this->registerMigrations();
        $this->registerRoutes();
        $this->registerAbout();
    }

    private function registerPublishing(): void
    {
        $this->publishes([self::CONFIG => config_path('package-template.php')], 'package-template-config');
    }

    /** Publishes and runs the package's migrations, once it has some (database/migrations). */
    private function registerMigrations(): void
    {
        if (is_dir(self::MIGRATIONS)) {
            $this->publishes([self::MIGRATIONS => database_path('migrations')], 'package-template-migrations');
            $this->loadMigrationsFrom(self::MIGRATIONS);
        }
    }

    /** Loads routes/package-template.php, if it exists and routes are on. */
    private function registerRoutes(): void
    {
        if (config('package-template.enabled')
            && config('package-template.routes.enabled')
            && is_file(self::ROUTES)
            && ! $this->app->routesAreCached()) {
            $this->loadRoutesFrom(self::ROUTES);
        }
    }

    /** A section in `php artisan about`. */
    private function registerAbout(): void
    {
        AboutCommand::add('Package Template', fn () => [
            'Enabled' => config('package-template.enabled') ? '<fg=green;options=bold>YES</>' : '<fg=yellow;options=bold>NO</>',
            'Routes' => config('package-template.routes.enabled') ? '/'.trim((string) config('package-template.routes.prefix'), '/') : 'off',
        ]);
    }
}
