<?php

namespace StrontiumCorp\PackageTemplate\Support;

/**
 * Deep-merges the package's default config under the app's published config.
 *
 * Laravel's mergeConfigFrom() only merges top-level keys, so an app that
 * published the config before a nested key existed would silently lose it.
 * Here associative arrays merge key by key, while lists are taken from the
 * app as a whole so they can be narrowed or emptied.
 */
final class ConfigMerge
{
    /**
     * @param  array<array-key, mixed>  $defaults
     * @param  array<array-key, mixed>  $app
     * @return array<array-key, mixed>
     */
    public static function merge(array $defaults, array $app): array
    {
        foreach ($app as $key => $value) {
            $default = $defaults[$key] ?? null;

            $defaults[$key] = is_array($value) && is_array($default) && ! array_is_list($value) && ! array_is_list($default)
                ? self::merge($default, $value)
                : $value;
        }

        return $defaults;
    }
}
