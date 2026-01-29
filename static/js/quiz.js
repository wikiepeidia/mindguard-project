document.addEventListener('DOMContentLoaded', () => {
    // === Session Management (Fix Issue: Leave resets, F5 keeps) ===
    // Check navigation type to detect reload vs navigation
    const entries = performance.getEntriesByType("navigation");
    const isReload = entries.length > 0 && entries[0].type === 'reload';

    if (!isReload) {
        // If it is NOT a reload (i.e. normal navigation, back button, new visit), reset session
        sessionStorage.removeItem('quiz_start_time');
    }

    // === Timer Logic ===
    const DURATION_SECONDS = 15 * 60; // 15 mins
    const timerDisplay = document.getElementById('timer');
    const quizForm = document.getElementById('quizForm');
    
    // Check for stored start time or start new
    let startTime = sessionStorage.getItem('quiz_start_time');
    if (!startTime) {
        startTime = Date.now();
        sessionStorage.setItem('quiz_start_time', startTime);
    }
    
    let timerInterval = setInterval(updateTimer, 1000);
    updateTimer(); // Initial call
    
    // Intercept internal links to warn/reset
    let pendingUrl = null;
    const exitModalEl = document.getElementById('exitModal');
    let exitModal = null;
    if (exitModalEl) {
        exitModal = new bootstrap.Modal(exitModalEl);
        
        // Handle confirm button inside modal
        const confirmBtn = document.getElementById('confirmExitBtn');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                if (pendingUrl) {
                    sessionStorage.removeItem('quiz_start_time');
                    window.isSubmitting = true; // Bypass beforeunload check
                    window.location.href = pendingUrl;
                }
            });
        }
    }

    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href && href !== '#' && !href.startsWith('javascript')) {
                e.preventDefault();
                pendingUrl = href;
                if (exitModal) {
                    exitModal.show();
                } else {
                    // Fallback if modal is missing
                    if(confirm('Bạn có chắc chắn muốn rời khỏi bài kiểm tra? Tiến trình sẽ bị hủy.')) {
                        sessionStorage.removeItem('quiz_start_time');
                        window.isSubmitting = true;
                        window.location.href = href;
                    }
                }
            }
        });
    });

    function updateTimer() {
        const now = Date.now();
        const elapsedSeconds = Math.floor((now - parseInt(startTime)) / 1000);
        let timeLeft = DURATION_SECONDS - elapsedSeconds;

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            sessionStorage.removeItem('quiz_start_time');
            alert("Hết giờ! Hệ thống sẽ tự động nộp bài.");
            submitQuiz(true); // Force submit
            return;
        }

        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        
        if (timerDisplay) {
            timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            if (timeLeft < 60) {
                timerDisplay.style.color = '#dc3545';
                timerDisplay.closest('.timer-container').style.borderColor = '#fecaca';
                timerDisplay.closest('.timer-container').style.backgroundColor = '#fef2f2';
            }
        }
    }

    // === Navigation Logic ===
    window.currentQuestion = 1; // Global for access
    
    // Initialize buttons
    updateNavState();
    
    // Restore answered state from DOM (if reloaded)
    // We bind this dynamically
    document.querySelectorAll('.question-block').forEach((block, index) => {
        const qIndex = index + 1;
        if (block.querySelector('input:checked')) {
            markAnsweredInNav(qIndex);
        }
    });
});

function markAnswered(index) {
    const btn = document.getElementById(`nav-btn-${index}`);
    if (btn) {
        markAnsweredInNav(index);
        updateProgress();
        
        // Auto-show next button or enable it if on current question
        if (index === window.currentQuestion) {
            const nextBtn = document.getElementById('btn-next');
            if (nextBtn) {
               nextBtn.classList.add('pulse-animation');
               setTimeout(() => nextBtn.classList.remove('pulse-animation'), 1000);
            }
        }
    }
}

function markAnsweredInNav(index) {
    const btn = document.getElementById(`nav-btn-${index}`);
    if (btn) {
        btn.classList.add('answered');
        btn.classList.remove('btn-outline-secondary');
    }
}

function updateProgress() {
    const total = getTotalQuestions();
    let answeredCount = 0;
    for (let i = 1; i <= total; i++) {
        const block = document.getElementById(`q-block-${i}`);
        if (block && block.querySelector('input:checked')) {
            answeredCount++;
        }
    }
    const completedCountEl = document.getElementById('completed-count');
    if (completedCountEl) completedCountEl.textContent = answeredCount;
    const barEl = document.getElementById('progress-bar-fill');
    if (barEl) {
        const pct = (answeredCount / total) * 100;
        barEl.style.width = `${pct}%`;
    }
}

