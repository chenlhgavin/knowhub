#!/usr/bin/env python3
"""
AI Image Generation Script using Volcano Engine Seedream 4.5 Model

This script generates AI images using the Volcano Engine ARK API,
which is compatible with the OpenAI API format.

Environment Variables:
    VOLCANO_API_KEY: Required. Your Volcano Engine API key
    VOLCANO_ENDPOINT_ID: Optional. The ARK inference endpoint ID for Seedream 4.5
"""

import argparse
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library not installed. Run: pip install requests")
    sys.exit(1)


# Volcano Engine ARK API configuration
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
IMAGES_ENDPOINT = f"{ARK_BASE_URL}/images/generations"

# Default endpoint ID for Seedream 4.5 (user should configure their own)
DEFAULT_ENDPOINT_ID = "doubao-seedream-4-5-251128"

# Supported image sizes (minimum 3686400 pixels required by Seedream 4.5 API)
SUPPORTED_SIZES = [
    "1920x1920", "2048x2048", "2560x2560",
    "2560x1440", "1440x2560",
    "2048x1920", "1920x2048",
    "2880x1620", "1620x2880",
    "3840x2160", "2160x3840"
]


def get_api_key():
    """Get API key from environment variable."""
    api_key = os.environ.get("VOLCANO_API_KEY")
    if not api_key:
        print("Error: VOLCANO_API_KEY environment variable is not set.")
        print("Please set it with your Volcano Engine API key:")
        print("  export VOLCANO_API_KEY='your-api-key-here'")
        sys.exit(1)
    return api_key


def get_endpoint_id(args_endpoint_id=None):
    """Get endpoint ID from argument or environment variable."""
    if args_endpoint_id:
        return args_endpoint_id
    return os.environ.get("VOLCANO_ENDPOINT_ID", DEFAULT_ENDPOINT_ID)


def generate_image(
    prompt: str,
    size: str = "2048x2048",
    quality: str = "standard",
    seed: int = None,
    watermark: bool = False,
    endpoint_id: str = None
) -> dict:
    """
    Generate an image using Volcano Engine Seedream 4.5 API.

    Args:
        prompt: Text description of the image to generate
        size: Image dimensions (e.g., "1024x1024")
        quality: "standard" for 2K or "high" for 4K output
        seed: Random seed for reproducible results
        watermark: Whether to add watermark
        endpoint_id: Volcano ARK inference endpoint ID

    Returns:
        dict containing the API response
    """
    api_key = get_api_key()
    model_id = get_endpoint_id(endpoint_id)

    # Validate size
    if size not in SUPPORTED_SIZES:
        print(f"Warning: Size {size} may not be supported. Supported sizes: {SUPPORTED_SIZES}")

    # Build request payload
    payload = {
        "model": model_id,
        "prompt": prompt,
        "size": size,
        "n": 1,
        "response_format": "b64_json",
        "quality": quality,
        "watermark": watermark
    }

    if seed is not None:
        payload["seed"] = seed

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print(f"Generating image with prompt: {prompt[:100]}...")
    print(f"Size: {size}, Quality: {quality}, Model: {model_id}")

    try:
        response = requests.post(
            IMAGES_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("Error: Request timed out. The server took too long to respond.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_detail = response.json()
        except:
            error_detail = response.text
        print(f"Error: API request failed with status {response.status_code}")
        print(f"Details: {error_detail}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed - {e}")
        sys.exit(1)


def save_image(b64_data: str, output_path: str) -> str:
    """
    Save base64 encoded image data to a file.

    Args:
        b64_data: Base64 encoded image data
        output_path: Path to save the image

    Returns:
        The absolute path of the saved image
    """
    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Decode and save
    image_data = base64.b64decode(b64_data)
    with open(output_file, "wb") as f:
        f.write(image_data)

    return str(output_file.absolute())


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI images using Volcano Engine Seedream 4.5 model"
    )
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        required=True,
        help="Text description of the image to generate"
    )
    parser.add_argument(
        "--size", "-s",
        type=str,
        default="2048x2048",
        help=f"Image size (default: 2048x2048). Supported: {', '.join(SUPPORTED_SIZES)}"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file path (default: ./generated_image_TIMESTAMP.png)"
    )
    parser.add_argument(
        "--quality", "-q",
        type=str,
        choices=["standard", "high"],
        default="standard",
        help="Quality level: 'standard' for 2K, 'high' for 4K (default: standard)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible results"
    )
    parser.add_argument(
        "--watermark",
        action="store_true",
        help="Add watermark on generated image (default: no watermark)"
    )
    parser.add_argument(
        "--endpoint-id", "-e",
        type=str,
        default=None,
        help="Volcano ARK endpoint ID (default: uses VOLCANO_ENDPOINT_ID env var or built-in default)"
    )

    args = parser.parse_args()

    # Generate default output path if not specified
    if args.output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"./generated_image_{timestamp}.png"

    # Generate the image
    result = generate_image(
        prompt=args.prompt,
        size=args.size,
        quality=args.quality,
        seed=args.seed,
        watermark=args.watermark,
        endpoint_id=args.endpoint_id
    )

    # Extract and save the image
    if "data" in result and len(result["data"]) > 0:
        image_data = result["data"][0]

        if "b64_json" in image_data:
            saved_path = save_image(image_data["b64_json"], args.output)
            print(f"\nImage generated successfully!")
            print(f"Saved to: {saved_path}")

            # Print additional info if available
            if "revised_prompt" in image_data:
                print(f"Revised prompt: {image_data['revised_prompt']}")
        elif "url" in image_data:
            print(f"\nImage generated successfully!")
            print(f"Image URL: {image_data['url']}")
        else:
            print("Warning: Unexpected response format")
            print(json.dumps(result, indent=2))
    else:
        print("Error: No image data in response")
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Print usage info if seed was used
    if args.seed:
        print(f"\nTo reproduce this image, use --seed {args.seed}")


if __name__ == "__main__":
    main()
