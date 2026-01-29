document.addEventListener('DOMContentLoaded', function() {
    // Check if html2pdf is available
    if (typeof html2pdf === 'undefined') {
        console.warn('html2pdf.js not loaded');
    }
});

function exportPDF() {
    const element = document.getElementById('certificate-content');
    const btnContainer = document.querySelector('.no-print'); // The button container
    
    // Hide button temporarily if it's inside the element (it shouldn't be if we target card-body but let's be safe)
    if(btnContainer) btnContainer.style.display = 'none';

    const opt = {
        margin:       10,
        filename:     'MindGuard_Certificate.pdf',
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'landscape' }
    };

    if (typeof html2pdf !== 'undefined') {
        html2pdf().set(opt).from(element).save().then(function(){
            if(btnContainer) btnContainer.style.display = 'block';
        });
    } else {
        alert('Đang tải thư viện tạo PDF. Vui lòng thử lại sau giây lát.');
        if(btnContainer) btnContainer.style.display = 'block';
    }
}
