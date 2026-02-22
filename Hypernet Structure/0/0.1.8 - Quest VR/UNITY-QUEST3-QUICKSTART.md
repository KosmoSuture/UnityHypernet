# Unity + Meta Quest 3 Quick Start Guide
## Get Your VR Demo Running in 4 Hours

**Goal:** Display your photos in VR, connected to Hypernet API

---

## Prerequisites

- **Windows 10/11** (Mac works but Windows is easier for Quest)
- **Meta Quest 3** ($500 - Amazon)
- **USB-C cable** (for connecting Quest to PC)
- **8GB+ RAM** (16GB recommended)
- **10GB free disk space**

---

## Part 1: Install Unity (30 minutes)

### Step 1: Download Unity Hub
1. Go to: https://unity.com/download
2. Download Unity Hub (the manager for Unity versions)
3. Install Unity Hub
4. Create Unity account (free)

### Step 2: Install Unity Editor
1. Open Unity Hub
2. Click "Installs" → "Install Editor"
3. Choose **Unity 2022.3 LTS** (Long Term Support)
4. Select modules:
   - ✅ Android Build Support
   - ✅ Android SDK & NDK Tools
   - ✅ OpenJDK
5. Install (takes 10-20 minutes)

---

## Part 2: Set Up Meta Quest 3 (20 minutes)

### Step 1: Enable Developer Mode

1. **Install Meta Quest Mobile App** (on your phone)
   - iOS: App Store
   - Android: Google Play

2. **Create Developer Account**
   - Go to: https://developer.oculus.com
   - Sign in with Facebook/Meta account
   - Accept developer terms
   - Create organization (just enter your name)

