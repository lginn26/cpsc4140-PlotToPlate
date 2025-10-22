// Garden Form Handler
document.addEventListener('DOMContentLoaded', function() {
    const gardenForm = document.getElementById('gardenForm');
    const createGardenBtn = document.querySelector('.modal-footer .btn-success');

    if (createGardenBtn) {
        createGardenBtn.addEventListener('click', function() {
            createGarden();
        });
    }

    // Allow form submission with Enter key
    if (gardenForm) {
        gardenForm.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                createGarden();
            }
        });
    }
});

function createGarden() {
    const gardenForm = document.getElementById('gardenForm');
    const formData = new FormData(gardenForm);

    const gardenData = {
        name: formData.get('name'),
        description: formData.get('description'),
        location: formData.get('location'),
        plants: formData.get('plants'),
        user_id: 1  // Default user ID - update this based on logged-in user
    };

    // Validate required fields
    if (!gardenData.name.trim()) {
        alert('Please enter a garden name');
        return;
    }

    // Send to API
    fetch('/api/gardens', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(gardenData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Garden created:', data);
        
        // Clear form
        gardenForm.reset();
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('newGardenModal'));
        if (modal) {
            modal.hide();
        }
        
        // Show success message
        alert('Garden created successfully!');
        
        // Reload page to show new garden
        setTimeout(() => {
            location.reload();
        }, 500);
    })
    .catch(error => {
        console.error('Error creating garden:', error);
        alert('Error creating garden: ' + error.message);
    });
}

// Community Form Handler (if you have one)
function createPost() {
    const postForm = document.getElementById('postForm');
    if (!postForm) return;

    const formData = new FormData(postForm);

    const postData = {
        title: formData.get('title'),
        content: formData.get('content'),
        food_type: formData.get('food_type'),
        quantity: formData.get('quantity'),
        location: formData.get('location'),
        user_id: 1  // Default user ID
    };

    if (!postData.title.trim()) {
        alert('Please enter a title');
        return;
    }

    fetch('/api/posts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Post created:', data);
        postForm.reset();
        alert('Post shared successfully!');
        setTimeout(() => {
            location.reload();
        }, 500);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error creating post');
    });
}