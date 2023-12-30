document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('a[href^="http"], a[href^="/documents/"]').forEach((element) => {
        element.setAttribute('target', '_blank');
        element.setAttribute('rel', 'nofollow noopener');
    });
});
