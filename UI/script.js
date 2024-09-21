document.querySelector('.toggle-password').addEventListener('click', function () {
    const passwordInput = document.querySelector('input[type="password"]');
    if (passwordInput.type === 'password') {
      passwordInput.type = 'text';
      this.textContent = '🙈';
    } else {
      passwordInput.type = 'password';
      this.textContent = '👁';
    }
  });
  