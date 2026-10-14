# .NET 10 MAUI Development on a MacBook Air M3 — Full Setup Guide

A complete, end-to-end guide for building .NET 10 MAUI apps on a MacBook Air with an
Apple M3 (Apple Silicon / `arm64`) chip, including Apple certificates, provisioning
profiles, Xcode + Keychain, simulators, pairing the Mac as a build host for a Windows
machine, and configuring Visual Studio on that Windows machine to pair back to the Mac.

> **Who this is for:** You are on macOS with an Apple Silicon Mac (M3) and want to build
> iOS, Mac Catalyst, and Android apps with .NET MAUI. You may also have a Windows PC
> running Visual Studio that builds iOS apps by pairing to this Mac.
>
> **Versions used in this guide (verify before you start — see [Section 9](#9-version-compatibility-matrix)):**
> .NET SDK 10.0.4xx · MAUI workload 10.0.1xx · Xcode 26.x / 27.x · Visual Studio 2026 (or 2022 17.12+).
> Apple's toolchain and the .NET workloads are tightly coupled. **A .NET iOS/Mac Catalyst
> workload is built for one specific Xcode version.** Mismatches produce errors such as
> *"This version of .NET for iOS requires Xcode X.Y. The current version of Xcode is A.B."*
> Always install the Xcode version that your installed workload expects.

---

## Table of contents

1. [How the pieces fit together](#1-how-the-pieces-fit-together)
2. [Prerequisites and hardware notes for the MacBook Air M3](#2-prerequisites-and-hardware-notes-for-the-macbook-air-m3)
3. [Part 1 — Set up the MacBook Air M3](#3-part-1--set-up-the-macbook-air-m3)
4. [Part 2 — Apple certificates, Keychain, and provisioning profiles](#4-part-2--apple-certificates-keychain-and-provisioning-profiles)
5. [Part 3 — Install and manage iOS simulators](#5-part-3--install-and-manage-ios-simulators)
6. [Part 4 — Make the Mac a build host (pairing target)](#6-part-4--make-the-mac-a-build-host-pairing-target)
7. [Part 5 — Visual Studio on the Windows pairing machine](#7-part-5--visual-studio-on-the-windows-pairing-machine)
8. [Part 6 — Create and run your first app](#8-part-6--create-and-run-your-first-app)
9. [Version compatibility matrix](#9-version-compatibility-matrix)
10. [Troubleshooting appendix](#10-troubleshooting-appendix)
11. [Sources](#11-sources)

---

## 1. How the pieces fit together

Apple's build tools (`xcodebuild`, `ibtool`, `actool`, the iOS Simulator, and code
signing) **only run on macOS**. That single fact drives the entire setup:

| Machine | Role | What must be installed |
| --- | --- | --- |
| **MacBook Air M3** | The build host. Compiles and signs iOS/Mac Catalyst apps, runs the iOS Simulator. | .NET 10 SDK + MAUI workload, Xcode, Xcode command-line tools, simulators, Rosetta 2, Mono, Apple developer certificates/profiles in Keychain. |
| **Windows PC (optional)** | IDE front-end only. Runs Visual Studio, edits code, and *pairs to* the Mac over the network to build/sign/deploy. | Visual Studio 2026 (or 2022 17.12+), the **.NET Multi-platform App UI development** workload, an Apple Developer API key, and a paired connection to the Mac. |

Two valid workflows:

- **Mac-only (recommended for the M3):** Do everything on the Mac using **Visual Studio
  Code + the .NET MAUI extension**, or **JetBrains Rider**. No pairing needed. You get the
  fastest builds and native simulators.
- **Windows + paired Mac:** Edit on Windows in Visual Studio; Visual Studio drives the Mac
  over SSH for builds, signing, and deployment. Simulators can render in a *remote iOS
  Simulator for Windows* window.

You can do both at once. The Mac serves as the source of truth for Apple tooling.

---

## 2. Prerequisites and hardware notes for the MacBook Air M3

**Hardware / OS**

- MacBook Air M3 (Apple Silicon, `arm64`). All downloads below must be the **Apple
  Silicon / arm64** variants — never Intel/x64 builds (they will not run or will run under
  slow emulation).
- macOS version must satisfy Xcode's minimum. Recent Xcode releases require **macOS 26.2
  (Tahoe) or later**. Keep macOS up to date before installing Xcode.
- **Disk space:** budget generously. Xcode (~15–40 GB after components), multiple iOS
  simulator runtimes (~7 GB each), the Android SDK/emulators, and the .NET workloads add
  up quickly. 256 GB models fill fast; keep 60–80 GB free.
- **RAM:** 8 GB works for basic MAUI/iOS builds but 16 GB+ is strongly recommended once you
  run a simulator and Android emulator at the same time.
- A stable network connection; the Mac and Windows PC should be on the **same LAN/subnet**
  for automatic discovery during pairing.

**Accounts**

- A free **Apple ID** (needed for Xcode and for local simulator work).
- A **paid Apple Developer Program membership** (Individual or Organization) is required to
  deploy to physical devices, create development/distribution certificates and
  provisioning profiles, and publish to the App Store.
- A **Microsoft account with an active Visual Studio subscription** if you use the VS Code
  C# Dev Kit / .NET MAUI extension.

**Recommended terminal setup**

```bash
# Install Homebrew if you don't already have it (Apple Silicon path is /opt/homebrew)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Homebrew on Apple Silicon needs its bin dir on PATH:
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
brew --version
```

---

## 3. Part 1 — Set up the MacBook Air M3

### 3.1 Install the .NET 10 SDK (arm64)

Download the **.NET 10 SDK** for **macOS Apple Silicon** (`.pkg`) from the official .NET
download page (`https://dotnet.microsoft.com/download/dotnet/10.0`). The installer places
the SDK in `/usr/local/share/dotnet` and adds `dotnet` to your PATH.

Alternatively, via Homebrew:

```bash
brew install --cask dotnet-sdk
```

Verify:

```bash
dotnet --version          # e.g. 10.0.4xx
dotnet --info             # confirm "Architecture: arm64" and "OS Name: Mac OS X"
```

> If `dotnet` is "command not found", open a **new** terminal (or restart) so the shell
> picks up the updated PATH.

### 3.2 Install the .NET MAUI workload

The SDK alone does not include MAUI. Install the workload (elevated permissions are needed
on macOS):

```bash
sudo dotnet workload install maui
```

Verify:

```bash
dotnet workload list
# Expect: maui   <version>
dotnet workload --info
```

To pin a specific workload set (recommended for reproducibility and to match your Xcode
version):

```bash
# Example: install a specific workload set version
sudo dotnet workload install maui --version 10.0.401.1
```

To install individual platform workloads explicitly (iOS/Mac Catalyst are the ones that
need a Mac):

```bash
sudo dotnet workload install ios maccatalyst macos android maui
```

> **Tip:** If a project contains a `global.json`, the SDK version it pins must be installed,
> and its workload set must be honored. Read `global.json`, `Directory.Build.props`, and the
> `.csproj` before installing "the latest" of anything.

### 3.3 Install Xcode and the command-line tools

1. Install Xcode from the **Mac App Store** (search "Xcode"). If you need a *specific*
   older Xcode version to match your workload, download it from
   `https://developer.apple.com/download/all/` (Apple ID required) and keep multiple
   versions side by side using tools like `xcodes` (`brew install xcodesorg/made/xcodes`).
2. **Launch Xcode once** after installing so it can install its additional components and
   let you accept the license.
3. Install the command-line tools and point `xcode-select` at the full Xcode app:

```bash
xcode-select --install                 # installs the standalone CLT if missing
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -runFirstLaunch        # accepts the license non-interactively
xcodebuild -version                    # confirm the version Xcode reports
xcode-select -p                        # should print the Xcode Developer path
```

4. In **Xcode > Settings > Locations**, confirm **Command Line Tools** points to your Xcode
   installation.
5. In **Xcode > Settings > Components**, install the **iOS Simulator runtime(s)** you need
   (see [Section 5](#5-part-3--install-and-manage-ios-simulators)).

> **Version match is critical.** Compare `xcodebuild -version` with the Xcode version your
> `ios`/`maccatalyst` workload requires. If they differ, either install the required Xcode
> or downgrade/upgrade the workload. See [Section 9](#9-version-compatibility-matrix).

### 3.4 Install Rosetta 2 (required on Apple Silicon for pairing)

Even on an M3, the pairing stack relies on Intel-based components (`mono-sgen`), so Rosetta
must be present for the Visual Studio **Pair to Mac** workflow:

```bash
softwareupdate --install-rosetta --agree-to-license
```

### 3.5 Install Mono (required for pairing)

Mono is needed on the Mac build host for the pairing agent. Install the stable macOS
package from `https://www.mono-project.com/download/stable/#download-mac`, or via
Homebrew:

```bash
brew install mono
mono --version
```

> Mono is only needed if you will pair from a Windows machine. A Mac-only VS Code/Rider
> workflow does not require it.

### 3.6 (Optional) Android development

Android builds do not require Xcode, but do require a JDK and the Android SDK.

```bash
# Java (Microsoft OpenJDK 17) — Apple Silicon build
brew install --cask microsoft-openjdk@17
# or download from https://learn.microsoft.com/java/openjdk/download

export JAVA_HOME=$(/usr/libexec/java_home -v 17)
echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 17)' >> ~/.zprofile
```

The easiest way to install the Android SDK is via the MAUI `InstallAndroidDependencies`
MSBuild target:

```bash
dotnet new maui -n "MyMauiApp"
cd MyMauiApp
dotnet build -t:InstallAndroidDependencies -f net10.0-android \
  -p:AndroidSdkDirectory="$HOME/Library/Android/sdk" \
  -p:JavaSdkDirectory="$JAVA_HOME" \
  -p:AcceptAndroidSDKLicenses=True
```

Then create an Apple-Silicon emulator (note `arm64-v8a`, not `x86_64`):

```bash
cd "$HOME/Library/Android/sdk/cmdline-tools/latest/bin"
./sdkmanager --install emulator
./sdkmanager --install "system-images;android-35;google_apis;arm64-v8a"
./avdmanager list device
./avdmanager create avd -n MyAndroidVirtualDevice-API35 \
  -k "system-images;android-35;google_apis;arm64-v8a" -d pixel_9
```

Set `ANDROID_HOME`:

```bash
echo 'export ANDROID_HOME="$HOME/Library/Android/sdk"' >> ~/.zprofile
```

### 3.7 (Optional) IDE on the Mac

**Visual Studio Code + .NET MAUI extension (recommended for Mac-only work):**

1. Install VS Code from `https://code.visualstudio.com`.
2. In the Extensions view, install the **.NET MAUI** extension. It pulls in **C# Dev Kit**
   and **C#** automatically.
3. Sign in with your Microsoft account (C# Dev Kit requires an active Visual Studio
   subscription).
4. Open the Command Palette (`Cmd+Shift+P`) and run the walkthrough commands to configure
   each environment:
   - **.NET MAUI: Configure Apple → Refresh Apple environment**
   - **.NET MAUI: Configure Android → Refresh Android environment**

**JetBrains Rider** is also a fully supported cross-platform MAUI IDE and can build/deploy
iOS directly on the Mac.

### 3.8 Verify the Mac environment

```bash
dotnet --info                 # SDK, runtime, arm64, workloads
dotnet workload list          # maui, ios, maccatalyst, android present
xcodebuild -version           # Xcode version
xcode-select -p               # Xcode path
xcrun simctl list runtimes    # installed simulator runtimes
softwareupdate --install-rosetta --agree-to-license   # idempotent; safe to re-run
mono --version                # only if pairing from Windows
```

A quick smoke test (build for the simulator):

```bash
dotnet new maui -n MauiSmokeTest
cd MauiSmokeTest
dotnet build -f net10.0-ios -p:RuntimeIdentifier=iossimulator-arm64
```

---

## 4. Part 2 — Apple certificates, Keychain, and provisioning profiles

This section covers the Apple identity layer. You need it to run on a **physical device**
and to publish. Simulator-only development does **not** require certificates or profiles.

### 4.1 Enroll and accept agreements

1. Enroll in the **Apple Developer Program** (`https://developer.apple.com/programs`) —
   Individual or Organization. Approval can take hours to a couple of days.
2. Sign in to `https://developer.apple.com/account` and to
   `https://appstoreconnect.apple.com` and **accept any pending licensing agreements**.
   Skipping this is a common cause of "Authentication Service Is Unavailable" errors later.
3. Note your **Team ID** (10-character string) under Membership. You'll need it for App IDs
   and profiles.

Everything below lives under **Certificates, Identifiers & Profiles**
(`https://developer.apple.com/account/resources`).

### 4.2 Concepts (read this once)

- **Signing certificate** = a public certificate + its **private key**. It establishes your
  identity with Apple. The **private key never leaves the machine that created it** — this
  is why certificates must be *exported* (as `.p12`) to move between machines.
- **App ID** = a reverse-DNS identifier (e.g. `com.yourcompany.yourapp`). It must match your
  MAUI app's **Application ID** (which also drives the bundle identifier in `Info.plist`).
  - *Wildcard* App ID (`com.yourcompany.*`) — simpler, works for most apps.
  - *Explicit* App ID (`com.yourcompany.yourapp`) — required for app-specific capabilities
    (Push Notifications, App Groups, Apple Pay, HealthKit, In-App Purchase, etc.).
- **Provisioning profile** = the glue: it ties an **App ID** + one or more **certificates**
  + a set of **registered devices** together, and defines which **capabilities** the app may
  use.
- **Keychain Access** on macOS is where certificates + private keys live. Xcode and the
  .NET build read them from there.

> ⚠️ **You may have only two iOS development certificates at a time.** Creating a third
> requires revoking an existing one, and any machine using a revoked certificate can no
> longer sign. **Back up certificates and private keys.** Losing the private key means
> revoking the certificate and re-provisioning every affected device.

### 4.3 Create a signing certificate

You can do this in **three** ways. Pick one.

#### Option A — Let Xcode manage it automatically (easiest)

1. Open **Xcode > Settings > Accounts**, add your Apple ID, and select your team.
2. Click **Manage Certificates…** and press **+** to add **Apple Development** (and
   **Apple Distribution** for release).
3. Xcode creates the certificate and installs the certificate + private key into
   **Keychain Access** for you.

This is the recommended path if you develop primarily on the Mac.

#### Option B — Create the certificate in Xcode but sign manually

Same as Option A, then use the certificate name shown in **Keychain Access > My
Certificates** in your project's `CodesignKey`.

#### Option C — Create the certificate manually with a CSR from Keychain Access

Use this when you want explicit control or when creating the identity on the Windows side.

1. **Generate a Certificate Signing Request (CSR) in Keychain Access:**
   - Open **Keychain Access** (Applications > Utilities).
   - Menu: **Keychain Access > Certificate Assistant > Request a Certificate From a
     Certificate Authority…**
   - Enter your email and a common name, choose **Saved to disk**, and save the
     `.certSigningRequest` file. This also creates a private key in your login keychain.
2. **Upload the CSR to Apple:**
   - Go to `https://developer.apple.com/account/resources/certificates/list` and click **+**.
   - Under **Software**, choose **Apple Development** (for development) or a distribution
     type (**Apple Distribution**, **iOS Distribution**, etc.).
   - Upload the `.certSigningRequest`, then **Download** the generated `.cer`.
3. **Import the `.cer` into Keychain Access:**
   - Double-click the downloaded `.cer`, or drag it into **Keychain Access** (login
     keychain). The certificate pairs with the private key you created in step 1 and appears
     as valid under **My Certificates**.
4. Confirm the identity is complete: in **Keychain Access > My Certificates**, the entry
   should have a disclosure triangle (private key present). If the private key is missing,
   the identity cannot sign.

#### Export / back up the identity as `.p12` (do this now)

1. In **Keychain Access > My Certificates**, find your certificate (e.g.
   `Apple Development: Your Name (TEAMID)`).
2. Right-click → **Export…**, choose **Personal Information Exchange (.p12)**.
3. Set a strong password. Store the `.p12` **and** its password somewhere safe (a password
   manager). This is your portable backup and the file you import on the Windows machine.

> The name of the certificate as it appears in Keychain (e.g.
> `Apple Development: Your Name (ABCDEFGH)`) is exactly what you put in the `CodesignKey`
> MSBuild property, if you set it manually.

### 4.4 Register devices (needed for on-device development)

1. Connect the iPhone/iPad to the Mac with a USB cable.
2. In Xcode, open **Window > Devices and Simulators**, select the **Devices** tab, pick the
   device, and copy its **Identifier** (the UDID).
3. In the Apple Developer portal, go to
   `https://developer.apple.com/account/resources/devices/list`, click **+**, choose the
   platform, name the device, paste the UDID, and register it.
4. Repeat for every device you want to deploy to. (With **automatic provisioning**, Visual
   Studio/Xcode can register devices for you when they're plugged into the Mac.)

### 4.5 Create the App ID

1. Go to `https://developer.apple.com/account/resources/identifiers/list`, click **+**.
2. Choose **App IDs → App**, then **Continue**.
3. Enter a **Description** and a **Bundle ID**:
   - **Wildcard** (`com.yourcompany.*`) — recommended unless you need app-specific
     capabilities.
   - **Explicit** (`com.yourcompany.yourapp`) — required for app-specific capabilities.
4. Enable any required **Capabilities / App Services**, then **Continue → Register**.
5. Make sure your MAUI project's **Application ID** matches this exactly.

### 4.6 Create a provisioning profile

1. Go to `https://developer.apple.com/account/resources/profiles/list`, click **+**.
2. Under **Development**, choose **iOS App Development** (or a **Distribution** type for
   release), then **Continue**.
3. Select the **App ID** you created, then **Continue**.
4. Select the **certificate(s)** to include, then **Continue**.
5. Select the **devices** the app may install on, then **Continue**.
6. Give the profile a **name** and click **Generate**, then **Download** it.
7. **Install it:** double-click the `.mobileprovision` file on the Mac to add it to Xcode's
   profiles, or manage it via Xcode's **Manage Certificates / Profiles**.

### 4.7 Automatic vs. manual provisioning in MAUI

**Automatic provisioning (recommended).** Visual Studio (Windows) or Xcode (Mac) creates
and manages signing identities, App IDs, and profiles for you.

- On the Mac, enable it in your Apple ID/team settings in Xcode, or let the .NET build
  select the right identity/profile.
- In Visual Studio: right-click the project → **Properties → iOS > Bundle Signing** → set
  **Scheme** to **Automatic Provisioning**, then click **Configure Automatic Provisioning**
  and select your team.

Automatic provisioning will create a **wildcard** App ID by default; it switches to an
explicit App ID when you enable an entitlement that requires one (Push Notifications, App
Groups, Apple Pay, Game Center, HealthKit, HomeKit, In-App Purchase, NFC, Personal VPN,
etc.).

**Manual provisioning.** Use the certificate + App ID + profile you built above. In the
project file:

```xml
<PropertyGroup>
  <CodesignKey>Apple Development: Your Name (ABCDEFGH)</CodesignKey>
  <CodesignProvision>My Provisioning Profile</CodesignProvision>
</PropertyGroup>
```

Or in Visual Studio: **Properties → iOS > Bundle Signing** → **Scheme: Manual
Provisioning**, then pick the **Signing identity** and **Provisioning profile**.

### 4.8 Moving identities between machines

Automatic provisioning does **not** remove the need to copy certificates when you use
multiple machines, because the private key exists only where the certificate was created.

- **Mac → Mac:** export the certificate from **Keychain Access** on the origin Mac and
  import it into Keychain Access on the other Mac.
- **Mac → Windows:** export the `.p12` from Keychain Access and import it in Visual Studio
  (**Tools > Options > Xamarin > Apple Accounts → team → View Details… → Import
  Certificate**).
- **Windows → anywhere:** certificates *created by Visual Studio on Windows* are
  **password-protected and cannot be exported/copied**. Create such certificates on the Mac
  instead if you need portability.

If a certificate shows **"Not in Keychain"** in the Visual Studio team details, it must be
exported from the machine that created it and imported as a `.p12`.

### 4.9 Verify on the Mac

```bash
# List code-signing identities visible to the build
security find-identity -v -p codesigning

# List installed provisioning profiles
ls ~/Library/MobileDevice/Provisioning\ Profiles/
```

---

## 5. Part 3 — Install and manage iOS simulators

Simulators run on the Mac and do **not** require certificates or provisioning profiles.

### 5.1 Install simulator runtimes

1. Open **Xcode > Settings > Components** and install the **iOS Simulator** runtime(s) you
   need (each is a multi-GB download). When you first launch Xcode, it may begin installing
   one automatically.
2. Command-line alternative:

```bash
# See what's available and what's installed
xcrun simctl list runtimes
xcrun simctl list devicetypes

# (Optional) Download a specific runtime via Xcode's download mechanism
xcodebuild -downloadPlatform iOS
```

### 5.2 Create, boot, and use simulators

```bash
# List all devices (available + created)
xcrun simctl list devices

# Create a simulator (device type + runtime identifier)
xcrun simctl create "iPhone 17" "com.apple.CoreSimulator.SimDeviceType.iPhone-17" \
  "com.apple.CoreSimulator.SimRuntime.iOS-26-0"

# Boot it and open the Simulator UI
xcrun simctl boot "iPhone 17"
open -a Simulator

# Install a built .app onto a booted simulator
xcrun simctl install booted ./bin/Debug/net10.0-ios/iossimulator-arm64/MauiSmokeTest.app

# Launch it
xcrun simctl launch booted com.companyname.mauismoketest

# Shut down / delete
xcrun simctl shutdown "iPhone 17"
xcrun simctl delete "iPhone 17"
```

Run a MAUI app directly on a simulator from the Mac:

```bash
dotnet build -t:Run -f net10.0-ios -p:_DeviceName=:v2:udid=<SIMULATOR_UDID>
```

Or, in VS Code / Rider, pick the **iOS Simulator** target and press Run/Debug.

> Device-type and runtime identifiers change between Xcode versions. Use
> `xcrun simctl list devicetypes` and `xcrun simctl list runtimes` to get the exact strings
> for your Xcode.

### 5.3 Simulator troubleshooting

If simulators won't boot or behave oddly (a frequent cause of the Windows remote-simulator
boot loop, see [Section 7.6](#76-troubleshooting-pairing-and-remote-simulator)):

```bash
# Quit Xcode first
killall -9 com.apple.CoreSimulator.CoreSimulatorService
rm -rf ~/Library/Developer/CoreSimulator/Devices
xcrun simctl list devices
```

Then recreate simulators in **Xcode > Window > Devices & Simulators > Simulators**.

---

## 6. Part 4 — Make the Mac a build host (pairing target)

Do this on the **MacBook Air M3**. It lets a Windows machine running Visual Studio build
iOS/Mac Catalyst apps by driving this Mac over SSH.

### 6.1 Install the prerequisites on the Mac

- Xcode installed and launched at least once (Section 3.3).
- Xcode command-line tools (`xcode-select --install`).
- **Mono** installed (Section 3.5).
- **Rosetta 2** installed on Apple Silicon (Section 3.4).

Visual Studio will auto-configure most other prerequisites on the Mac when it connects, but
it will **not** install Xcode or Mono for you.

### 6.2 Enable Remote Login (SSH) on the Mac

1. **System Settings > General > Sharing** (older macOS: **System Preferences > Sharing**).
2. Turn on **Remote Login**.
3. Click the **ⓘ** next to Remote Login and:
   - Enable **Allow full disk access for remote users**.
   - Set access to **All users** (or include your Mac username/group in the allowed list).
4. If the macOS firewall blocks incoming connections, allow `mono-sgen` to accept incoming
   connections when prompted (or add it in **Firewall Options**).

### 6.3 Find the Mac's address

```bash
ipconfig getifaddr en0        # Wi-Fi; use en1/en2 if en0 is not your active interface
```

Note the IP address (and/or the Mac's hostname). The Mac and the Windows PC should be on the
**same network/subnet** for automatic discovery. If they're on different subnets, you'll add
the Mac manually by IP.

### 6.4 Understand the SSH key behavior

- On the **first** connection, Pair to Mac generates SSH keys and adds a public key to the
  Mac's `~/.ssh/authorized_keys`; later connections log in without a password.
- On Windows, those keys live in **`%LOCALAPPDATA%\Xamarin\MonoTouch`**.
- **macOS 15.4.1+ caveat:** SSH keys generated against macOS 15.4.1 or later are **not
  compatible with Xamarin.iOS**. If you work on both .NET MAUI and legacy Xamarin.iOS
  projects and use different macOS versions per project, make the initial connection on a
  macOS version **older than 15.4.1** so the key works for both.
- To force regeneration of the SSH key, delete the `%LOCALAPPDATA%\Xamarin\MonoTouch` folder
  on Windows and reconnect.

You are now ready to pair from Windows (Section 7).

---

## 7. Part 5 — Visual Studio on the Windows pairing machine

Do this on the **Windows PC**. It edits code and pairs back to the Mac for iOS builds.

### 7.1 Choose and install Visual Studio

- **Visual Studio 2026** is recommended for .NET 10 MAUI and the current iOS/Xcode
  toolchain. (Visual Studio 2022 **17.12 or greater** also supports .NET MAUI.)
- During install (or via **Visual Studio Installer > Modify**), select the **.NET
  Multi-platform App UI development** workload with its default optional components. This
  installs the MAUI SDK, the Android tooling, and the **remote iOS Simulator for Windows**.

> **Note:** iOS **Hot Restart** (building directly from Windows to a device without a Mac)
> is **not** included in Visual Studio 2026. The **Pair to Mac** workflow is the standard
> approach. If Hot Restart is essential, stay on Visual Studio 2022 (17.3+) for now.

### 7.2 Ensure the .NET 10 SDK + MAUI workload are present

The workload is normally installed by the Visual Studio workload selection. To verify or
install manually:

```powershell
dotnet --version
dotnet workload list
dotnet workload install maui
```

### 7.3 Add your Apple Developer account to Visual Studio

Pairing and provisioning need an Apple **API key**.

1. **Generate an App Store Connect API key (Team Key):**
   - Sign in to `https://appstoreconnect.apple.com`, go to **Users and Access →
     Integrations → Team Keys**, click **+**.
   - Name it, set **Access = Admin** (Admin is required to register Bundle IDs and create
     profiles; Developer keys cannot), click **OK**.
   - Note the **Issuer ID** and **Key ID**, and **download the private key** (`.p8`) to a
     safe location. You can only download it once.
   - (Enterprise Program members generate the key under Apple Developer Account → **Users
     and Access → Integrations** instead.)
2. **Add the account in Visual Studio:** **Tools > Options > Xamarin > Apple Accounts →
   Add**. Provide a name, paste the **Issuer ID** and **Key ID**, and browse to the
   downloaded private key file.

### 7.4 Pair to the Mac

1. Open or create a .NET MAUI project in Visual Studio.
2. Click the **Pair to Mac** button on the iOS toolbar, or use **Tools > iOS > Pair to
   Mac**.
3. The dialog lists previously connected and currently discoverable Macs. Select your
   MacBook Air M3 and click **Connect**.
   - If it isn't listed, click **Add Mac…**, enter the Mac's IP address (from Section 6.3),
     and **Add**.
4. Enter the **Mac's system username and password**. (Use your actual system username, not
   a nickname.)
   - Pair to Mac creates the SSH connection and stores the key in
     `%LOCALAPPDATA%\Xamarin\MonoTouch`; future connections are automatic.
5. Watch the connection status icon — a connected Mac shows a green/connected indicator.
   **Only one Mac can be connected at a time.**
6. Right-click a Mac in the list for **Connect…**, **Forget this Mac**, or **Disconnect**.
   "Forget" removes stored credentials; you'll re-enter them next time.

Visual Studio will auto-install/update required software on the Mac (except Xcode, which
you install manually, and Mono, which you install manually).

### 7.5 Enable auto-connection (optional)

**Tools > Options > Xamarin > iOS Settings → Enable auto connection to known Macs**. After
restarting Visual Studio, it reconnects to known Macs on each launch.

### 7.6 Troubleshooting pairing and remote simulator

- **IDE logs:** `%LOCALAPPDATA%\Xamarin\Logs\17.0` (and `…\18.0` for VS 2026). These contain
  detailed provisioning/pairing errors.
- **Remote simulator logs:** Mac `~/Library/Logs/Xamarin/Simulator.Server`; Windows
  `%LOCALAPPDATA%\Xamarin\Logs\Xamarin.Simulator`.
- **Remote iOS Simulator for Windows:** enabled by default. If disabled, re-enable under
  **Tools > Options > Xamarin > iOS Settings → Remote Simulator to Windows**. With it
  enabled, debugging an iOS simulator app opens a simulator window on Windows; disabled, the
  simulator opens on the Mac instead.
- **Stuck "Connecting to Mac… / Checking Server… / Connected…" loop:** a common Xcode
  configuration problem. Reset simulators on the Mac (Section 5.3):
  ```bash
  # On the Mac (quit XMA and Xcode first)
  rm -rf ~/Library/Developer/CoreSimulator/Devices
  killall -9 com.apple.CoreSimulator.CoreSimulatorService
  xcrun simctl list devices
  ```
  Then recreate simulators in Xcode.
- **"Certificate already exists but cannot be found in the local Keychain":** import the
  `.p12` from the machine that created the certificate (Section 4.8), or revoke and let
  automatic provisioning create a new one.
- **"Authentication Service Is Unavailable":** accept the latest agreements in App Store
  Connect and your Apple Developer account.

### 7.7 Build iOS from the Windows command line

```powershell
dotnet build -f net10.0-ios `
  -p:ServerAddress=<macOS_IP_address> `
  -p:ServerUser=<macOS_username> `
  -p:ServerPassword=<macOS_password> `
  -p:TcpPort=58181 `
  -p:_DotNetRootRemoteDirectory=/Users/<macOS_username>/Library/Caches/Xamarin/XMA/SDKs/dotnet/
```

If `ServerPassword` is omitted, the build uses the saved SSH keys. Note that automatic
remote Mac setup does **not** run for command-line builds — make an initial connection from
Visual Studio first so all prerequisites exist on the Mac.

---

## 8. Part 6 — Create and run your first app

```bash
# On the Mac (or in a Windows terminal with the .NET 10 SDK)
dotnet new maui -n MyMauiApp
cd MyMauiApp
```

**Run on the Mac simulator:**

```bash
dotnet build -t:Run -f net10.0-ios -p:RuntimeIdentifier=iossimulator-arm64
```

**Run on Windows via pairing:** in Visual Studio's **Debug Target** dropdown, choose
**iOS Simulators → \<simulator\>** (or **iOS Remote Devices → \<device\>** for a physical
device attached to the Mac) and press the green **Start** button. Visual Studio builds on
the Mac, starts the remote simulator, and deploys the app.

**Run on Android (Mac):**

```bash
dotnet build -t:Run -f net10.0-android
```

---

## 9. Version compatibility matrix

The single most important rule: **match the Xcode version to your installed iOS/Mac
Catalyst workload.** Each `dotnet/macios` release documents the Xcode version it requires.

| Component | Notes |
| --- | --- |
| .NET 10 SDK | GA 2025-11-11, **LTS** (3 years of support). Check `dotnet --version` (e.g. `10.0.4xx`). |
| MAUI workload | Installed with `dotnet workload install maui`. Keep it in step with the SDK. |
| .NET for iOS / Mac Catalyst workload | Built for **one specific Xcode**. Example: workload `26.5.10318` requires **Xcode 26.6** (needs macOS 26.2+). Newer workload sets (e.g. `10.0.401.1`) add **Xcode 27.0** support. |
| Xcode | Must satisfy the workload's requirement **and** macOS's minimum. Xcode 26.x and 27.x each require specific macOS versions (Tahoe 26.x). |
| macOS | Must meet Xcode's minimum (recent Xcode needs macOS 26.2+). |
| Visual Studio | **2026** recommended; **2022 17.12+** also supported. iOS Hot Restart is absent in VS 2026. |

**Authoritative version sources (check these before installing):**

- .NET MAUI release versions: `https://github.com/dotnet/maui/wiki/Release-Versions`
- .NET for iOS/macOS releases (states the required Xcode): `https://github.com/dotnet/macios/releases`
- Android bindings: `https://github.com/dotnet/android/releases`

**Typical error and fix:**

```
error: This version of .NET for iOS (X) requires Xcode Y.
       The current version of Xcode is Z.
       Either install Xcode Y, or use a different version of .NET for iOS.
```

Fix by installing the required Xcode (via `developer.apple.com/download/all/` + `xcodes`),
**or** by installing a workload version that matches your existing Xcode.

To pin a workload set explicitly:

```bash
sudo dotnet workload install maui --version <workload-set-version>
# or, for the individual Apple workloads:
sudo dotnet workload install ios maccatalyst macos --version <workload-set-version>
```

---

## 10. Troubleshooting appendix

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `dotnet: command not found` | PATH not refreshed | Open a new terminal / restart; check `/usr/local/share/dotnet`. |
| `The current version of Xcode is…` build error | Xcode/workload mismatch | Install the required Xcode or matching workload (Section 9). |
| Xcode won't launch / missing components | Never launched Xcode, or license not accepted | `sudo xcodebuild -runFirstLaunch`; open Xcode and accept. |
| `xcode-select` points at CLT not Xcode | CLT-only path selected | `sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer`. |
| Mac not discoverable when pairing | Remote Login off, wrong subnet, or firewall | Enable Remote Login; same LAN; allow `mono-sgen`; add Mac by IP. |
| Pairing fails on Apple Silicon | Rosetta/Mono missing | `softwareupdate --install-rosetta --agree-to-license`; install Mono. |
| Remote simulator boot loop | Corrupt simulator devices on Mac | Reset simulators (Section 5.3). |
| "Certificate … cannot be found in the local Keychain" | Identity created on another machine | Export/import `.p12` (Section 4.8). |
| "Authentication Service Is Unavailable" | Pending Apple agreements | Accept agreements in App Store Connect + Apple Developer. |
| Can't create a 3rd iOS dev certificate | Apple limit of two | Revoke an existing certificate first. |
| SSH key incompatible (Xamarin.iOS) | macOS 15.4.1+ key format | Make first connection on macOS < 15.4.1; or delete `%LOCALAPPDATA%\Xamarin\MonoTouch` and reconnect. |
| Android emulator slow/won't start | Wrong ABI image | Use `arm64-v8a` system images on Apple Silicon. |
| IDE pairing errors | Need detail | Read `%LOCALAPPDATA%\Xamarin\Logs\17.0` (VS 2022) / `…\18.0` (VS 2026). |

---

## 11. Sources

- Install .NET MAUI tooling — Microsoft Learn:
  `https://learn.microsoft.com/dotnet/maui/get-started/installation?view=net-maui-10.0`
- Pair to Mac for iOS development — Microsoft Learn:
  `https://learn.microsoft.com/dotnet/maui/ios/pair-to-mac?view=net-maui-10.0`
- Remote iOS Simulator for Windows — Microsoft Learn:
  `https://learn.microsoft.com/dotnet/maui/ios/remote-simulator?view=net-maui-10.0`
- Automatic provisioning for iOS apps — Microsoft Learn:
  `https://learn.microsoft.com/dotnet/maui/ios/device-provisioning/automatic-provisioning?view=net-maui-10.0`
- Manual provisioning for iOS apps — Microsoft Learn:
  `https://learn.microsoft.com/dotnet/maui/ios/device-provisioning/manual-provisioning?view=net-maui-10.0`
- iOS capabilities — Microsoft Learn:
  `https://learn.microsoft.com/dotnet/maui/ios/capabilities?view=net-maui-10.0`
- Apple account management — Microsoft Learn:
  `https://learn.microsoft.com/dotnet/maui/ios/apple-account-management?view=net-maui-10.0`
- .NET MAUI release versions (Xcode mapping) — GitHub wiki:
  `https://github.com/dotnet/maui/wiki/Release-Versions`
- .NET for iOS/macOS releases (required Xcode) — GitHub:
  `https://github.com/dotnet/macios/releases`
- .NET 10 download — Microsoft:
  `https://dotnet.microsoft.com/download/dotnet/10.0`

> **Note:** Apple's toolchain (Xcode, macOS) and Microsoft's .NET workloads change
> frequently, and this guide is accurate as of the date it was written. Always confirm the
> current Xcode↔workload pairing in the two GitHub sources above before installing.
