# Unity VR - Start Right Now (3 Hours)
## Get Your First Photo Displaying in VR Today

**Goal:** By end of today, see a photo in VR on your Quest 3

---

## Hour 1: Install Unity

### Step 1: Download Unity Hub (10 min)
1. Go to: https://unity.com/download
2. Download "Unity Hub" (not Unity Editor directly)
3. Install Unity Hub
4. Create Unity account (free) - you'll need this

### Step 2: Install Unity Editor (15 min download + install)
1. Open Unity Hub
2. Click "Installs" (left sidebar)
3. Click "Install Editor" (blue button, top right)
4. Choose **"2022.3 LTS"** (Long Term Support - most stable)
5. Select these modules (MUST HAVE):
   - ✅ **Android Build Support**
   - ✅ **Android SDK & NDK Tools**
   - ✅ **OpenJDK**
6. Click "Install" (bottom right)
7. Wait 15-30 minutes (good time for coffee break)

### Step 3: While Installing - Set Up Quest 3 (20 min)

**Create Developer Account:**
1. Go to: https://developer.oculus.com
2. Sign in with your Meta/Facebook account
3. Click "Create Organization"
4. Enter your name (doesn't matter, just needs something)
5. Accept terms

**Enable Developer Mode on Quest 3:**
1. Install "Meta Quest" app on your phone
   - iOS: App Store
   - Android: Google Play
2. Open app, connect to your Quest 3
3. In app: Menu (bottom) → Devices → Your Quest 3 → Developer Mode
4. Toggle ON
5. Restart Quest 3

**Connect Quest to PC:**
1. Put on Quest 3
2. Connect USB-C cable (Quest to PC)
3. In headset: Dialog appears "Allow USB debugging?"
4. Click **"Allow"**
5. Check **"Always allow from this computer"**

**Test Connection:**
```bash
# This path might be slightly different - check your Unity version number
cd "C:\Program Files\Unity\Hub\Editor\2022.3.XX\Editor\Data\PlaybackEngines\AndroidPlayer\SDK\platform-tools"
adb devices
```

You should see something like:
```
List of devices attached
1WMHH8XXXX    device
```

If you see your device, you're connected! ✅

---

## Hour 2: Create VR Project

### Step 1: Create Project (5 min)
1. Open Unity Hub
2. Click "New Project" (top right)
3. Choose **"3D (URP)"** template
   - URP = Universal Render Pipeline (better for VR)
4. Project Name: **"HypernetVR"**
5. Location: Choose where to save (anywhere is fine)
6. Click **"Create Project"** (bottom right)
7. Unity Editor will open (takes 2-3 minutes first time)

### Step 2: Install VR Packages (15 min)

**Install XR Packages:**
1. In Unity: **Window** → **Package Manager**
2. Top-left dropdown: Change from "In Project" to **"Unity Registry"**
3. Search for and install (click package, click "Install" button):
   - **"XR Plugin Management"** (search "xr plugin")
   - **"XR Interaction Toolkit"** (search "xr interaction")
   - Wait for each to finish before next one

4. Search "oculus" → Install **"Oculus XR Plugin"**

**Configure XR:**
1. **Edit** → **Project Settings**
2. Left sidebar: Click **"XR Plug-in Management"**
3. You'll see tabs: PC icon, Android icon, etc.
4. Click **Android** tab (Android icon)
5. Check the box: ✅ **"Oculus"**
6. Close Project Settings

**Switch to Android:**
1. **File** → **Build Settings**
2. In "Platform" list, click **"Android"**
3. Click **"Switch Platform"** (bottom)
4. Wait 2-5 minutes (Unity is converting project)
5. Leave Build Settings open for next step

### Step 3: Configure Build Settings (5 min)

Still in Build Settings window:

1. Click **"Player Settings..."** (bottom left)
2. In Inspector (right side):
   - **Company Name:** Your name
   - **Product Name:** Hypernet VR
3. Scroll down to **"Minimum API Level"**
   - Change to: **"Android 10.0 (API level 29)"**
4. Close Inspector
5. Close Build Settings

### Step 4: Create VR Scene (10 min)

**Add XR Rig:**
1. In Hierarchy (left panel):
   - Right-click → **GameObject** → **XR** → **XR Origin (Action-based)**
2. You should see "XR Origin" appear in Hierarchy
3. Expand it (click arrow) - you'll see:
   - Camera Offset
     - Main Camera (this is your VR view)
   - Left/Right Controller

**Delete Old Camera:**
1. In Hierarchy, select "Main Camera" (the one NOT under XR Origin)
2. Press **Delete** key
3. Now you only have the XR Origin camera

**Add Floor:**
1. Right-click in Hierarchy
2. **3D Object** → **Plane**
3. Name it "Floor"
4. In Inspector (right), set Transform:
   - Position: X=0, Y=0, Z=0
   - Scale: X=10, Y=1, Z=10

**Add Test Cube:**
1. Right-click in Hierarchy
2. **3D Object** → **Cube**
3. Name it "TestCube"
4. In Inspector, set Transform:
   - Position: X=0, Y=1, Z=2 (in front of you)
   - Scale: X=0.5, Y=0.5, Z=0.5

**Test in Editor:**
1. Press **Play** button (top center, triangle icon)
2. In "Game" view, you should see floor and cube from VR camera
3. Press **Play** again to stop

---

## Hour 3: Build to Quest 3 & Display Photo

### Step 1: First Build (20 min)

**Save Scene:**
1. **File** → **Save As**
2. Name: "PhotoGallery"
3. Save in "Assets/Scenes" folder

**Build and Run:**
1. Make sure Quest 3 is connected via USB
2. Put on Quest 3, make sure it's on
3. In Unity: **File** → **Build And Run**
4. Choose where to save APK (anywhere, like Desktop)
5. Name it: "Hypernet.apk"
6. Click **Save**
7. Wait 5-10 minutes (first build is slow)

**If build succeeds:**
- Quest 3 will automatically launch the app
- Put on headset
- You should see: Floor and cube!
- Move your head - it should track
- **🎉 YOU'RE RUNNING VR!**

**If build fails:**
- Check error in Unity Console (bottom panel)
- Common fix: Make sure you selected Oculus in XR Plug-in Management (Android tab)
- Google the exact error message

### Step 2: Display a Photo (40 min)

**Start Your API:**

Open Command Prompt:
```bash
cd "C:\Hypernet\Hypernet Structure\0.1 - Hypernet Core\0.1.1 - Core System"
python api.py
```

Leave it running. Test: http://localhost:8000/health

**Find Your PC's IP Address:**

Command Prompt:
```bash
ipconfig
```

Look for "IPv4 Address" under your WiFi adapter. Example: `192.168.1.100`

**Create Photo Display Script:**

In Unity:
1. Right-click in Project panel (bottom) → **Create** → **C# Script**
2. Name it: **"SimplePhotoDisplay"**
3. Double-click to open in your code editor
4. Replace ALL contents with:

```csharp
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class SimplePhotoDisplay : MonoBehaviour
{
    // CHANGE THIS TO YOUR PC'S IP ADDRESS!
    public string apiUrl = "http://192.168.1.100:8000";

    void Start()
    {
        StartCoroutine(LoadFirstPhoto());
    }

    IEnumerator LoadFirstPhoto()
    {
        Debug.Log("Loading photo from API...");

        // Get list of photos
        string url = apiUrl + "/photos?limit=1";
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Got photos list!");

                // Parse response (simplified - assumes at least 1 photo)
                string json = request.downloadHandler.text;

                // Extract first photo address (hacky but works for demo)
                int haStart = json.IndexOf("hypernet_address\":\"") + 19;
                int haEnd = json.IndexOf("\"", haStart);
                string photoAddress = json.Substring(haStart, haEnd - haStart);

                Debug.Log("Photo address: " + photoAddress);

                // Load the actual photo
                StartCoroutine(LoadPhotoImage(photoAddress));
            }
            else
            {
                Debug.LogError("Failed to load photos: " + request.error);
            }
        }
    }

    IEnumerator LoadPhotoImage(string photoAddress)
    {
        string url = apiUrl + "/photos/" + photoAddress + "/file?size=medium";
        Debug.Log("Loading image: " + url);

        using (UnityWebRequest request = UnityWebRequestTexture.GetTexture(url))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Image loaded!");

                Texture2D texture = DownloadHandlerTexture.GetContent(request);

                // Create a quad to display the photo
                GameObject photoQuad = GameObject.CreatePrimitive(PrimitiveType.Quad);
                photoQuad.transform.position = new Vector3(0, 1.5f, 3); // In front of you
                photoQuad.transform.localScale = new Vector3(2, 1.5f, 1); // Landscape

                // Apply the texture
                Material material = new Material(Shader.Find("Standard"));
                material.mainTexture = texture;
                photoQuad.GetComponent<Renderer>().material = material;

                Debug.Log("Photo displayed in VR!");
            }
            else
            {
                Debug.LogError("Failed to load image: " + request.error);
            }
        }
    }
}
```

5. **IMPORTANT:** Change line 8 to YOUR PC's IP address!
6. Save file (Ctrl+S)

**Add Script to Scene:**

1. In Hierarchy, right-click → **Create Empty**
2. Name it: "PhotoLoader"
3. Select "PhotoLoader"
4. In Inspector, click **Add Component**
5. Search for "SimplePhotoDisplay"
6. Click it to add

**Save and Build:**

1. **File** → **Save** (save scene)
2. **File** → **Build And Run**
3. Wait for build (faster this time, 2-3 min)

**Test:**

1. Put on Quest 3
2. You should see your photo floating in front of you!
3. Walk around it, look at it
4. **🎉 YOU'RE VIEWING YOUR DATA IN VR!**

**Debug if it doesn't work:**

1. Take off headset
2. In Unity: **Window** → **Console**
3. Look for error messages
4. Common issues:
   - Wrong IP address (check ipconfig again)
   - API not running (restart it)
   - Quest and PC not on same WiFi
   - Firewall blocking port 8000

---

## ✅ Success!

**If you can see a photo in VR, you've achieved:**
- ✅ Unity installed and configured
- ✅ Quest 3 development working
- ✅ VR app building and deploying
- ✅ API connection working
- ✅ Photo rendering in 3D space

**This is your foundation. Everything else builds on this.**

---

## Tomorrow: Make It Better

### Easy Improvements (30 min each):

**1. Display Multiple Photos:**
```csharp
// Change limit=1 to limit=10
string url = apiUrl + "/photos?limit=10";

// In a loop, create multiple quads at different positions
float x = 0;
for (each photo) {
    photoQuad.transform.position = new Vector3(x, 1.5f, 3);
    x += 2.5f; // Space them out
}
```

**2. Add Text Labels:**
- Import TextMeshPro (Window → TextMeshPro → Import TMP Essentials)
- Create text above each photo with title and date

**3. Better Layout:**
- Arrange photos in a circle around you
- Use: `x = radius * Cos(angle)`, `z = radius * Sin(angle)`

**4. Add Lighting:**
- GameObject → Light → Directional Light
- Adjust intensity and color for mood

---

## Resources

**If Stuck:**
- Google: "Unity VR Quest 3 [your error]"
- Unity Forums: https://forum.unity.com/forums/vr.80/
- Reddit: r/Unity3D (post your issue)
- Meta Quest Developer Forums

**Learning:**
- Unity Learn (free courses): https://learn.unity.com
- Brackeys YouTube (best Unity tutorials)
- "Create with VR" Unity course

**Community:**
- Unity Discord: discord.gg/unity
- Quest Developer Discord

---

## What You Have Now

- ✅ Working VR development environment
- ✅ Can build apps to Quest 3
- ✅ Can load data from Hypernet API
- ✅ Can display photos in VR
- ✅ Foundation for full demo

**Next week:** Timeline view, AI integration, polish

**But for today:** CELEBRATE! You built VR! 🎉

---

## Quick Reference

**Build to Quest 3:**
```
File → Build And Run
```

**Test in Unity Editor:**
```
Press Play button (top center)
```

**Check Console for Errors:**
```
Window → Console
```

**Find Your IP:**
```
Command Prompt: ipconfig
Look for IPv4 Address
```

**Restart API:**
```
Ctrl+C (stop)
python api.py (restart)
```

---

**Now go build it!** 🚀
