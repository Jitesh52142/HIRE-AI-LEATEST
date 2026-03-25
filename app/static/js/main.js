document.addEventListener('DOMContentLoaded', function() {
    // --- Multi-Step Form Logic ---
    const multiStepForm = document.getElementById('multiStepForm');
    if (multiStepForm) {
        const nextBtns = multiStepForm.querySelectorAll('.next-btn');
        const prevBtns = multiStepForm.querySelectorAll('.prev-btn');
        const formSteps = multiStepForm.querySelectorAll('.form-step');
        const submitBtn = document.getElementById('submitBtn');
        const spinner = submitBtn.querySelector('.spinner-border');

        let currentStep = 0;

        nextBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                if (validateStep(currentStep)) {
                    formSteps[currentStep].classList.remove('active');
                    currentStep++;
                    formSteps[currentStep].classList.add('active');
                }
            });
        });

        prevBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                formSteps[currentStep].classList.remove('active');
                currentStep--;
                formSteps[currentStep].classList.add('active');
            });
        });

        multiStepForm.addEventListener('submit', function(e) {
            // Final validation before submitting
            if (!validateStep(currentStep)) {
                e.preventDefault(); // Stop submission if invalid
                return;
            }
            
            // Show loader on submit
            submitBtn.disabled = true;
            spinner.classList.remove('d-none');
            submitBtn.querySelector('span:not(.spinner-border)').textContent = ' Submitting...';
        });

        function validateStep(stepIndex) {
            let isValid = true;
            const currentStepFields = formSteps[stepIndex].querySelectorAll('input[required], select[required], textarea[required]');
            
            currentStepFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                 alert('Please fill out all required fields in this step.');
            }
            return isValid;
        }
    }
});

document.addEventListener('DOMContentLoaded', () => {
    // Multi-step form logic
    const form = document.getElementById('multiStepForm');
    if (form) {
        let currentStep = 0;
        const steps = form.querySelectorAll('.form-step');
        const nextBtns = form.querySelectorAll('.next-btn');
        const prevBtns = form.querySelectorAll('.prev-btn');
        const submitBtn = form.querySelector('.submit-btn');

        function showStep(stepIndex) {
            steps.forEach((step, index) => {
                step.classList.toggle('active', index === stepIndex);
            });
        }

        nextBtns.forEach(button => {
            button.addEventListener('click', () => {
                const currentInputs = steps[currentStep].querySelectorAll('input, select, textarea');
                let isValid = true;
                currentInputs.forEach(input => {
                    if (input.hasAttribute('required') && !input.value) {
                        input.classList.add('is-invalid');
                        isValid = false;
                    } else {
                        input.classList.remove('is-invalid');
                    }
                });

                if (isValid) {
                    currentStep++;
                    showStep(currentStep);
                }
            });
        });

        prevBtns.forEach(button => {
            button.addEventListener('click', () => {
                currentStep--;
                showStep(currentStep);
            });
        });

        // Initialize form
        showStep(currentStep);
    }
});