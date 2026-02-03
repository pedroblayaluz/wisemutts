import asyncio
import os
import json
import traceback
from dotenv import load_dotenv
from src.wisemutts import WiseMutts


async def main():
    """Run WiseMutts automation: create media, generate captions, and post."""

    # Load environment variables from .env file
    load_dotenv()

    # Check for required environment variables
    if not os.getenv("INSTAGRAM_ACCESS_TOKEN"):
        raise ValueError("INSTAGRAM_ACCESS_TOKEN environment variable not set")
    if not os.getenv("INSTAGRAM_USER_ID"):
        raise ValueError("INSTAGRAM_USER_ID environment variable not set")

    print("🚀 Starting WiseMutts automation...\n")

    try:
        # Determine prompt selection mode
        prompt_index = None
        prompt_mode = "daily"  # default

        # Check for PROMPT_MODE environment variable (random, daily, or index)
        env_prompt_mode = os.getenv("PROMPT_MODE", "random").lower()
        if env_prompt_mode == "random":
            prompt_mode = "random"
        elif env_prompt_mode.isdigit():
            prompt_index = int(env_prompt_mode)

        mode_display = prompt_mode if prompt_index is None else f'Index {prompt_index}'
        print(f"📋 Prompt selection mode: {mode_display}\n")

        # Initialize WiseMutts
        wisemutts = WiseMutts(
            prompt_index=prompt_index,
            prompt_mode=prompt_mode
        )

        # Create media
        print("Step 1: Creating media...")
        try:
            output = await wisemutts.create()
            print(f"✅ Media created: {output}\n")
        except Exception as e:
            print(f"❌ Failed to create media: {e}")
            traceback.print_exc()
            raise

        # Generate captions
        print("Step 2: Generating captions...")
        try:
            captions = await wisemutts.create_captions()
            caption_text = captions.instagram.caption if hasattr(captions, 'instagram') else ""
            print(f"✅ Captions generated: {caption_text[:50]}...\n")
        except Exception as e:
            print(f"❌ Failed to generate captions: {e}")
            traceback.print_exc()
            raise

        # Post to Instagram
        print("Step 3: Posting to Instagram...")
        try:
            success = wisemutts.post(caption=caption_text)

            if success:
                print("\n🎉 WiseMutts automation completed successfully!")
            else:
                print("\n❌ Failed to post to Instagram")
                raise RuntimeError("Post returned False")
        except Exception as e:
            print(f"❌ Failed to post to Instagram: {e}")
            traceback.print_exc()
            raise

    except Exception as e:
        print(f"\n❌ Error during automation: {e}")
        traceback.print_exc()


def lambda_handler(event, context):
    """AWS Lambda handler for scheduled execution."""
    try:
        asyncio.run(main())
        return {
            'statusCode': 200,
            'body': json.dumps({'message': '✅ WiseMutts automation completed successfully'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


if __name__ == "__main__":
    asyncio.run(main())
