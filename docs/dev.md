# Development

## Option 1: Running the Home Assistant with VSCode devcontainer

This is a recommended approach by Home Assistant, but feels a bit buggy at the moment.

1. Install `ms-vscode-remote.remote-containers` VSCode plugin.
2. Restart VSCode and click `Reopen in Container` on bottom right.
3. Wait few moments to finish the setup and open the command palette, search for `Tasks: Run Task` and select `Run the mock API server`. This will start the mock go-e REST API.
4. Open the command palette again, search for `Tasks: Run Task` and select `Run Home Assistant on port 9123`. This will start the Home Assistant with the custom component on port `9123`.
5. Open the <http://127.0.0.1:9123> in a browser.
6. Create an account. __This feels quite buggy at the moment and you have to refresh the browser several times.__
7. You should see bunch of auto-created cards on the dashboard.

If you change the code, you'll have to restart the task `Run Home Assistant on port 9123` by running `Tasks: Restart Running Task` from the command palette.

Known issues:

- `/bin/bash: line 1: container: command not found` - try to rebuild the container
- `[59923 ms] postCreateCommand failed with exit code 2. Skipping any further user-provided commands.` - same as above, try to rebuild the container
- there are issues with zeroconf installation which leads to some subsequent errors - this is probably caused by the fact that the `ghcr.io/ludeeus/devcontainer/integration:stable` image is just too old

## Option 2: Running the Home Assistant with custom script

If you have issues running VSCode `devcontainer`, there is a script to achieve live reloads of the custom component in the running Docker container.

Run:

```bash
./start-dev.sh
```

After few minutes, Home Assistant should be running and script should be in the watch mode. Whenever you change a file in the `custom_components/smartenergy_goecharger` folder, it will restart the Home Assistant within a few seconds. Thus, you have a quick development feedback.

1. Open the <http://127.0.0.1:8123> in a browser.
2. Create an account.
3. You should see bunch of auto-created cards on the dashboard.
4. Continue with the chapter [Working with virtual env](#working-with-virtual-env) and below to test all the dev capabilities. 

## Option 3: Running the Home Assistant with HACS

In case you want to try HACS locally, run:

```
./start-local.sh
```

1. Open the <http://127.0.0.1:8123> in a browser.
2. Create an account - make sure that timezone is set correctly, otherwise it will fail to connect to the Github.
3. Go to Settings -> Integrations and click on the `ADD INTEGRATION`.
4. Search for `HACS` and go through the process.
5. In the left menu you should have HACS icon, click it.
6. Click on `Integrations` -> click 3 dots top right corner -> click `Custom repositories`.
7. In the dialog window, add `https://github.com/openkfw/smartenergy.goecharger` as a repository and select `Integration` as a category.
8. Click `ADD`, wait for spinner to finish and close the dialog.
9. Click `EXPLORE & DOWNLOAD REPOSITORIES` -> search for `go-e` -> select the `go-e Charger Cloud` -> wait and click `DOWNLOAD`.
10. Go to Settings -> System -> click `RESTART` and wait few seconds.
11. Go to Settings -> Devices & Services. Click the `ADD INTEGRATION` button.
12. Search for `go-e Charger Cloud` -> click -> fill in details -> click `SUBMIT`.

Example config:

![example config](./ha-example-config.png)

> Make sure that there is no trailing slash in the API host, otherwise the validation fails. When pressing submit, validation will also check the connectivity and fails if not able to connect and authenticate.

11. Go to the dashboard screen, you should see bunch of sensors for the go-e Charger Cloud integration.

## Working with virtual env

It is highly recommended to work from within a virtual environment as especially dependencies can mess up quite easily.

Create:

```bash
python3 -m venv env
```

Activate:

```bash
source env/bin/activate
```

Deactivate:

```bash
deactivate
```

## Install required pip packages

```bash
python3 -m pip install -r requirements.txt
pre-commit install -t pre-push
```

## Uninstall all pip packages

In case you need to refresh your virtual environment, you can uninstall everything and the install again from scratch:

```bash
pip freeze | xargs pip uninstall -y
```

## Linting

Linting is done via [Pylint](https://www.pylint.org/).

```bash
python3 -m pylint tests/**/*.py custom_components/**/*.py mock_api/**/*.py
```

## Formatting

Formatting is done via [Black](https://black.readthedocs.io/en/stable/getting_started.html).

```
black custom_components/smartenergy_goecharger
```

To have autoformatting in the VSCode, install the extension `ms-python.black-formatter`.

## Unit testing

Unit testing is done via [Pytest](https://docs.pytest.org/en/7.2.x/).

```bash
python3 -m pytest

# show logs
python3 -m pytest -o log_cli=true

# code coverage
python3 -m pytest --durations=10 --cov-report term-missing --cov=custom_components.smartenergy_goecharger tests
```

> __Note: In case you have issues with bcrypt circular import, run this:__

```bash
python3 -m pip uninstall bcrypt -y && python3 -m pip install bcrypt
```