function changeQuestion(step) {
    const total = getTotalQuestions();
    let nextQ = window.currentQuestion + step;
    if (nextQ >= 1 && nextQ <= total) {
        goToQuestion(nextQ);
    }
}

function goToQuestion(qIndex) {
    const total = getTotalQuestions();
    if (qIndex < 1 || qIndex > total) return;
    
    // Hide current
    const currentBlock = document.getElementById(`q-block-${window.currentQuestion}`);
    const currentNav = document.getElementById(`nav-btn-${window.currentQuestion}`);
    
    if (currentBlock) {
        currentBlock.classList.remove('d-flex');
        currentBlock.classList.add('d-none');
    }
    if (currentNav) currentNav.classList.remove('active');
    
    // Show new
    window.currentQuestion = qIndex;
    const newBlock = document.getElementById(`q-block-${window.currentQuestion}`);
    const newNav = document.getElementById(`nav-btn-${window.currentQuestion}`);
    
    if (newBlock) {
        newBlock.classList.remove('d-none');
        newBlock.classList.add('d-flex');
    }
    if (newNav) newNav.classList.add('active');
    
    // Update controls
    updateNavState();
}

function updateNavState() {
    const prevBtn = document.getElementById('btn-prev');
    const nextBtn = document.getElementById('btn-next');
    
    // Use optional chaining or check existence
    const progressText = document.getElementById('progress-text'); 
    
    const total = getTotalQuestions();
    
    if (prevBtn) {
        prevBtn.disabled = (window.currentQuestion === 1);
    }
    
    if (nextBtn) {
        if (window.currentQuestion === total) {
            nextBtn.innerHTML = 'Nộp bài <i class="fas fa-check ms-2"></i>';
            nextBtn.onclick = validateAndSubmit; 
            nextBtn.classList.remove('btn-primary');
            nextBtn.classList.add('btn-success');
        } else {
            nextBtn.innerHTML = 'Tiếp theo <i class="fas fa-arrow-right ms-2"></i>';
            nextBtn.onclick = () => changeQuestion(1);
            nextBtn.classList.add('btn-primary');
            nextBtn.classList.remove('btn-success');
        }
    }
    
    if (progressText) progressText.textContent = window.currentQuestion;
    
    // Update progress bar
    updateProgress();
}

function getTotalQuestions() {
    // Get from data attribute in HTML or count elements
    return document.querySelectorAll('.question-block').length;
}

function validateAndSubmit() {
    const total = getTotalQuestions();
    let unanswered = [];
    
    for (let i = 1; i <= total; i++) {
        const block = document.getElementById(`q-block-${i}`);
        const inputs = block.querySelectorAll('input[type="radio"]');
        let answered = false;
        inputs.forEach(input => {
            if (input.checked) answered = true;
        });
        
        if (!answered) {
            unanswered.push(i);
        }
    }

    if (unanswered.length > 0) {
        // Show alert
        alert(`Bạn chưa trả lời các câu hỏi: ${unanswered.join(', ')}. Vui lòng hoàn thành để nộp bài.`);
        
        // Highlight in sidebar
        unanswered.forEach(idx => {
            const btn = document.getElementById(`nav-btn-${idx}`);
            if (btn) {
                btn.classList.add('unanswered-warn');
                setTimeout(() => btn.classList.remove('unanswered-warn'), 2000);
            }
        });
        
        // Jump to first unanswered
        goToQuestion(unanswered[0]);
    } else {
        if (confirm('Bạn có chắc chắn muốn nộp bài? Bạn sẽ không thể sửa lại sau khi nộp.')) {
            submitQuiz();
        }
    }
}

function submitQuiz(force = false) {
    if (!force) {
        // Clean up session storage
        sessionStorage.removeItem('quiz_start_time');
    }
    
    // Set flag to prevent unload warning
    window.isSubmitting = true;
    document.getElementById('quizForm').submit();
}

// Window unload warning
window.isSubmitting = false;
window.onbeforeunload = function(e) {
    if (!window.isSubmitting) {
        e = e || window.event;
        const msg = 'Bạn có chắc muốn rời khỏi bài kiểm tra?';
        if (e) e.returnValue = msg;
        return msg;
    }
};
