document.addEventListener('DOMContentLoaded', function () {
    // Only initialize charts if the canvas elements exist & data is available
    if (document.getElementById('trendChart') && typeof Chart !== 'undefined') {
        // Data should be passed via data attributes on the canvas or a global variable
        // However, since the current template uses Jinja2 variable injection inside script tags, 
        // we need to access those values. 
        // Best practice: Attach data to the DOM element data-attributes.
        
        const trendCanvas = document.getElementById('trendChart');
        if (trendCanvas.dataset.datesLabels && trendCanvas.dataset.datesData) {
            const dateLabels = JSON.parse(trendCanvas.dataset.datesLabels);
            const dateData = JSON.parse(trendCanvas.dataset.datesData);

            const trendCtx = trendCanvas.getContext('2d');
            new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: dateLabels,
                    datasets: [{
                        label: 'Số lượng tố cáo',
                        data: dateData,
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#fff',
                        pointBorderColor: '#0d6efd',
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, ticks: { stepSize: 1 } },
                        x: { grid: { display: false } }
                    }
                }
            });
        }
    }

    if (document.getElementById('typeChart') && typeof Chart !== 'undefined') {
        const typeCanvas = document.getElementById('typeChart');
        if (typeCanvas.dataset.typesLabels && typeCanvas.dataset.typesData) {
            const typeLabels = JSON.parse(typeCanvas.dataset.typesLabels);
            const typeData = JSON.parse(typeCanvas.dataset.typesData);

            const typeCtx = typeCanvas.getContext('2d');
            new Chart(typeCtx, {
                type: 'doughnut',
                data: {
                    labels: typeLabels,
                    datasets: [{
                        data: typeData,
                        backgroundColor: ['#0d6efd', '#dc3545', '#198754', '#ffc107', '#0dcaf0', '#6610f2'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { boxWidth: 12, usePointStyle: true } }
                    },
                    cutout: '70%'
                }
            });
        }
    }
});
