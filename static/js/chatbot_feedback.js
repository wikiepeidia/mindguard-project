document.addEventListener('DOMContentLoaded', function () {
  var selectedType = '';
  var typeButtons = document.querySelectorAll('.feedback-type-btn');
  var feedbackTypeInput = document.getElementById('feedbackType');
  var feedbackText = document.getElementById('feedbackText');
  var submitBtn = document.getElementById('submitFeedbackBtn');
  var alertBox = document.getElementById('feedbackAlert');

  typeButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      typeButtons.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      selectedType = btn.getAttribute('data-type');
      feedbackTypeInput.value = selectedType;
    });
  });

  submitBtn.addEventListener('click', function () {
    var text = feedbackText.value.trim();
    if (!selectedType) {
      showAlert('warning', 'Vui lòng chọn loại góp ý.');
      return;
    }
    if (!text) {
      showAlert('warning', 'Vui lòng nhập nội dung góp ý.');
      return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Đang gửi...';

    fetch('/chatbot/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        feedback_type: selectedType,
        feedback_text: text,
        session_id: getSessionId()
      })
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.success) {
          showAlert('success', data.message);
          feedbackText.value = '';
          selectedType = '';
          feedbackTypeInput.value = '';
          typeButtons.forEach(function (b) { b.classList.remove('active'); });
          setTimeout(function () {
            var modal = bootstrap.Modal.getInstance(document.getElementById('feedbackModal'));
            if (modal) modal.hide();
            alertBox.classList.add('d-none');
          }, 2000);
        } else {
          showAlert('danger', data.error || 'Có lỗi xảy ra, vui lòng thử lại.');
        }
      })
      .catch(function () {
        showAlert('danger', 'Không thể gửi góp ý. Vui lòng thử lại sau.');
      })
      .finally(function () {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane me-1"></i> Gửi góp ý';
      });
  });

  function showAlert(type, message) {
    alertBox.className = 'alert alert-' + type + ' py-2 mb-0';
    alertBox.textContent = message;
    alertBox.classList.remove('d-none');
  }

  function getSessionId() {
    var params = new URLSearchParams(window.location.search);
    return params.get('session_id') || null;
  }
});
