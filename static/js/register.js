document.addEventListener('DOMContentLoaded', function() {
    const cccdInput = document.getElementById('cccdInput');
    const dobInput = document.getElementById('dobInput');
    const cccdHint = document.getElementById('cccdHint');
    
    if (cccdInput) {
        cccdInput.addEventListener('input', autoFillFromCCCD);
    }
    
    function autoFillFromCCCD() {
        if (!cccdInput) return;
        
        const cccd = cccdInput.value;
        if (cccd.length === 12) {
            // Simple logic for Vietnam CCCD
            // 4th digit: Gender/Century (0,2,4... Male; 1,3,5... Female)
            // 0: 1900, 1: 1900
            // 2: 2000, 3: 2000
            
            // 0,1 -> 19xx
            // 2,3 -> 20xx
            // 4,5 -> 21xx
            // 6,7 -> 22xx
            // 8,9 -> 23xx
            
            const genderCentury = parseInt(cccd[3]);
            if (isNaN(genderCentury)) return;
            
            const yearSuffix = cccd.substring(4, 6);
            let yearPrefix = '19';
            
            if (genderCentury === 2 || genderCentury === 3) yearPrefix = '20';
            if (genderCentury === 4 || genderCentury === 5) yearPrefix = '21';
            if (genderCentury === 6 || genderCentury === 7) yearPrefix = '22';
            if (genderCentury === 8 || genderCentury === 9) yearPrefix = '23';
            
            const fullYear = yearPrefix + yearSuffix;
            
            // CCCD does not encode month/day, so we default to 01-01 or leave it for user to pick
            // But user asked to "auto input". Let's set Year and let user pick date.
            
            if (dobInput) {
                // If user hasn't set value yet or we want to overwrite
                 // alert(`Đã nhận diện năm sinh từ CCCD: ${fullYear}. Vui lòng bổ sung ngày tháng.`);
                 // Using a more subtle UI hint instead of alert is better UX
                 if (cccdHint) {
                    cccdHint.textContent = `Đã nhận diện năm sinh: ${fullYear}. Vui lòng bổ sung ngày tháng.`;
                    cccdHint.classList.add('text-success');
                    cccdHint.classList.remove('text-muted');
                 }
                 
                 // format YYYY-MM-DD
                 dobInput.value = `${fullYear}-01-01`; 
            }
        }
    }
});
