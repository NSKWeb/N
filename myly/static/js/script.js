document.addEventListener('DOMContentLoaded', () => {
    const copyBtn = document.getElementById('copy-btn');
    const shortUrlInput = document.getElementById('short_url');

    if (copyBtn && shortUrlInput) {
        copyBtn.addEventListener('click', () => {
            shortUrlInput.select();
            shortUrlInput.setSelectionRange(0, 99999); // For mobile devices

            try {
                navigator.clipboard.writeText(shortUrlInput.value);

                // Visual feedback
                copyBtn.textContent = 'Copied!';
                copyBtn.classList.add('copied');

                setTimeout(() => {
                    copyBtn.textContent = 'Copy';
                    copyBtn.classList.remove('copied');
                }, 2000);

            } catch (err) {
                console.error('Failed to copy: ', err);
                alert('Failed to copy URL.');
            }
        });
    }
});
