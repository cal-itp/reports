import bb, { bar, area, line } from 'billboard.js';

const twoDecimals = new Intl.NumberFormat('default', { maximumFractionDigits: 2});

// HOURS CHARTS
// *****************************************************************************

const hoursCharts = document.querySelectorAll('.hours-chart');

hoursCharts.forEach((chartEl) => {
    const dates = JSON.parse(chartEl.dataset.dates);
    const hours = JSON.parse(chartEl.dataset.hours);
    const chartType = chartEl.dataset.chartType || 'line'; // Get chart type from dataset, default to 'line'
    const color = chartEl.dataset.color;
    const colLabel = chartEl.dataset.chartCollabel || 'hours';

    const chart = bb.generate({
        bindto: chartEl,
        color: {
            pattern: [color]
        },
        data: {
            x: "Date",
            xFormat: "%Q",
            columns: [
                ["Date"].concat(dates),
                [colLabel].concat(hours),
            ],
            types: {
                [colLabel]: chartType === 'area' ? area() : line()
            }
        },
        area: {
            linearGradient: true,
        },
        axis: {
            x: {
                label: {
                    position: "outer-center",
                    text: "Service date"
                },
                localtime: false,
                tick: {
                    fit: false,
                    format: "%-m/%-d",
                    outer: false,
                    rotate: -30,
                },
                type: "timeseries",
            },
            y: {
                label: {
                    position: "outer-middle",
                    text: chartEl.dataset.yAxisLabel || "Total service hours" // Default to "Total service hours" if not provided
                },
                tick: {
                    culling: {
                        max: 6,
                    },
                    outer: false,
                },
            },
        },
        legend: {
            show: false
        },
        tooltip: {
            format: {
                title: (x) => Intl.DateTimeFormat('default', {
                    weekday: 'short',
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric',
                    timeZone: 'UTC',
                }).format(x),
                // Get the tooltip value label from the chart element's dataset
                value: (x) => `${twoDecimals.format(x)} ${chartEl.dataset.tooltipValueLabel || 'hours'}` 
            },
        },

        onafterinit: function () {
            const { circles } = this.$;

            circles.each(function (circle, i) {
                const labelDate = circle.x.toLocaleString('en-US', {
                    month: "short",
                    day: "numeric",
                });
                const labelValue = `${twoDecimals.format(circle.value)} hours`;
                this.setAttribute('tabindex', 0);
                this.setAttribute('aria-label', `${labelDate}: ${labelValue}`);
            });
        }
    })
});

// CHANGES CHART
// *****************************************************************************

const changesChartEl = document.getElementById('changes-chart');
const changesData = changesChartEl.dataset;
const addedColumn = ['Added', changesData.routesAdded, changesData.stopsAdded];
const removedColumn = ['Removed', changesData.routesRemoved, changesData.stopsRemoved];
const unchangedColumn = ['Unchanged', changesData.routesUnchanged, changesData.stopsUnchanged];
const percentWithDecimal = new Intl.NumberFormat('default', {
    style: 'percent',
    maximumFractionDigits: 2,
});

const changesChart = bb.generate({
    bindto: changesChartEl,
    padding: {
        bottom: 48,
    },
    data: {
        type: bar(),
        columns: [
            addedColumn,
            removedColumn,
            unchangedColumn,
        ],
        groups: [
            [
                'Added',
                'Removed',
                'Unchanged',
            ]
        ],
        colors: {
            Added: '#51BF9D',
            Removed: '#E16B26',
            Unchanged: '#DEE1E6',
        },
    },
    axis: {
        rotated: true,
        x: {
            categories: [
                'Routes',
                'Stops',
            ],
            padding: 0,
            tick: {
                outer: false,
                show: false,
            },
            type: 'category',
        },
        y: {
            label: {
                position: 'outer-center',
                text: 'Percentage of IDs',
            },
            padding: { bottom: 0, top: 16 },
            tick: {
                format: (x) => Intl.NumberFormat('default', { style: 'percent' }).format(x),
                outer: false,
                values: [
                    0, .2, .4, .6, .8, 1
                ]
            }
        }
    },
    legend: {
        item: {
            tile: {
                type: 'circle',
            },
        },
        padding: 16,
    },
    tooltip: {
        format: {
            value: (x) => percentWithDecimal.format(x)
        },
        order: '',
    },
    interaction: {
        enabled: false,
    },
    onafterinit: function() {
        const { bars } = this.$.bar;
        const categories = this.categories();

        bars.each(function(bar) {
            const label = `${percentWithDecimal.format(bar.value)} of ${categories[bar.x]} were ${bar.id}`;
            this.setAttribute('aria-label', label);
            this.setAttribute("tabindex", 0);
        });
    },
});
