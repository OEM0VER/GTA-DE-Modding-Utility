![alt text](https://i.ibb.co/zh1Q60wM/Screenshot-2026-09-20-215854.png)

# GTA DE Modding Utility

A comprehensive modding toolkit for **Grand Theft Auto: The Trilogy – The Definitive Edition**, bringing together tools for repairing models, editing vehicles, working with materials and textures, managing `.pak` files, localization, and other Unreal Engine assets.

# **Key features include:**

- **Model Repair:**
  - Fixes `.uasset` / `.uexp` files affected by serialization errors using [Hypermodule’s MeshAibRemover](https://github.com/hypermodule/MeshAibRemover), powered by [CUE4Parse](https://github.com/FabianFG/CUE4Parse).
  - Supports fixing multiple models at once for faster workflows.

- **Vehicle Tools:**
  - Transfer vehicle lighting data from original GTA Trilogy DE vehicles to custom models.
  - Edit vehicle light material-slot indices.
  - Edit wheel mesh references.
  - Transfer and edit various vehicle properties.
  - Edit siren material-slot indices.
  - View and inspect material slots and mesh sections.

- **PAK Management:**
  - Drag a **folder** → creates an uncompressed `.pak` file.
  - Create compressed `.pak` files.
  - Drag a **.pak file** → unpacks its contents.
  - Files are automatically organized based on the operation being performed.

- **Asset & Material Tools:**
  - Inspect and edit Unreal Engine asset data.
  - Create and edit GTA Trilogy DE materials.
  - Work with material instances and material properties.
  - Create game materials for custom assets.
  - Inspect and edit mesh-related asset data.

- **Color & Texture Tools:**
  - Pick colors directly from images.
  - Get RGB color values.
  - Convert RGB and HEX values to Unreal Engine-compatible decimal/float values.
  - Utilities for working with GTA Trilogy DE textures and materials.

- **Automatic Setup:**
  - Downloads required resources on first launch where needed (500MB of free space needed!).
  - Helps ensure required tools and dependencies are available without complicated manual setup.

- **User-Friendly Interface:**
  - Dark-themed interface designed for long modding sessions.
  - Custom fonts, hover effects and organised tool sections.
  - Integrated links to useful resources, tutorials and documentation.

- **Persistent Window Position:**
  - Remembers the last screen and position the application was opened on.
  - Supports multiple monitor setups and different display resolutions.

- **Integrated Tools & Shortcuts:**
  - Quickly launch commonly used modding tools directly from the application.
  - Create a desktop shortcut for faster access.
  - Access helpful links and tutorials directly from the **Tools** and **Help** menus.

Designed to assist both modders and developers, **GTA DE Modding Utility** brings commonly used GTA Trilogy DE modding tools and workflows together into one application, making asset editing, repair, conversion and packaging easier and more efficient.

## Credits

This project would not be possible without the amazing work of others:

- **[Hypermodule’s MeshAibRemover](https://github.com/hypermodule/MeshAibRemover)** – Provides the core functionality for repairing affected Unreal Engine models.
- **[CUE4Parse](https://github.com/FabianFG/CUE4Parse)** – A powerful Unreal Engine asset parser used by the model repair tools.
- **[UAssetGUI](https://github.com/atenfyr/UAssetGUI)** – A powerful Unreal Engine asset editor used for inspecting and editing `.uasset` files.
- **[UnrealPak](https://github.com/xamarth/unrealpak)** – Used for packing and unpacking `.pak` files.

Special thanks to their developers for making these tools available to the community 👏
