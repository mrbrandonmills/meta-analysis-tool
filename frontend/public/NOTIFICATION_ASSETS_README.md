# Notification Assets

This directory should contain the following assets for the notification system:

## Required Assets

### Icons
- `icon-192x192.png` - Large notification icon (192x192 pixels)
- `icon-96x96.png` - Badge icon (96x96 pixels)
- `favicon.ico` - Browser favicon

### Recommended Icon Specifications
- Format: PNG with transparency
- Background: Transparent or solid color
- Design: Simple, recognizable logo or symbol
- Colors: Match your brand colors

### Example Icon Content
- Meta-analysis tool logo
- Microscope or research symbol
- Academic/scientific iconography

## Sound Files (Optional)

The notification system uses embedded data URLs for sounds, but you can add custom sound files:

### Custom Sounds
- `notification-success.mp3` - Success sound (completion)
- `notification-error.mp3` - Error sound (failure)
- `notification-info.mp3` - Info sound (updates)

### Recommended Sound Specifications
- Format: MP3 or WAV
- Duration: 0.5-2 seconds
- Volume: Moderate (not too loud)
- Tone: Pleasant, non-intrusive

## Usage

To use custom sound files instead of embedded data URLs, update `/frontend/src/lib/notifications.ts`:

```typescript
// Replace this line:
audio.src = 'data:audio/wav;base64,...'

// With:
audio.src = '/notification-success.mp3'
```

## Creating Icons

### Using Figma/Sketch
1. Create a 192x192px artboard
2. Design your icon with padding (leave 16px margin)
3. Export as PNG with transparency

### Using Online Tools
- [Favicon Generator](https://realfavicongenerator.net/)
- [Icon Generator](https://www.iconsgenerator.com/)
- [Canva](https://www.canva.com/)

### AI-Generated Icons
- [Midjourney](https://www.midjourney.com/)
- [DALL-E](https://openai.com/dall-e)
- [Stable Diffusion](https://stability.ai/)

Prompt example: "Clean, minimal microscope icon for academic research platform, flat design, transparent background, 512x512"

## Testing

Test your icons by:
1. Running the dev server: `npm run dev`
2. Triggering a notification
3. Checking browser notification appearance
4. Verifying icon clarity and visibility
