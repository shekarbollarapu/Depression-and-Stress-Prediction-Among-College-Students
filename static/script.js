document.addEventListener('DOMContentLoaded', () => {
    const images = document.querySelectorAll('.moving-image');
    let selectedImage = null;

    images.forEach(image => {
        image.addEventListener('click', () => {
            if (selectedImage) {
                // Swap positions with the previously selected image
                swapImages(selectedImage, image);
                selectedImage = null;
            } else {
                // Highlight the selected image
                selectedImage = image;
                image.style.boxShadow = '0 0 10px 5px #00f';
            }
        });

        image.addEventListener('transitionend', () => {
            image.classList.remove('swapping');
        });
    });

    function swapImages(img1, img2) {
        // Remove highlight from the selected image
        img1.style.boxShadow = '';

        // Get parent container
        const parent = img1.parentNode;

        // Get all images
        const allImages = Array.from(parent.children);

        // Get indexes of the images to swap
        const index1 = allImages.indexOf(img1);
        const index2 = allImages.indexOf(img2);

        // Swap images in the DOM
        if (index1 < index2) {
            parent.insertBefore(img2, img1);
            parent.insertBefore(img1, allImages[index2]);
        } else {
            parent.insertBefore(img1, img2);
            parent.insertBefore(img2, allImages[index1]);
        }

        // Add swapping class for animation
        img1.classList.add('swapping');
        img2.classList.add('swapping');
    }
});
