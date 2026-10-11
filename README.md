# Gym Management DevOps Pipeline

This practical builds a small Flask membership API and demonstrates the flow:

**Jira → GitHub → Jenkins/GitHub Actions → pytest → Docker → Trivy → Ansible/Docker Compose**

## API

- `GET /health` — container and service health check
- `GET /api/members` — list in-memory members
- `POST /api/members` — add a member with `name` and `email`
- `GET /api/members/<id>` — retrieve a member by ID

Memberships are held in memory for this pipeline demonstration; they reset when
the application restarts. Do not use this sample as a production member database.

## Run the tests

From this directory, create a virtual environment and install the development
dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

If PowerShell blocks activation, run the tools directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

## Build and run with Docker

Start Docker Desktop, then run:

```powershell
docker compose up --build -d
docker compose ps
curl.exe http://localhost:8088/health
Invoke-RestMethod -Method Post -Uri 'http://localhost:8088/api/members' -ContentType 'application/json' -Body (@{name='Asha Patel';email='asha@example.com'} | ConvertTo-Json)
docker compose down
```

## CI and deployment

- `.github/workflows/ci.yml` runs tests, builds the container, and fails on
  fixable CRITICAL or HIGH Trivy findings for pushes and pull requests to `main`.
- `Jenkinsfile` runs the same test/build/scan gates and deploys with Compose.
  Configure a Jenkins Linux agent with Python 3, Docker Compose, and Trivy.
- `deploy.yml` runs the local Compose deployment using Ansible:

  ```powershell
  ansible-playbook deploy.yml
  ```

For a local Trivy scan after building the image, run:

```powershell
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.75.0 image --pkg-types os --exit-code 1 --severity CRITICAL,HIGH --ignore-unfixed gym-management-api:local
$projectPath = (Get-Location).Path
docker run --rm -v "${projectPath}:/src" aquasec/trivy:0.75.0 fs --scanners vuln --pkg-types library --exit-code 1 --severity CRITICAL,HIGH --ignore-unfixed /src/requirements.txt
```

The two scans keep operating-system packages and the application's declared
Python dependencies distinct. The upstream Python image SBOM can list unrelated
Python packages that are not installed in this runtime image, so the pipeline
does not treat those SBOM-only entries as application dependencies.

To publish the local image to Docker Hub, sign in interactively and push a tag:

```powershell
docker login
docker tag gym-management-api:local YOUR_DOCKERHUB_USERNAME/gym-management-api:1.0
docker push YOUR_DOCKERHUB_USERNAME/gym-management-api:1.0
```

For a GitHub Actions demonstration, push this directory as a GitHub repository
and capture the completed Actions run. The workflow tests, builds, scans, then
deploys to the temporary GitHub runner with Ansible. For Jenkins, create a
Pipeline job pointing at the repository and configure Python 3, Docker Compose,
and Trivy on its Linux agent. Store any registry or cloud credentials in the
CI secret store; never commit them.

## Jira evidence

Create a Jira project named **Gym Management DevOps** and track work such as:
API implementation, automated tests, containerization, CI/security scanning,
and deployment automation. Capture the project board with the tasks visible.

## Suggested evidence screenshots

Capture the Jira board; GitHub repository and workflow run; passing local test
output; Docker image/build and running container; the Trivy scan result; and
Ansible deployment plus the `/health` response. Use your own signed-in accounts
for screenshots and redact personal tokens or credentials.
