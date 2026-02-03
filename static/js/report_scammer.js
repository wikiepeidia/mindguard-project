function toggleForm(mode) {
    const formPerson = document.getElementById('form_person');
    const formWebsite = document.getElementById('form_website');
    const hiddenType = document.getElementById('hidden_report_type');

    // Lấy tất cả input của từng phần
    const inputsPerson = [
        document.getElementById('input_identifier_person'),
        document.getElementById('input_scam_type_person'),
        document.getElementById('input_scammer_name'),
        document.getElementById('input_bank_name')
    ];

    const inputsWebsite = [
        document.getElementById('input_identifier_website'),
        document.getElementById('select_scam_type_website'),
        document.getElementById('input_platform_website')
    ];

    if (mode === 'person') {
        formPerson.style.display = 'block';
        formWebsite.style.display = 'none';
        hiddenType.value = document.getElementById('person_type_select').value; // general or bank

        // BẬT input Person
        inputsPerson.forEach(el => el.disabled = false);
        // TẮT input Website (để không bị bắt validation)
        inputsWebsite.forEach(el => el.disabled = true);

        updatePersonType(); // Reset label SĐT/Bank

    } else {
        formPerson.style.display = 'none';
        formWebsite.style.display = 'block';
        hiddenType.value = 'website';

        // TẮT input Person
        inputsPerson.forEach(el => el.disabled = true);
        // BẬT input Website
        inputsWebsite.forEach(el => el.disabled = false);
    }
}

function updatePersonType() {
    const select = document.getElementById('person_type_select');
    const label = document.getElementById('label_identifier');
    const placeholder = document.getElementById('input_identifier_person');
    const hiddenType = document.getElementById('hidden_report_type');
    const bankDiv = document.getElementById('bank_name_div');

    if (select.value === 'bank') {
        label.innerText = 'Số Tài Khoản Ngân Hàng (*)';
        placeholder.placeholder = 'VD: 1903xxx...';
        hiddenType.value = 'bank';
        bankDiv.style.display = 'block';
    } else {
        label.innerText = 'Số Điện Thoại / Zalo / ID (*)';
        placeholder.placeholder = 'VD: 0912345678';
        hiddenType.value = 'general';
        bankDiv.style.display = 'none';
    }
}

function previewFiles(input) {
    const preview = document.getElementById('file-preview');
    preview.innerHTML = (input.files && input.files.length > 0) ?
        `<i class="fas fa-check-circle me-1"></i> Đã chọn ${input.files.length} ảnh.` : '';
}

window.onload = function () { toggleForm('person'); };
