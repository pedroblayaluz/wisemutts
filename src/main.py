import asyncio
import os
import json
from src.wisemutts import WiseMutts


async def main():
    """Run WiseMutts automation: create media, generate captions, and post."""

    # Check for required environment variables
    if not os.getenv("INSTAGRAM_ACCESS_TOKEN"):
        raise ValueError("INSTAGRAM_ACCESS_TOKEN environment variable not set")
    if not os.getenv("INSTAGRAM_USER_ID"):
        raise ValueError("INSTAGRAM_USER_ID environment variable not set")

    print("🚀 Starting WiseMutts automation...\n")

    try:
        # Initialize WiseMutts
        wisemutts = WiseMutts()

        # Create media
        print("Step 1: Creating media...")
        output = await wisemutts.create()
        print(f"✅ Media created: {output}\n")

        # Generate captions
        print("Step 2: Generating captions...")
        captions = await wisemutts.create_captions()
        caption_text = captions.instagram.caption if hasattr(captions, 'instagram') else ""
        print("✅ Captions generated\n")

        # Post to Instagram
        print("Step 3: Posting to Instagram...")
        success = wisemutts.post(caption=caption_text)

        if success:
            print("\n🎉 WiseMutts automation completed successfully!")
        else:
            print("\n❌ Failed to post to Instagram")

    except Exception as e:
        print(f"❌ Error: {e}")


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
