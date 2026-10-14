# 🤌 FUGGEDABOUTIT SENSE 🇺🇸📡

### *What exit? We already know where ya at!*

**A Garden State-flavored Meshtastic network monitor.** Ayyy, how ya doin'? Watch your nodes, check signal reports, map the neighborhood, and run traceroutes — without taking a wrong turn at the jughandle.

> **Status: work in progress.** This is a community fork of [Affirmatech MeshSense](https://github.com/Affirmatech/MeshSense). The Jersey branding and Intel build automation are in progress; the Intel macOS app has **not** yet been successfully built, signed, notarized, or verified on Tahoe 26.7.1.

## 🍕 What's cookin'?

- 📡 **Da Neighborhood:** View Meshtastic nodes and their network health.
- 🗺️ **What Exit?:** Map your mesh network.
- 📶 **How Ya Doin'?:** Inspect signals and network activity.
- 🚗 **The Jersey Slide:** Follow traceroutes and connection paths.
- 🤌 **Fuggedaboutit!:** A dark Garden State green, Jersey gold, and Turnpike asphalt look.

The Jersey names are branding ideas; existing functionality is inherited from upstream and individual screen labels may still be updated.

## 🍎 Intel Mac — click to open

The target is a normal **Fuggedaboutit Sense.app** for Intel Macs, distributed in a **DMG**. Once a working release is available, drag the app into Applications and open it from Finder. **There is no tested DMG download yet. A GitHub Actions workflow now attempts to build an unsigned Intel DMG and stores it as a workflow artifact.** macOS signing/notarization and Bluetooth permissions still need verification.

For developers, the Electron package includes an Intel macOS build script:

```sh
cd electron
npm run build:mac:intel
```

The project dependencies and bundled API must be prepared first, as described below. Running this command is not a guarantee that the current fork builds successfully.

## 🚦 Builds and releases\n\nThe [Intel Mac workflow](https://github.com/BaconDisk22/FUGGEDABOUTIT-SENSE/actions/workflows/intel-mac.yml) builds the UI, API and Electron app on an Intel macOS runner, generates an original Garden State app icon, and uploads a DMG if the build succeeds. It can be started manually using **Run workflow** once merged to the default branch. A push of a `v*` tag triggers an attempt to publish the DMG in GitHub Releases. The unsigned build may require additional macOS Gatekeeper steps; no signing or notarization is configured yet.\n\nVersion numbering currently follows the Electron package version; release tags should match the packaged version. Automated update delivery is **not** configured for GitHub Releases yet.\n\n## 🎨 Garden State colors

| Flavor | Color |
| --- | --- |
| Garden State Green | `#006747` |
| Jersey Gold | `#F2B134` |
| Turnpike Asphalt | `#15191D` |
| Diner Booth Charcoal | `#252B30` |
| Tail Light Red | `#D62828` |

## 🛠️ Under da hood — development

Clone **this fork**, including its submodules:

```sh
git clone --recurse-submodules https://github.com/BaconDisk22/FUGGEDABOUTIT-SENSE.git
cd MeshSense
```

Build the `webbluetooth` dependency (Debian may require `cmake` and `libdbus-1-dev`):

```sh
cd api/webbluetooth
npm install
npm run build:all
cd ../..
```

The upstream `update.mjs` script installs and updates the UI, API, and Electron dependencies:

```sh
./update.mjs
```

To run the development UI:

```sh
cd ui
PORT=5921 npm run dev
```

In another terminal, run the API:

```sh
cd api
DEV_UI_URL=http://localhost:5921 PORT=5920 npm run dev
```

Open the API-served interface at `http://localhost:5920/`. The `PORT` and `DEV_UI_URL` values can also be configured through `.env` files.

To build deployable components, consult `build.mjs`; outputs are placed under `api/dist` and `electron/dist`. On some systems, UI hot reload can duplicate state subscriptions; refreshing the browser resets them.

## 🖥️ Headless mode

The inherited MeshSense API supports `--headless`, with optional `ACCESS_KEY` for privileged remote access. Example for an upstream Linux AppImage:

```sh
export ADDRESS=10.0.1.20
export PORT=5920
ACCESS_KEY=mySecretKey ./meshsense-x86_64.AppImage --headless
```

On Debian/Ubuntu/Raspberry Pi OS, AppImages may require `libfuse2`. For upstream headless and Bluetooth guidance, see the [MeshSense FAQ](https://affirmatech.com/meshsense/faq) and [Bluetooth tips](https://affirmatech.com/meshsense/bluetooth).

## 🤝 Respect da family

This project is a fork of **[Affirmatech/MeshSense](https://github.com/Affirmatech/MeshSense)**. Original code and upstream authorship remain credited. Review the repository's license and preserve all applicable notices. This Jersey-themed fork is not an official Meshtastic product.

---

**Made with Garden State attitude. No tolls required.** 🍕🤌
