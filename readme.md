<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

<img src="readmeai/assets/logos/purple.svg" width="30%" style="position: relative; top: 0; right: 0;" alt="Project Logo"/>

# <code>❯ REPLACE-ME</code>

<em>Seamless Face Recognition, Organized for You</em>

<!-- BADGES -->
<!-- local repository, no metadata badges. -->

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/scikitlearn-F7931E.svg?style=default&logo=scikit-learn&logoColor=white" alt="scikitlearn">
<img src="https://img.shields.io/badge/NumPy-013243.svg?style=default&logo=NumPy&logoColor=white" alt="NumPy">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=default&logo=Python&logoColor=white" alt="Python">

</div>
<br>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
    - [Project Index](#project-index)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview



---

## Features

<code>❯ REPLACE-ME</code>

---

## Project Structure

```sh
└── /
    ├── FaceSort.py
    ├── QT-Ui
    │   └── Main.ui
    ├── build.py
    ├── main_tab
    │   ├── __pycache__
    │   ├── a_ordner_auswählen.py
    │   ├── b_gesicht_erkennung.py
    │   ├── c_unter_tab
    │   ├── d_export.py
    │   └── g_settings.py
    ├── make-reports
    │   ├── 1_analyze_nuitka_report.py
    │   ├── 2_compare_imports.py
    ├── make_installer.py
    ├── project.env
    ├── readme-ai.md
    ├── requirements.txt
    └── src
        ├── DBManager.py
        ├── __pycache__
        ├── add_button_and_pcitures_in_two_widgets.py
        ├── add_picture_to_widget_clas.py
        ├── custom_logging.py
        ├── g_db_settings_handler.py
        ├── get_picture_metadata.py
        ├── nachrichten_clas.py
        ├── progressbar_clas.py
        ├── resource_path.py
        └── version.py
```

### Project Index

<details open>
	<summary><b><code>/</code></b></summary>
	<!-- __root__ Submodule -->
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/FaceSort.py'>FaceSort.py</a></b></td>
					<td style='padding: 8px;'>- Orchestrates the main application window, managing UI interactions, process initiation, and update checks<br>- Serves as the entry point for face recognition, folder selection, and settings integration, coordinating modular components to enable seamless user workflow and system functionality.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/make_installer.py'>make_installer.py</a></b></td>
					<td style='padding: 8px;'>- Generates platform-specific installers for Linux AppImage and Windows, integrating versioning from the projects version module<br>- Orchestrates the creation of distribution packages by leveraging build artifacts from the Nuitka compiler, ensuring cross-platform deployment readiness within the projects release workflow.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/requirements.txt'>requirements.txt</a></b></td>
					<td style='padding: 8px;'>- Defines required third-party libraries to enable core features like facial recognition, real-time processing, and GUI interactions<br>- These dependencies ensure consistent runtime environments across development, testing, and deployment stages.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/build.py'>build.py</a></b></td>
					<td style='padding: 8px;'>- Compiles the main application into cross-platform standalone executables using Nuitka, integrating UI assets and dependencies<br>- Manages OS-specific build flags, caching, and logging to ensure consistent, reproducible distributions across Windows and Linux<br>- Centralizes build configuration and execution logic for the project.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- QT-Ui Submodule -->
	<details>
		<summary><b>QT-Ui</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ QT-Ui</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/QT-Ui/Main.ui'>Main.ui</a></b></td>
					<td style='padding: 8px;'>- This file defines the main application windows user interface layout, establishing the foundational structure for user interaction<br>- It sets up the primary window's dimensions, styling (dark theme with light text), and includes a critical exit button for terminating the application<br>- As part of the UI layer, it ensures a consistent visual design and provides the entry point for all user-facing controls, aligning with the project's architecture of separating presentation logic from business logic.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- src Submodule -->
	<details>
		<summary><b>src</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ src</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/src/progressbar_clas.py'>progressbar_clas.py</a></b></td>
					<td style='padding: 8px;'>- Manages UI feedback during processes by updating a progress bar and displaying completion messages<br>- It integrates with the applications UI components to track progress and signal task completion<br>- This ensures users receive clear status updates throughout operations.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/src/add_button_and_pcitures_in_two_widgets.py'>add_button_and_pcitures_in_two_widgets.py</a></b></td>
					<td style='padding: 8px;'>- Manages UI elements for displaying person data, linking buttons to image loading and main image display<br>- Integrates with the database to fetch and show faces, coordinating between UI components and data retrieval to present person information effectively.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/src/add_picture_to_widget_clas.py'>add_picture_to_widget_clas.py</a></b></td>
					<td style='padding: 8px;'>- Manages image display in the UI, integrating with the database to show full images or face crops<br>- Handles user interactions, updates progress indicators, and logs errors during image loading and rendering.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/src/g_db_settings_handler.py'>g_db_settings_handler.py</a></b></td>
					<td style='padding: 8px;'>- Manages persistent application settings via SQLite, ensuring configuration data is loaded or created on initialization<br>- Provides controlled access to critical parameters like database paths, folder locations, and operational modes, while maintaining data integrity and logging changes<br>- Serves as the database interaction layer for configuration management.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/src/nachrichten_clas.py'>nachrichten_clas.py</a></b></td>
					<td style='padding: 8px;'>- Manages status messages and errors within the applications UI framework<br>- Integrates logging with a text widget to display alerts, ensuring visual feedback aligns with the logging system<br>- The widget serves as a centralized hub for conveying messages to users, maintaining consistency across the applications interface.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/src/DBManager.py'>DBManager.py</a></b></td>
					<td style='padding: 8px;'>- Manages facial recognition data storage and relationships, handling image-face associations, person merging, and query operations<br>- Defines database models and provides methods for adding, retrieving, and organizing facial data, ensuring structured access to images, faces, and person assignments within the projects architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/src/get_picture_metadata.py'>get_picture_metadata.py</a></b></td>
					<td style='padding: 8px;'>- Extracts metadata from image files, gathering timestamps and geographic coordinates<br>- Focuses on reliable extraction of date fields and GPS data, ensuring robust handling of missing or malformed information<br>- Integrates with the projects data processing pipeline to enrich image records with contextual details.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/src/custom_logging.py'>custom_logging.py</a></b></td>
					<td style='padding: 8px;'>- Configures custom logging for the application, defining unique levels and formatters for console and file outputs<br>- Manages log rotation, ensures structured formatting, and maintains recent log files while removing outdated entries<br>- Centralizes logging setup to unify message handling across the codebase.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/src/version.py'>version.py</a></b></td>
					<td style='padding: 8px;'>- Provides the current version string used across the codebase, sourced from the project.env file in the root directory<br>- Serves as a centralized point for version retrieval, ensuring consistency and fallback to a default value when the file is missing.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/src/resource_path.py'>resource_path.py</a></b></td>
					<td style='padding: 8px;'>- Resolves UI resource paths across development and standalone environments<br>- Ensures correct file location retrieval whether bundled with PyInstaller, Nuitka, or run directly<br>- Supports seamless resource loading for the applications interface.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- make-reports Submodule -->
	<details>
		<summary><b>make-reports</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ make-reports</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/make-reports/1_analyze_nuitka_report.py'>1_analyze_nuitka_report.py</a></b></td>
					<td style='padding: 8px;'>- Generates a clean list of top modules from Nuitkas XML report, extracting and counting module names for downstream analysis<br>- Serves as a preprocessing step in the build pipeline to prepare structured module usage data for reporting or optimization tasks.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/make-reports/2_compare_imports.py'>2_compare_imports.py</a></b></td>
					<td style='padding: 8px;'>- Generates nofollow suggestions by comparing import sets across platforms<br>- Identifies unused imports in Nuitka builds not present in runtime dependencies<br>- Excludes specified modules from recommendations<br>- Outputs results to nofollow_suggestions.txt for build optimization.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- main_tab Submodule -->
	<details>
		<summary><b>main_tab</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ main_tab</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/main_tab/d_export.py'>d_export.py</a></b></td>
					<td style='padding: 8px;'>- Manages export operations by coordinating user selections, database queries, and file copying<br>- It enables exporting images filtered by selected persons, handles destination selection, and ensures data consistency between UI and storage<br>- Central to facilitating controlled data export within the applications workflow.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/main_tab/a_ordner_auswählen.py'>a_ordner_auswählen.py</a></b></td>
					<td style='padding: 8px;'>- Handles folder selection and coordinates image processing workflows<br>- Integrates with database operations to manage image storage and retrieval<br>- Manages UI interactions for folder navigation, image renaming, and progress tracking<br>- Ensures seamless data flow between user input, file system, and persistent storage<br>- Central to organizing and displaying visual data within the application.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/main_tab/g_settings.py'>g_settings.py</a></b></td>
					<td style='padding: 8px;'>- Initializes a database for storing and retrieving application settings<br>- Defines a model to persist configuration parameters like mode and thread count<br>- Loads default values on startup, ensuring consistent access to runtime configuration across the application<br>- Integrates with the logging system for operational visibility.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/main_tab/b_gesicht_erkennung.py'>b_gesicht_erkennung.py</a></b></td>
					<td style='padding: 8px;'>- Processes images for face recognition, integrating with the database and settings to detect and save facial data<br>- Updates the UI in real-time, handles model loading, and ensures efficient processing while logging errors and progress.</td>
				</tr>
			</table>
			<!-- c_unter_tab Submodule -->
			<details>
				<summary><b>c_unter_tab</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ main_tab.c_unter_tab</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/main_tab/c_unter_tab/benenen.py'>benenen.py</a></b></td>
							<td style='padding: 8px;'>- Manages person name renames in the database, synchronizing UI updates with persistent storage<br>- Integrates user input validation, real-time data reflection, and error handling to ensure consistent state between interface and backend<br>- Central to maintaining accurate identity mappings across the applications data flow.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/main_tab/c_unter_tab/start_personen_scan.py'>start_personen_scan.py</a></b></td>
							<td style='padding: 8px;'>- Clusters detected faces into groups using similarity metrics, matches these groups to existing person entries or creates new ones, and updates the UI to reflect assignments<br>- Streamlines face-to-person mapping for efficient database organization and user feedback.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/main_tab/c_unter_tab/zusammenfuegen.py'>zusammenfuegen.py</a></b></td>
							<td style='padding: 8px;'>- Merges person data from a database into UI widgets, enabling side-by-side comparison and consolidation<br>- Loads buttons and images for left/right sections, updates UI after merging, and synchronizes state across components<br>- Central to integrating database records with visual interfaces for data reconciliation.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/main_tab/c_unter_tab/hauptbild_aendern.py'>hauptbild_aendern.py</a></b></td>
							<td style='padding: 8px;'>- Manages setting and updating main images for individuals by integrating database operations with UI components<br>- Coordinates folder paths, person data, and image selections to apply changes across the applications interface<br>- Ensures consistent state updates and error handling for user interactions.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/main_tab/c_unter_tab/personen_loeschen.py'>personen_loeschen.py</a></b></td>
							<td style='padding: 8px;'>- Enables deletion of persons via UI buttons, integrating with the database to load and refresh options<br>- Manages real-time updates and error handling for a seamless user experience.</td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---

## Getting Started

### Prerequisites

This project requires the following dependencies:

- **Programming Language:** Python
- **Package Manager:** Pip

### Installation

Build  from the source and intsall dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone https://codeberg.org/beginner2026/FaceSort.git
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd FaceSort
    ```

3. **Install the dependencies:**

<!-- SHIELDS BADGE CURRENTLY DISABLED -->

	```sh
	pip install -r requirements.txt
	```

### Usage

Run the project with:

**Using [pip](https://pypi.org/project/pip/):**
```sh
python FaceSort.py
```

---

## Contributing

- **💬 [Join the Discussions](https://LOCAL///discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://LOCAL///issues)**: Submit bugs found or log feature requests for the `` project.
- **💡 [Submit Pull Requests](https://LOCAL///blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your LOCAL account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone .
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to LOCAL**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>

---

## License

 is protected under the [PolyForm Noncommercial License 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0) License. For more details, refer to the [LICENSE](LICENSE.txt) file.

---

## Acknowledgments

- Credit `contributors`, `inspiration`, `references`, etc.

<div align="right">

[![][back-to-top]](#top)

</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square


---
