"""WiseMutts main entry point for AWS Lambda and local execution."""
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
        # Initialize WiseMutts (prompt selection is handled internally via PROMPT_MODE env var)
        wisemutts = WiseMutts()

        # Create media
        print("Step 1: Creating media...")
        try:
            output = await wisemutts.create()
            print(f"✅ Media created: {output}\n")
        except Exception as e:
            print(f"❌ Failed to create media: {e}")
            traceback.print_exc()
            raise

        # Get captions (already generated during media creation)
        print("Step 2: Getting captions...")
        try:
            captions = wisemutts.get_captions()
            caption_text = captions.instagram.caption if hasattr(captions, 'instagram') else ""
            print(f"✅ Captions retrieved: {caption_text[:50]}...\n")
        except Exception as e:
            print(f"❌ Failed to get captions: {e}")
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
