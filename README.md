# wisemutts 🐕

<img src="logo.png" align="right" width="200px">

Automated Instagram content creation with AI-generated pixel art videos and philosophical narration.

### How It Works

Every day, wisemutts creates and posts beautiful pixel art videos featuring a contemplative dog with whispered wisdom. Each day rotates through three themes:

1. **Presence & Simplicity** - Peace in nature
2. **Digital World** - Navigating technology with clarity
3. **Authenticity** - Being yourself

This is powered by two custom packages I built:

### [mediaichemy](https://github.com/pedroblayaluz/mediaichemy)
<img src="https://github.com/pedroblayaluz/mediaichemy/raw/main/logo.png" align="right" width="100px">

Handles the creative side of wisemutts. It generates the pixel art visuals, creates AI narration, and orchestrates the entire video pipeline. mediaichemy intelligently optimizes costs while maintaining high-quality output, making daily content generation economically viable.

### [instapost](https://github.com/pedroblayaluz/instapost)
<img src="https://github.com/pedroblayaluz/instapost/raw/main/logo.png" align="right" width="100px">

Handles posting to Instagram. Once wisemutts has generated the video and captions, instapost takes care of uploading it as a reel to Instagram with the right metadata and captions, keeping everything automated and seamless.

### 🤖 Automation

GitHub Actions CI/CD automatically creates and posts videos daily at 6 PM São Paulo time (9 PM UTC). Every day, the workflow runs, generates fresh content, and posts to Instagram—all without lifting a finger.

**Hosted on AWS:** wisemutts runs as a containerized Lambda function. Docker packages all dependencies (FFmpeg, ONNX runtime, etc.) efficiently, allowing the project to stay within Lambda's size constraints while handling large media processing workloads.

**Follow [@wisemutts](https://instagram.com/wisemutts) on Instagram for daily wisdom! 📸**

## 🎬 Showcase

Check out some generated videos:

### 🌿 Presence & Simplicity
https://github.com/user-attachments/assets/4097bf88-76fc-4f21-80ef-fb8fd9f033ad
> *Sometimes the best moments are the quiet ones 🐾✨ Find peace in simply being. Double tap if you needed this reminder 💙
> 
> #peaceful #mindfulness #doglovers #pixelart #calm*


*Coming soon...*

---

### 🦋 Authenticity


https://github.com/user-attachments/assets/74e835de-0a49-47c7-9882-6ace671b1013
> *In a world of copies, be an original 🐾✨ Your uniqueness is your superpower. Stay true to you 💙
> 
> #selflove #beyourself #motivation #inspiration #positivevibes*

---
### 🤖 Digital World



https://github.com/user-attachments/assets/dfa9e172-6aa0-4826-9fa6-a63ccd690c60


> *We scroll for connection but feel more alone 💔 Technology built walls, not bridges. Time to remember what it means to be human ✨*
>
> #technology #mentalhealth #connection #awareness #digitaldetox

