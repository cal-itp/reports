import Alpine from 'alpinejs';

import filters from './monthFilters';
Alpine.data('filters', filters);

window.Alpine = Alpine;
Alpine.start();
