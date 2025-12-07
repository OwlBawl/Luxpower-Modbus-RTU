# Luxpower Modbus RTU Home Assistant Integration

This is a custom component for Home Assistant to integrate Luxpower inverters using Modbus RTU via an RS485-to-USB adapter.

## Installation

### HACS (Recommended)

1.  This integration is not in the default HACS repository yet. You can add it as a custom repository.
2.  Go to HACS -> Integrations -> Click the 3 dots in the top right -> Custom repositories.
3.  Add the URL to this repository and select `Integration` as the category.
4.  Click `ADD`. You should now see "Luxpower Modbus RTU" in your HACS integrations list.
5.  Click `INSTALL` and follow the instructions.
6.  Restart Home Assistant.

### Manual Installation

1.  Copy the `custom_components/luxpower_modbus` directory to your Home Assistant `custom_components` directory.
2.  Restart Home Assistant.

## Configuration

1.  Go to Settings -> Devices & Services -> Add Integration.
2.  Search for "Luxpower Modbus RTU" and click on it.
3.  Follow the on-screen instructions to configure the integration:
    -   **Serial Port**: The path to your RS485-to-USB adapter (e.g., `/dev/ttyUSB0`).
    -   **Slave ID**: The Modbus slave ID of your inverter (usually `1`).
    -   **Baud Rate**: The communication speed (usually `9600`).
    -   **Polling Interval**: How often to poll the inverter for data in seconds.

## Customization

To add or change sensors and controls, you need to edit the entity descriptions in `custom_components/luxpower_modbus/const.py`. You will need the Modbus register map for your specific Luxpower inverter model.

## Recommended VS Code Extensions

To improve your development workflow, this repository includes a list of recommended extensions in the `.vscode/extensions.json` file. When you open this project in VS Code, you should be prompted to install them.

-   **[GitHub Pull Requests and Issues](https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-pull-request-github)**: Allows you to review and manage GitHub pull requests and issues directly within VS Code. This is essential for collaborating and preparing for a release.
-   **[GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)**: Supercharges the Git capabilities built into VS Code. It helps you visualize code authorship with Git blame annotations, navigate repositories seamlessly, and gain powerful comparison commands. This is invaluable for understanding the history of changes before creating a release.

These extensions work alongside the release task we created, providing a more integrated and powerful development experience.

## Developer Workflow: Creating a Release

This repository is set up with an automated release workflow for VS Code.

### Prerequisites

1.  **Node.js**: [Install Node.js](https://nodejs.org/).
2.  **GitHub CLI**: [Install the GitHub CLI](https://cli.github.com/).
3.  **Authenticate**: Log in to the GitHub CLI with `gh auth login`.
4.  **Install dependencies**: Run `npm install` in the root of the repository.

### How to Create a Release

1.  Ensure all your code changes are committed to the `main` (or `master`) branch.
2.  Open the Command Palette in VS Code (`Ctrl+Shift+P` or `Cmd+Shift+P`).
3.  Type `Tasks: Run Task` and select it.
4.  Choose the `Create Release` task.
5.  You will be prompted to select the version bump type (`patch`, `minor`, or `major`). Select one.
6.  The script will automatically:
    -   Increase the version number in `custom_components/luxpower_modbus/manifest.json`.
    -   Commit the version change.
    -   Create and push a new Git tag.
    -   Create a new GitHub Release with auto-generated release notes based on your recent commits.
