/* main.js — Hire AI Form Validation & UI Helpers */

document.addEventListener('DOMContentLoaded', function () {

  /* ---- helpers ---- */
  function isEmail(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v); }
  function isUrl(v)   { try { new URL(v); return true; } catch { return false; } }
  function isPhone(v) { return /^[\+]?[\d\s\-\(\)]{7,20}$/.test(v.trim()); }

  function setError(field, msg) {
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    const fb = field.closest('.form-group, .field-group > div, .col-sm-6, .col-12, .col-sm-12')
                    ?.querySelector('.invalid-feedback')
              || field.parentElement?.querySelector('.invalid-feedback')
              || field.nextElementSibling;
    if (fb && fb.classList.contains('invalid-feedback')) fb.textContent = msg;
  }

  function clearError(field) {
    field.classList.remove('is-invalid', 'is-valid');
  }

  /* clear on input */
  document.querySelectorAll('.form-control, .form-select').forEach(f => {
    f.addEventListener('input',  () => clearError(f));
    f.addEventListener('change', () => clearError(f));
  });

  /* ---- Password strength (register) ---- */
  const pwdInput     = document.getElementById('register-password');
  const strengthFill = document.getElementById('strength-fill');
  const strengthText = document.getElementById('strength-text');

  if (pwdInput && strengthFill) {
    function checkRule(id, pass) {
      const el = document.getElementById(id);
      if (!el) return;
      el.classList.toggle('met', pass);
      el.querySelector('i').className = pass ? 'fas fa-check-circle' : 'far fa-circle';
    }

    pwdInput.addEventListener('input', function () {
      const v = this.value;
      const checks = {
        length:  v.length >= 8,
        number:  /\d/.test(v),
        upper:   /[A-Z]/.test(v),
        special: /[^A-Za-z0-9]/.test(v),
      };
      const score  = Object.values(checks).filter(Boolean).length;
      const colors = ['', '#ef4444', '#f59e0b', '#3b82f6', '#10b981'];
      const labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];

      checkRule('rule-length',  checks.length);
      checkRule('rule-number',  checks.number);
      checkRule('rule-upper',   checks.upper);
      checkRule('rule-special', checks.special);

      strengthFill.style.width      = (score * 25) + '%';
      strengthFill.style.background = colors[score] || '';
      if (strengthText) {
        strengthText.textContent  = labels[score] || '';
        strengthText.style.color  = colors[score] || '';
      }
    });
  }

  /* ---- Login form ---- */
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
      let ok = true;
      const email = this.querySelector('[name="email"]');
      const pwd   = this.querySelector('[name="password"]');
      if (!email.value.trim() || !isEmail(email.value)) {
        setError(email, 'Please enter a valid email address.'); ok = false;
      }
      if (!pwd.value.trim()) {
        setError(pwd, 'Password is required.'); ok = false;
      }
      if (!ok) e.preventDefault();
    });
  }

  /* ---- Register form ---- */
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', function (e) {
      let ok = true;
      const email = this.querySelector('[name="email"]');
      const pwd   = this.querySelector('[name="password"]');
      if (!email.value.trim() || !isEmail(email.value)) {
        setError(email, 'Please enter a valid professional email address.'); ok = false;
      }
      if (!pwd.value || pwd.value.length < 8) {
        setError(pwd, 'Password must be at least 8 characters.'); ok = false;
      } else if (!/\d/.test(pwd.value)) {
        setError(pwd, 'Password must include at least one number.'); ok = false;
      }
      if (!ok) e.preventDefault();
    });
  }

  /* ---- Contact form ---- */
  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      let ok = true;
      const name    = this.querySelector('[name="name"]');
      const email   = this.querySelector('[name="email"]');
      const message = this.querySelector('[name="message"]');
      if (!name.value.trim() || name.value.trim().length < 2) {
        setError(name, 'Enter your full name (at least 2 characters).'); ok = false;
      }
      if (!email.value.trim() || !isEmail(email.value)) {
        setError(email, 'Please enter a valid email address.'); ok = false;
      }
      if (!message.value.trim() || message.value.trim().length < 10) {
        setError(message, 'Message must be at least 10 characters.'); ok = false;
      }
      if (!ok) e.preventDefault();
    });
  }

  /* ---- Wizard form ---- */
  const wizardForm = document.getElementById('wizard-form');
  if (wizardForm) {
    // Real-time salary cross-check
    const minSal = wizardForm.querySelector('[name="MinimumSalary"]');
    const maxSal = wizardForm.querySelector('[name="MaximumSalary"]');
    if (maxSal && minSal) {
      maxSal.addEventListener('input', function () {
        if (minSal.value && this.value && Number(this.value) < Number(minSal.value)) {
          setError(this, 'Must be ≥ minimum salary.');
        } else {
          clearError(this);
        }
      });
    }

    wizardForm.addEventListener('submit', function (e) {
      let ok = true;

      this.querySelectorAll('[required]').forEach(field => {
        const v = field.value.trim();
        if (!v) {
          setError(field, 'This field is required.'); ok = false; return;
        }
        if (field.type === 'email' && !isEmail(v)) {
          setError(field, 'Please enter a valid email address.'); ok = false;
        } else if (field.type === 'url' && !isUrl(v)) {
          setError(field, 'Please enter a valid URL (e.g. https://example.com).'); ok = false;
        } else if (field.type === 'tel' && !isPhone(v)) {
          setError(field, 'Please enter a valid phone number.'); ok = false;
        } else if (field.type === 'number' && (isNaN(Number(v)) || Number(v) < 0)) {
          setError(field, 'Please enter a valid positive number.'); ok = false;
        }
      });

      if (minSal && maxSal && minSal.value && maxSal.value) {
        if (Number(maxSal.value) < Number(minSal.value)) {
          setError(maxSal, 'Maximum salary must be ≥ minimum salary.'); ok = false;
        }
      }

      if (!ok) {
        e.preventDefault();
        const first = wizardForm.querySelector('.is-invalid');
        if (first) first.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        const btn = this.querySelector('[type="submit"]');
        if (btn) {
          btn.disabled = true;
          btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        }
      }
    });
  }

  /* ---- Auto-dismiss flash alerts ---- */
  document.querySelectorAll('.glass-alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateX(20px)';
      alert.style.transition = 'opacity 0.3s, transform 0.3s';
      setTimeout(() => alert.remove(), 320);
    }, 5000);
  });

});
