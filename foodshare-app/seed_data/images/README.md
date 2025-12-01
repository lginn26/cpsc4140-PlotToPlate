# Image Placeholder

Place your header images for posts in this directory.

## Recommended Images

For the seed data posts, consider adding:

1. **tomatoes.jpg** - Fresh cherry or heirloom tomatoes
2. **herbs.jpg** - Basil, mint, or herb garden
3. **zucchini.jpg** - Fresh zucchini harvest
4. **lettuce.jpg** - Lettuce or leafy greens
5. **pumpkins.jpg** - Fall pumpkins
6. **garden_workshop.jpg** - People gardening together
7. **peppers.jpg** - Bell peppers or hot peppers
8. **community_garden.jpg** - Garden overview

## Image Specifications

- **Format**: JPG, PNG, or WebP
- **Size**: Recommended 800x600px or 1200x800px
- **File Size**: Keep under 500KB for web performance
- **Aspect Ratio**: 4:3 or 16:9 works best

## Usage in Seed Script

To use images in the seed script, update the post creation:

```python
post = Post(
    title='Fresh Tomatoes Available!',
    content='...',
    image_url='/static/uploads/tomatoes.jpg',  # Add this line
    food_type='Tomatoes',
    ...
)
```

Then copy your images to `static/uploads/`:

```bash
cp seed_data/images/* static/uploads/
```

## Free Image Sources

If you need free garden images:
- Unsplash: https://unsplash.com/s/photos/garden
- Pexels: https://www.pexels.com/search/vegetables/
- Pixabay: https://pixabay.com/images/search/garden/

Remember to respect image licenses and attribution requirements.
