/**
 * quiz.js — One-question-per-step quiz UI behaviour.
 *
 * DOM contract (set by quiz.html):
 *   #quiz-progress          — container, data-answered, data-total
 *   #progress-bar-fill      — fill div, data-pct (0-100 int)
 *   #progress-current       — span: current 1-based step number
 *   #progress-total         — span: total question count
 *   .quiz-option-label      — clickable option rows
 *   .quiz-form              — the step form
 *   .quiz-submit-btn        — next/submit button
 *
 * NO multi-question navigation: all step routing is server-driven.
 */

document.addEventListener('DOMContentLoaded', () => {

    // ── Progress bar ──────────────────────────────────────────────── //
    const fill = document.getElementById('progress-bar-fill');
    if (fill) {
        const pct = parseInt(fill.dataset.pct || '0', 10);
        // Animate in after a brief paint delay for smoother feel
        requestAnimationFrame(() => {
            fill.style.width = pct + '%';
        });
    }

    // ── Option accessibility: Enter/Space triggers the radio ─────── //
    document.querySelectorAll('.quiz-option-label').forEach(label => {
        label.setAttribute('tabindex', '0');
        label.addEventListener('keydown', e => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                label.click();
            }
        });
    });

    // ── Submit guard: warn if no option selected ─────────────────── //
    const form = document.querySelector('.quiz-form');
    if (form) {
        form.addEventListener('submit', e => {
            const anyChecked = form.querySelector('input[type="radio"]:checked');
            if (!anyChecked) {
                e.preventDefault();
                const submitBtn = form.querySelector('.quiz-submit-btn');
                if (submitBtn) {
                    submitBtn.classList.add('btn-danger');
                    submitBtn.classList.remove('btn-primary', 'btn-success');
                    submitBtn.textContent = 'Vui lòng chọn đáp án!';
                    setTimeout(() => {
                        submitBtn.classList.remove('btn-danger');
                        submitBtn.classList.add('btn-primary');
                        const isLast = submitBtn.dataset.isLast === '1';
                        submitBtn.innerHTML = isLast
                            ? 'Nộp bài <i class="fas fa-check ms-2"></i>'
                            : 'Tiếp theo <i class="fas fa-arrow-right ms-2"></i>';
                    }, 1800);
                }
            }
        });
    }

});
