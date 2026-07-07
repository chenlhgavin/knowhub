---
name: ai-image
description: Generate AI images using Volcano Engine's Seedream 4.5 model. Use this skill when users want to create images, generate artwork, or mention image generation with specific styles such as Ghibli, Futuristic, Pixar, Oil Painting, Chinese Painting, Anime, Realistic, Cyberpunk, Watercolor, or other artistic styles.
---

# AI Image Generation Skill

This skill uses Volcano Engine's Seedream 4.5 model to generate high-quality AI images from text prompts.

## Prerequisites

- **API Key**: Set the `VOLCANO_API_KEY` environment variable with your Volcano Engine API key
- **Endpoint ID**: You need a Volcano Engine ARK inference endpoint ID for the Seedream 4.5 model

## Usage

When the user requests image generation:

1. **Analyze the request** to understand:
   - The subject/content of the image
   - The desired style (Ghibli, Pixar, Oil Painting, Chinese Painting, etc.)
   - Any specific requirements (size, aspect ratio, quality)

2. **Construct an effective prompt** following these guidelines:
   - Be specific and descriptive
   - Include style keywords if specified
   - Add quality enhancers like "high quality", "detailed", "professional"
   - For Ghibli style: add "Studio Ghibli style, anime, soft lighting, whimsical"
   - For Pixar style: add "Pixar 3D animation style, vibrant colors, expressive"
   - For Oil Painting: add "oil painting, brushstrokes visible, classical art"
   - For Chinese Painting: add "Chinese traditional painting, ink wash, elegant brushwork"
   - For Futuristic: add "futuristic, sci-fi, neon lights, cyberpunk aesthetics"

3. **Run the generation script** using:

```bash
python /home/ubuntu/workspace/codeai/.claude/skills/ai-image/scripts/generate_image.py \
  --prompt "your detailed prompt here" \
  --size "2048x2048" \
  --output "/path/to/output.png"
```

## Script Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--prompt` | Yes | - | The text description of the image to generate |
| `--size` | No | 2048x2048 | Image size (minimum 3686400 pixels required) |
| `--output` | No | ./generated_image.png | Output file path |
| `--quality` | No | standard | Quality level: "standard" (2K) or "high" (4K) |
| `--seed` | No | random | Seed for reproducible results |
| `--watermark` | No | false | Add watermark if set (default: no watermark) |
| `--endpoint-id` | No | env | Volcano ARK endpoint ID (or set VOLCANO_ENDPOINT_ID env var) |

## Supported Sizes

Note: Seedream 4.5 requires minimum 3686400 pixels (approximately 1920x1920).

- Square: 1920x1920, 2048x2048, 2560x2560
- Landscape: 2560x1440, 2880x1620, 3840x2160
- Portrait: 1440x2560, 1620x2880, 2160x3840

## Example Prompts by Style

### Ghibli Style
```
Studio Ghibli style, a young girl walking through a magical forest with glowing spirits,
soft lighting, dreamy atmosphere, anime, whimsical, hand-drawn quality, Hayao Miyazaki inspired
```

### Pixar Style
```
Pixar 3D animation style, a cute robot exploring a colorful candy factory,
vibrant colors, expressive eyes, detailed textures, cinematic lighting, family friendly
```

### Oil Painting
```
Classical oil painting style, a serene landscape at sunset with rolling hills and a windmill,
visible brushstrokes, rich warm colors, impressionist technique, museum quality
```

### Chinese Painting
```
Traditional Chinese ink wash painting, misty mountains with pine trees and a small pavilion,
elegant brushwork, minimalist composition, black ink on rice paper, peaceful atmosphere
```

### Futuristic/Cyberpunk
```
Futuristic cyberpunk cityscape at night, neon lights reflecting on wet streets,
flying vehicles, holographic advertisements, rain, high tech low life, blade runner inspired
```

## Workflow

1. Parse the user's request
2. Identify the desired style and subject
3. Craft an optimized prompt
4. Call the generation script
5. Display the generated image path to the user
6. Offer to regenerate with different parameters if needed

## Error Handling

- If `VOLCANO_API_KEY` is not set, inform the user to set it
- If generation fails, show the error message and suggest alternatives
- For rate limiting errors, wait and retry

## Notes

- The Seedream 4.5 model excels at artistic styles and detailed scenes
- Higher quality settings (4K) take longer but produce better results
- Using a consistent seed allows reproducing the same image
