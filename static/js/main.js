document.getElementById('helloBtn').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/hello');
        const data = await response.json();
        document.getElementById('message').textContent = data.message;
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('message').textContent = 'Error fetching message';
    }
});
