// this will be imported by main.js and passed into Alpine.data()
// so that it can be used in a template with `x-data="filters"`

export default () => ({
    hiddenCount: null,
    rawQuery: '',
    resultsCount: null,
    selectedVendor: null,

    // getters
    get query() {
        return this.rawQuery.trim().toLowerCase();
    },

    get hiddenCountFormatted() {
        if (this.hiddenCount) {
            return this.hiddenCount.toLocaleString();
        } else {
            return 0;
        }
    },

    get resultsCountFormatted() {
        if (this.resultsCount) {
            return this.resultsCount.toLocaleString();
        } else {
            return 0;
        }
    },

    // lifecycle
    init() {
        this.$watch('selectedVendor', () => {
            this.handleFilterChange();
        });

        this.$watch('query', () => {
            this.handleFilterChange();
        });

        this.countResults();
    },

    // methods
    checkFilters(el) {
        let shouldPass = true;

        // check query match
        if (shouldPass && this.query.length > 0) {
            const agency = el.dataset.agencyName.trim().toLowerCase();
            shouldPass = agency.includes(this.query);
        }

        // check vendor match
        if (shouldPass && this.selectedVendor) {
            const scheduleVendors = JSON.parse(el.dataset.scheduleVendors);
            const rtVendors = JSON.parse(el.dataset.rtVendors);
            const vendors = [...scheduleVendors, ...rtVendors];
            shouldPass = vendors.includes(this.selectedVendor);
        }

        return shouldPass;
    },

    clearFilters() {
        this.rawQuery = '';
        this.selectedVendor = '';
    },

    countResults() {
        this.$nextTick(() => {
            this.hiddenCount = document.querySelectorAll('#report-list li[data-report][hidden]').length;
            this.resultsCount = document.querySelectorAll('#report-list li[data-report]:not([hidden])').length;
        });
    },

    handleFilterChange() {
        this.countResults();
    },

    // bindings
    reportItem: {
        ['data-report']: '', // just add this attribute for later reference
        [':hidden']() { // hide item if it's filtered out
            return !this.checkFilters(this.$el);
        },
    }
});