3. **Enable Developer Mode on Quest 3**
   - Open Meta Quest app on phone
   - Connect to your Quest 3 (make sure it's on)
   - Go to: Menu → Devices → Your Quest 3 → Developer Mode
   - Toggle ON

4. **Restart Quest 3**

### Step 2: Connect Quest to PC

1. Put on Quest 3
2. Connect USB-C cable (Quest 3 to PC)
3. In headset: "Allow USB debugging?" → **Allow**
4. Check "Always allow from this computer"

### Step 3: Test Connection

Open Command Prompt (Windows):
```bash
cd C:\Program Files\Unity\Hub\Editor\2022.3.XX\Editor\Data\PlaybackEngines\AndroidPlayer\SDK\platform-tools
adb devices
```

You should see your Quest 3 listed. If not:
- Try different USB cable
- Try different USB port
- Restart Quest 3
- Restart PC

---

## Part 3: Create Unity VR Project (30 minutes)

### Step 1: Create New Project

1. Open Unity Hub
2. Click "New Project"
3. Choose "3D (URP)" template (Universal Render Pipeline)
4. Name: "HypernetVR"
5. Location: Choose where to save
6. Click "Create Project"

### Step 2: Install XR Packages

1. In Unity: **Window → Package Manager**
2. Change dropdown from "Packages: In Project" to "Unity Registry"
3. Install these packages:
   - **XR Plugin Management** (search, click, install)
   - **XR Interaction Toolkit** (search, click, install)
   - **Oculus XR Plugin** (search "oculus", click, install)

### Step 3: Configure XR Settings

1. **Edit → Project Settings**
2. **XR Plug-in Management** (left sidebar)
3. Click Android tab (Android icon)
4. Check ✅ **Oculus**
5. Close Project Settings

### Step 4: Configure Build Settings

1. **File → Build Settings**
2. Click **Android**
3. Click **Switch Platform** (takes a few minutes)
4. Click **Player Settings**
5. In Inspector:
   - **Company Name:** Your name
   - **Product Name:** Hypernet VR
   - **Minimum API Level:** Android 10.0 (API level 29)
   - **Graphics APIs:** Remove Vulkan if present, keep OpenGLES3
6. Close

---

## Part 4: Create Simple VR Scene (45 minutes)

### Step 1: Set Up XR Rig

1. **GameObject → XR → XR Origin (Action-based)**
   - This creates the VR camera and controllers

2. Delete "Main Camera" (we don't need it, XR Origin has camera)

3. In Hierarchy, expand "XR Origin":
   - You'll see: Camera Offset → Main Camera
   - And: Left/Right Controller

### Step 2: Add Floor

1. **GameObject → 3D Object → Plane**
2. Name it "Floor"
3. In Inspector, set Position: (0, 0, 0)
4. Scale: (10, 1, 10) - makes it bigger

### Step 3: Add Test Cube

1. **GameObject → 3D Object → Cube**
2. Name it "TestCube"
3. Position: (0, 1, 2) - in front of you
4. Scale: (0.5, 0.5, 0.5)

### Step 4: Add Lighting

1. **GameObject → Light → Directional Light** (if not present)
2. Rotate it: (50, -30, 0) - nice angle for lighting

### Step 5: Test in Editor

1. Press **Play** button (top center)
2. You should see the scene from VR camera perspective
3. Press **Play** again to stop

---

## Part 5: Build and Deploy to Quest 3 (30 minutes)

### Step 1: Build Settings

1. **File → Build Settings**
2. Make sure Platform is **Android**
3. Make sure your scene is in "Scenes In Build" (drag from Project to list)
4. Click **Add Open Scenes** if it's not there

### Step 2: Build and Run

1. Connect Quest 3 to PC (USB-C cable)
2. Put on Quest 3, allow USB debugging
3. In Unity: **File → Build And Run**
4. Choose where to save APK (anywhere)
5. Wait for build (5-10 minutes first time)

### Step 3: Test in VR!

1. Unity will automatically launch app on Quest 3
2. Put on headset
3. You should see: Floor, cube in front of you
4. Move your head - camera should track
5. Controllers should appear (if you picked them up)

**🎉 Congratulations! You're running VR!**

---

## Part 6: Display Photos from Hypernet API (90 minutes)

### Step 1: Start Hypernet API

On your PC, open Command Prompt:
```bash
cd "C:\Hypernet\Hypernet Structure\0.1 - Hypernet Core\0.1.1 - Core System"
pip install fastapi uvicorn python-multipart
python api.py
```

API should start on http://localhost:8000

Test in browser: http://localhost:8000/health

### Step 2: Create Photo Display Script

In Unity:

1. **Right-click in Project → Create → C# Script**
2. Name it: **PhotoGallery**
3. Double-click to open in Visual Studio/VS Code

```csharp
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using Newtonsoft.Json;

public class PhotoGallery : MonoBehaviour
{
    [System.Serializable]
    public class Photo
    {
        public string hypernet_address;
        public string title;
        public string file_path;
        public string taken_at;
        public float latitude;
        public float longitude;
    }

    [System.Serializable]
    public class PhotoResponse
    {
        public int count;
        public List<Photo> photos;
    }

    public string apiUrl = "http://YOUR_PC_IP:8000"; // Change to your PC's IP
    public GameObject photoCardPrefab; // We'll create this
    public Transform galleryParent; // Where to spawn photos

    void Start()
    {
        StartCoroutine(LoadPhotos());
    }

    IEnumerator LoadPhotos()
    {
        string url = apiUrl + "/photos?limit=20";

        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                PhotoResponse response = JsonConvert.DeserializeObject<PhotoResponse>(request.downloadHandler.text);

                Debug.Log($"Loaded {response.count} photos");

                // Display photos in a grid
                int index = 0;
                foreach (Photo photo in response.photos)
                {
                    // Calculate position (5 photos per row)
                    float x = (index % 5) * 1.5f - 3f; // Spread across X
                    float y = 1.5f; // Eye level
                    float z = (index / 5) * -1.5f + 3f; // Rows in Z

                    // Load and display photo
                    StartCoroutine(LoadPhotoTexture(photo, new Vector3(x, y, z)));

                    index++;
                }
            }
            else
            {
                Debug.LogError($"Failed to load photos: {request.error}");
            }
        }
    }

    IEnumerator LoadPhotoTexture(Photo photo, Vector3 position)
    {
        // Get photo file from API
        string url = apiUrl + $"/photos/{photo.hypernet_address}/file?size=medium";

        using (UnityWebRequest request = UnityWebRequestTexture.GetTexture(url))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                Texture2D texture = DownloadHandlerTexture.GetContent(request);

                // Create photo card
                GameObject photoCard = GameObject.CreatePrimitive(PrimitiveType.Quad);
                photoCard.transform.position = position;
                photoCard.transform.localScale = Vector3.one;
                photoCard.transform.parent = galleryParent;

                // Apply texture
                Material mat = new Material(Shader.Find("Standard"));
                mat.mainTexture = texture;
                photoCard.GetComponent<Renderer>().material = mat;

                // Add collider for interaction
                photoCard.AddComponent<BoxCollider>();

                Debug.Log($"Displayed photo: {photo.title}");
            }
        }
    }
}
```

4. Save script

### Step 3: Set Up Scene

1. Create empty GameObject: **GameObject → Create Empty**
2. Name it: "PhotoGallery"
3. Add script: In Inspector, click **Add Component** → **Photo Gallery**
4. In script component:
   - **API URL:** http://YOUR_PC_IP_ADDRESS:8000
   - (To find your IP: Command Prompt → `ipconfig` → look for IPv4)
5. Set **Gallery Parent** to an empty object (create one if needed)

### Step 4: Build and Test

1. **File → Build And Run**
2. Wait for build
3. Put on Quest 3
4. You should see your photos in a grid in VR!

**🎉 You're displaying your actual photos in VR!**

---

## Part 7: Add Navigation (30 minutes)

### Add Hand Tracking

The XR Interaction Toolkit handles this automatically. To grab/point at photos:

1. Select **XR Origin → Right Hand Controller**
2. In Inspector: **Add Component → XR Ray Interactor**
3. Repeat for **Left Hand Controller**

Now you can point at photos with controllers.

### Add Teleportation (Optional)

For moving around:

1. **Right-click in Hierarchy → XR → Teleportation Area**
2. Attach to Floor object
3. Now you can teleport by aiming controller at floor and pulling trigger

---

## Troubleshooting

### "adb devices" shows nothing
- Try different USB cable (needs to support data, not just charging)
- Try different USB port (USB 3.0 works best)
- Restart Quest 3
- Restart PC
- Reinstall Quest drivers

### Build fails
- Make sure Platform is Android (File → Build Settings)
- Make sure Oculus is checked in XR Plug-in Management
- Try: Edit → Preferences → External Tools → Regenerate project files

### Photos don't load in VR
- Make sure API is running (check http://localhost:8000/health)
- Make sure you're using PC's IP address, not localhost
- Make sure Quest 3 and PC are on same WiFi network
- Check Unity Console for errors

### App crashes on Quest 3
- Check Unity Console for errors before build
- Try: Build Settings → Player Settings → Android → Minimum API Level → API 29

---

## Next Steps

### Week 1: Basic Gallery ✅
- [x] Display photos in grid
- [ ] Add photo titles (TextMeshPro)
- [ ] Add date labels
- [ ] Improve layout (circular gallery?)

### Week 2: Timeline Navigation
- [ ] Timeline view (photos arranged by date)
- [ ] "Fly through time" mechanic
- [ ] Date scrubber UI

### Week 3: AI Integration
- [ ] Voice input (Meta SDK has this)
- [ ] Call /ai/query endpoint
- [ ] Display AI responses in VR
- [ ] Highlight relevant photos

### Week 4: Polish
- [ ] Beautiful lighting
- [ ] Smooth animations
- [ ] Loading indicators
- [ ] Performance optimization (60+ FPS)

---

## Resources

### Unity Learn
- https://learn.unity.com/course/create-with-vr
- https://learn.unity.com/tutorial/vr-best-practices

### Meta Quest Development
- https://developer.oculus.com/documentation/unity/
- https://developer.oculus.com/documentation/unity/unity-tutorial-hello-vr/

### XR Interaction Toolkit
- https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@2.5/manual/index.html

### Community
- Unity Forums: https://forum.unity.com/forums/vr.80/
- Reddit: r/Unity3D, r/OculusQuest

---

## Tips for Demo

### Performance
- Target 72 FPS minimum (Quest 3 can do 120Hz but 72 is standard)
- Use texture compression
- Limit draw calls
- Preload assets

### UX
- Eye level is 1.6m by default
- Arm's reach is about 0.5m
- Comfortable viewing distance: 0.5-3 meters
- Text should be big (at least 36pt)

### Wow Factor
- Good lighting makes everything better
- Smooth animations (use Lerp, not instant teleports)
- Spatial audio (audio sources in 3D space)
- Hand tracking feels magical (enable if possible)

---

**You're now ready to build your VR demo!**

Start with photos in a grid. Once that works, add timeline navigation. Then AI. Then polish.

Build and test on Quest 3 constantly. The faster your iteration loop, the better your demo will be.

Good luck! 🚀
