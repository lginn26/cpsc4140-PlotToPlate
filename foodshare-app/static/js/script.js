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



// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    const postForm = document.getElementById('postForm');
    const submitPostBtn = document.getElementById('submitPostBtn');

    if (submitPostBtn && postForm) {
        submitPostBtn.addEventListener('click', function() {
            createPost();
        });
    }
});

// Create a new post with image upload
function createPost() {
    const postForm = document.getElementById('postForm');
    if (!postForm) return;

    const formData = new FormData(postForm); // picks up file inputs

    // Add user_id 
    formData.append('user_id', 1);

    fetch('/api/posts', {
        method: 'POST',
        body: formData 
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        console.log('Post created:', data);
        postForm.reset();

        // Hide the modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('newPostModal'));
        if (modal) modal.hide();

        alert('Your post was successfully shared!');
        setTimeout(() => location.reload(), 500);
    })
    .catch(error => {
        console.error('Error creating post:', error);
        alert('Error creating post. Please try again.');
    });
}

// Like button handler
document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(e) {
        if (e.target && e.target.closest('.like-button')) {
            const button = e.target.closest('.like-button');
            const postId = button.dataset.postId;
            
            fetch(`/api/posts/${postId}/like`, { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(res => {
                if (!res.ok) throw new Error('Network response was not ok');
                return res.json();
            })
            .then(data => {
                button.querySelector('.likes-count').textContent = data.likes;
            })
            .catch(err => {
                console.error('Error liking post:', err);
                alert('Error updating like count. Please try again.');
            });
        }
    });
});
