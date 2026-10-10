import { render, screen } from '@testing-library/react';
import StatusBadge from '@/components/vendor/laravel-package-template/status-badge';

describe('StatusBadge', () => {
    it('says whether the package is on', () => {
        render(<StatusBadge enabled label="Example" />);

        expect(screen.getByRole('status')).toHaveTextContent('Example: on');
    });

    it('says when it is off', () => {
        render(<StatusBadge enabled={false} />);

        expect(screen.getByRole('status')).toHaveTextContent('Package: off');
    });
});
