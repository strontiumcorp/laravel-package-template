// An example component: plain React, no Inertia, so it works in any app.
// Replace it with the package's own components (or run `make remove-ui`).

export type StatusBadgeProps = {
    enabled: boolean;
    label?: string;
    className?: string;
};

export default function StatusBadge({ enabled, label = 'Package', className = '' }: StatusBadgeProps) {
    return (
        <span role="status" data-enabled={enabled} className={`inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs ${className}`.trim()}>
            {label}: {enabled ? 'on' : 'off'}
        </span>
    );
}
