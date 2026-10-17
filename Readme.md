# Multi AI Agent

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)
![Streamlit](https://img.shields.io/badge/frontend-Streamlit-FF4B4B)
![Docker](https://img.shields.io/badge/container-Docker-2496ED)
![CI/CD](https://img.shields.io/badge/CI%2FCD-Jenkins-D24939)
![Cloud](https://img.shields.io/badge/deploy-AWS%20ECS%20Fargate-FF9900)

A chat application powered by an AI agent. You choose a model, write a persona
for the agent, and ask anything. The agent can also search the web when you turn
web search on.

The project is built end to end: agent code, REST API, web interface, Docker
image, and a full CI/CD pipeline that scans, builds, and deploys the app to AWS
by itself.

---

## Table of Contents

1. [Features](#features)
2. [How It Works](#how-it-works)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Prerequisites](#prerequisites)
6. [Quick Start (Local)](#quick-start-local)
7. [Configuration](#configuration)
8. [API Reference](#api-reference)
9. [Run with Docker](#run-with-docker)
10. [CI/CD Pipeline](#cicd-pipeline)
11. [Deploy to AWS](#deploy-to-aws)
12. [Security](#security)
13. [Troubleshooting](#troubleshooting)
14. [Cost and Cleanup](#cost-and-cleanup)
15. [Known Limitations and Roadmap](#known-limitations-and-roadmap)
16. [Contributing](#contributing)
17. [License](#license)

---

## Features

- **Choice of models.** Pick from the models allowed in the configuration file.
- **Custom persona.** Write a system prompt to change how the agent behaves.
- **Optional web search.** The agent uses Tavily search only when you allow it.
- **Optional conversation context.** Send earlier questions together with the new one.
- **Clear errors.** Errors from the backend show the file name and line number, and the interface shows the details in an "Error details" box.
- **Logging.** Every request and error is written to the screen and to a daily log file.
- **One-command start.** `python -m app.main` starts the backend and the frontend together.
- **Container ready.** A single Docker image holds the whole app.
- **Automatic pipeline.** Jenkins clones the code, scans it with SonarQube, pushes the image to AWS ECR, and deploys it to AWS ECS Fargate.

---

## How It Works

A request travels in this order:

1. You type a question in the Streamlit page (port `8501`).
2. Streamlit sends the question to the FastAPI backend (port `9999`).
3. The backend checks the request and calls the agent function.
4. The agent calls the Groq model. If web search is on, it can also call Tavily.
5. The answer goes back to the backend, then to the page.

Inside one container, both programs run together. The backend listens on
`127.0.0.1:9999`, which means only the frontend in the same container can reach
it. Only port `8501` is meant to be opened to users.

Deployment flow:

1. You push code to GitHub.
2. Jenkins pulls the code.
3. SonarQube scans the code.
4. Jenkins builds the Docker image and pushes it to AWS ECR.
5. Jenkins tells AWS ECS to start a new task with the new image.

---

## Tech Stack

| Area | Tool |
|---|---|
| Language | Python 3.12 |
| Environment | uv |
| LLM provider | Groq |
| Web search | Tavily |
| Agent framework | LangChain, LangGraph |
| Backend | FastAPI, Uvicorn |
| Frontend | Streamlit |
| Container | Docker |
| CI/CD | Jenkins |
| Code quality | SonarQube |
| Image registry | AWS ECR |
| Runtime | AWS ECS Fargate |
| Secrets | AWS Secrets Manager |

---

## Project Structure

```
multi_ai_agent/
├── app/
│   ├── main.py                  # starts backend and frontend together
│   ├── backend/
│   │   └── api.py               # FastAPI app: /health and /chat
│   ├── frontend/
│   │   └── ui.py                # Streamlit interface
│   ├── core/
│   │   └── ai_agent.py          # the agent (Groq model + Tavily search)
│   ├── config/
│   │   └── settings.py          # environment variables and allowed models
│   └── common/
│       ├── logger.py            # logging setup
│       └── custom_exception.py  # errors with file name and line number
├── custom_jenkins/
│   └── Dockerfile               # Jenkins image with Docker and AWS CLI
├── Dockerfile                   # image of the app
├── Jenkinsfile                  # CI/CD pipeline
├── requirements.txt
├── setup.py
├── .env                         # your secret keys (never commit this file)
├── .dockerignore
└── .gitignore
```

---

## Prerequisites

- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- Git
- A [Groq](https://console.groq.com/keys) API key
- A [Tavily](https://app.tavily.com) API key
- Docker (on Windows, use WSL with Ubuntu)

For the CI/CD and cloud parts you also need:

- Jenkins and SonarQube (the steps below run them as containers)
- A GitHub account and a personal access token
- An AWS account

---

## Quick Start (Local)

**1. Clone the project**

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

**2. Create the environment and install the libraries**

```bash
uv venv --python 3.12
```

Activate it:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# Linux, macOS, or WSL
source .venv/bin/activate
```

Install:

```bash
uv pip install -r requirements.txt
uv pip install -e .
```

**3. Add your keys**

Create a file named `.env` in the project root (see [Configuration](#configuration)).

**4. Start the app**

```bash
python -m app.main
```

**5. Open it**

Go to `http://localhost:8501`.

To run the two parts in separate terminals instead:

```bash
uvicorn app.backend.api:app --host 127.0.0.1 --port 9999
python -m streamlit run app/frontend/ui.py
```

---

## Configuration

### Environment variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Key for the Groq model. It starts with `gsk_`. |
| `TAVILY_API_KEY` | Yes, for web search | Key for Tavily search. It starts with `tvly-`. |
| `API_URL` | No | Address of the backend used by the frontend. Default: `http://127.0.0.1:9999/chat` |

### The `.env` file

```
GROQ_API_KEY=gsk_your_key_here
TAVILY_API_KEY=tvly-your_key_here
```

Follow these three rules. Docker keeps spaces and quote marks as part of the value, so a small mistake gives `Invalid API Key`.

1. No spaces around `=`.
2. No quote marks around the value.
3. No space or comment at the end of the line.

### Allowed models

The allowed model names are listed in `app/config/settings.py`:

```python
ALLOWED_MODEL_NAMES = [
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
]
```

Model names change over time. Check the Groq website for current names and update this list when needed.

---

## API Reference

Base address (local): `http://127.0.0.1:9999`

FastAPI also serves an interactive test page at `http://127.0.0.1:9999/docs`.

### `GET /health`

Checks that the backend is running.

Response:

```json
{ "status": "ok" }
```

### `POST /chat`

Sends a question to the agent.

Request body:

| Field | Type | Description |
|---|---|---|
| `model_name` | string | One of the allowed model names |
| `system_prompt` | string | The persona or instructions for the agent |
| `messages` | list of strings | The question, or the earlier questions plus the new one |
| `allow_search` | boolean | `true` lets the agent use web search |

Example request:

```json
{
  "model_name": "openai/gpt-oss-120b",
  "system_prompt": "You are a helpful assistant",
  "messages": ["What is 2 + 2?"],
  "allow_search": false
}
```

Example response:

```json
{ "response": "2 + 2 = 4." }
```

Example with `curl`:

```bash
curl -X POST http://127.0.0.1:9999/chat \
  -H "Content-Type: application/json" \
  -d '{"model_name":"openai/gpt-oss-120b","system_prompt":"You are a helpful assistant","messages":["What is 2 + 2?"],"allow_search":false}'
```

Status codes:

| Code | Meaning |
|---|---|
| `200` | Success |
| `400` | The model name is not in the allowed list |
| `422` | The request body has a missing or wrong field |
| `500` | An error happened inside the agent. The `detail` field has the message, the file name, and the line number |

---

## Run with Docker

Run these commands where Docker is installed (on Windows, inside the Ubuntu window).

**Build the image**

```bash
docker build -t multi-ai-agent .
```

**Run the container**

```bash
docker run --rm -it -p 8501:8501 --env-file .env multi-ai-agent
```

Open `http://localhost:8501`.

How it works:

- `--env-file .env` gives the keys to the container when it starts. The keys are not stored inside the image.
- A container reads `.env` only when it starts. If you change `.env`, stop the container and run it again. You do not need to build again.
- Port `9999` stays inside the container, so you do not need to publish it.

**Check the key inside a container (when you see a 401 error)**

```bash
docker run --rm --env-file .env multi-ai-agent sh -c 'echo "Length: ${#GROQ_API_KEY}"; echo "First 4: $(echo "$GROQ_API_KEY" | cut -c1-4)"'
```

A good Groq key starts with `gsk_`. If the first character is a quote mark, remove the quote marks from `.env`.

**Useful commands**

```bash
docker images               # list images
docker ps                   # list running containers
docker logs --tail 50 NAME  # last 50 log lines
docker stop NAME            # stop a container
docker image prune -f       # remove unused images
```

---

## CI/CD Pipeline

The pipeline is described in the `Jenkinsfile` in the project root. Jenkins reads it from GitHub, so you must push every change.

### Stages

| # | Stage | What it does |
|---|---|---|
| 1 | Clone GitHub repo | Gets the latest code from the `master` branch |
| 2 | SonarQube Analysis | Scans the code for bugs, security risks, and code smells |
| 3 | Build and Push Docker Image to ECR | Builds the image, tags it, and pushes it to AWS ECR |
| 4 | Deploy to ECS Fargate | Tells ECS to start a new task with the newest image |

### Jenkins setup

The `custom_jenkins/Dockerfile` builds a Jenkins image that has the Docker CLI and the AWS CLI inside.

```bash
cd custom_jenkins
docker build -t jenkins-dind .
docker network create jenkins-net

docker run -d --name jenkins-dind \
  --restart unless-stopped \
  --group-add $(stat -c '%g' /var/run/docker.sock) \
  --network jenkins-net \
  -p 8080:8080 -p 50000:50000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v jenkins_home:/var/jenkins_home \
  jenkins-dind
```

What the options do:

- `-v /var/run/docker.sock:/var/run/docker.sock` lets Jenkins send Docker commands to the Docker on your machine. The images Jenkins builds appear in `docker images` on your machine.
- `--group-add` gives Jenkins the permission to use that socket.
- `-v jenkins_home:...` keeps your Jenkins data when the container is removed.

Get the first password and open `http://localhost:8080`:

```bash
docker exec jenkins-dind cat /var/jenkins_home/secrets/initialAdminPassword
```

### SonarQube setup

```bash
sudo sysctl -w vm.max_map_count=262144

docker run -d --name sonarqube-dind \
  --restart unless-stopped \
  --network jenkins-net \
  -p 9000:9000 \
  -v sonarqube_data:/opt/sonarqube/data \
  -v sonarqube_extensions:/opt/sonarqube/extensions \
  -v sonarqube_logs:/opt/sonarqube/logs \
  sonarqube:community
```

SonarQube needs about 2 GB of free memory. Open `http://localhost:9000`, create a user token, and test it:

```bash
curl -s -u YOUR_TOKEN: http://localhost:9000/api/authentication/validate
```

The answer must be `{"valid":true}`.

### Jenkins plugins

- Git
- Pipeline
- SonarQube Scanner
- AWS Credentials

### Jenkins credentials

| ID | Type | Used for |
|---|---|---|
| `github-token` | Username with password (GitHub token) | Reading the repository |
| `sonarqube-token` | Secret text | Logging in to SonarQube |
| `aws-token` | AWS Credentials | Pushing to ECR and updating ECS |

### Jenkins tool settings

- **System, SonarQube servers:** name `Sonarqube`, URL `http://sonarqube-dind:9000`, token `sonarqube-token`.
- **Tools, SonarQube Scanner:** name `Sonarqube`, with **Install automatically** ticked.

### Pipeline variables

Set these in the `environment` block of the `Jenkinsfile`:

| Variable | Example value |
|---|---|
| `AWS_REGION` | `ap-southeast-2` |
| `ECR_REPO` | `multi-ai-agent` |
| `IMAGE_TAG` | `latest` |
| `ECS_CLUSTER` | `multi-ai-agent-cluster` |
| `ECS_SERVICE` | The exact service name shown in ECS |

If you create the ECS service with the quick setup, AWS may add random letters to the name (for example `multi-ai-agent-def-service-mn052znx`). Copy the real name into `ECS_SERVICE`.

### Start everything after a restart

```bash
sudo service docker start
sudo sysctl -w vm.max_map_count=262144
docker start jenkins-dind sonarqube-dind
```

---

## Deploy to AWS

Use one region for everything. The examples use `ap-southeast-2`.

### Resources

| Resource | Name | Notes |
|---|---|---|
| ECR repository | `multi-ai-agent` | Private |
| Secrets Manager secret | `multi-ai-agent/keys` | Two rows: `GROQ_API_KEY` and `TAVILY_API_KEY` |
| IAM role | `ecsTaskExecutionRole` | Policy `AmazonECSTaskExecutionRolePolicy`, plus an inline policy to read the secret |
| IAM user | `jenkins-ecr` | `AmazonEC2ContainerRegistryPowerUser`, plus `ecs:UpdateService` and `ecs:DescribeServices` |
| ECS cluster | `multi-ai-agent-cluster` | AWS Fargate |
| Task definition | `multi-ai-agent-def` | 1 vCPU, 2 GB memory, container port `8501` |
| ECS service | see the note above | 1 task, public IP on |
| Security group | created with the service | Inbound TCP `8501` from your own IP |

### Task definition details

- **Image URI:** the ECR repository address plus `:latest`, for example
  `ACCOUNT_ID.dkr.ecr.ap-southeast-2.amazonaws.com/multi-ai-agent:latest`.
  Do not use the `sha256:` digest as the image address.
- **Secrets:** add two environment variables with the type **ValueFrom**:
  - `GROQ_API_KEY` = `SECRET_ARN:GROQ_API_KEY::`
  - `TAVILY_API_KEY` = `SECRET_ARN:TAVILY_API_KEY::`

  Keep the two colons at the end. The name after the ARN must match the row name in the secret.
- **Logs:** keep log collection on. Logs go to CloudWatch.

### Secret read permission

Add this inline policy to `ecsTaskExecutionRole`, with your own secret ARN and the `*` at the end:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "YOUR_SECRET_ARN*"
    }
  ]
}
```

### Jenkins deploy permission

Add this inline policy to the IAM user `jenkins-ecr`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["ecs:UpdateService", "ecs:DescribeServices"],
      "Resource": "*"
    }
  ]
}
```

### Open the app

1. Open the ECS service, then the **Tasks** tab, then the running task.
2. Copy the **Public IP**.
3. Open `http://PUBLIC_IP:8501`.

The public IP changes every time a new task starts. Find it again after each deployment.

---

## Security

- **Never commit secrets.** `.env` is listed in `.gitignore` and `.dockerignore`. Check GitHub after your first push to be sure.
- **No keys in the image.** Keys are given at start time: `--env-file` locally, and Secrets Manager on AWS.
- **Limit access.** Allow port `8501` only from your own IP (`YOUR_IP/32`). If it is open to everyone, strangers can use your Groq and Tavily keys through the app.
- **Keep the backend private.** Port `9999` is used only inside the container. Do not open it.
- **Use small permissions.** The Jenkins user has only the ECR and ECS permissions it needs.
- **Rotate keys.** Make new API keys and AWS access keys after a project, and delete the old ones.
- **Protect Jenkins.** Do not turn off CSRF protection, and do not share the Jenkins port on the internet.
- **Local Docker permission shortcut.** The command `chmod 666 /var/run/docker.sock` opens the socket to everyone. Use it only on your own learning machine, never on a shared server.

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `docker` is not recognized in PowerShell | Docker is installed in Ubuntu | Run Docker commands in the Ubuntu window |
| `invalid env file ... contains whitespaces` | A space around `=` in `.env` | Write `KEY=value` with no spaces |
| `401 Invalid API Key` | Quote marks or a space in the key | Fix `.env`, check with the key test command, restart the container |
| `ModuleNotFoundError: No module named 'langchain_tavily'` | The library is not in `requirements.txt` | Add `langchain-tavily` and rebuild |
| `ModuleNotFoundError: No module named 'app'` on the Streamlit page | Streamlit does not have the project root on its path | Run `uv pip install -e .` and start with `python -m streamlit run app/frontend/ui.py` |
| `Could not reach the backend` | The backend is not running | Start with `python -m app.main`, or start the backend first |
| The page still shows an old version in Docker | Docker used a cached copy of old files | Build from the correct folder, or use `docker build --no-cache` |
| `failed to read dockerfile` | The file name is wrong | Name it exactly `Dockerfile` |
| `permission denied ... docker.sock` in Jenkins | Wrong group number | Run Jenkins with `--group-add $(stat -c '%g' /var/run/docker.sock)` |
| `HTTP ERROR 403 No valid crumb` | An old Jenkins page in the browser | Open a new tab and log in again |
| Jenkins container shows `Exited (5)` | Jenkins restarted after a plugin install | Run `docker start jenkins-dind` and use `--restart unless-stopped` |
| `No tool named Sonarqube found` | The tool name does not match | Add the scanner in Jenkins Tools with the same name |
| SonarQube `HTTP 401 Unauthorized` | A wrong token in Jenkins | Make a new token, test it, update `sonarqube-token` |
| `Expected a step` in the Jenkinsfile | A stage is outside `stages { }` or inside another stage | Put every stage next to the others, inside `stages { }` |
| `aws: command not found` in Jenkins | The Jenkins image has no AWS CLI | Rebuild the Jenkins image from `custom_jenkins/Dockerfile` |
| `repository does not exist` | A wrong region or repository name | Use the same region and name everywhere |
| `ServiceNotFoundException` | The service name or region does not match | Copy the exact service name into `ECS_SERVICE` |
| `ECS Deployment Circuit Breaker was triggered` | The container keeps failing to start | Open the stopped task and read the **Stopped reason** |
| `failed to normalize image reference "sha256:..."` | The image address is a digest | Use the ECR repository address plus `:latest` |
| `A secret with this name already exists` | A deleted secret waits for its removal date | Restore it, use a new name, or force delete with the AWS CLI |
| The app does not open on AWS | The security group has an old IP | Update the port `8501` rule with your new IP and `/32` |

How to debug any problem:

1. Read the last lines of the error. The reason is usually there.
2. Change one thing at a time, then test again.
3. For containers, use `docker logs --tail 50 NAME`. On AWS, read the **Stopped reason** and the CloudWatch logs.

---

## Cost and Cleanup

AWS charges while resources exist or run. ECS Fargate, ECR storage, Secrets Manager, and CloudWatch logs all cost money.

**To pause:** open the ECS service, choose **Update**, and set **Desired tasks** to `0`.

**To remove everything, in this order:**

1. Delete the ECS service (set tasks to `0` first).
2. Delete the ECS cluster.
3. Deregister and delete the task definitions.
4. Delete the ECR repository. This also deletes the images.
5. Delete the secret. AWS keeps it for a waiting time of 7 to 30 days.
6. Delete the CloudWatch log group that starts with `/ecs/`.
7. Delete the security group that starts with `ecs-`. Do not delete the group named `default`.
8. Delete leftover CloudFormation stacks for the project.
9. Delete the access key and the IAM user `jenkins-ecr`.
10. Delete the credential `aws-token` in Jenkins.
11. Make new Groq and Tavily keys and delete the old ones.
12. Check the AWS bill after 2 or 3 days, and set a small budget alert.

**Clean the local machine:**

```bash
docker stop jenkins-dind sonarqube-dind
docker image prune -f
```

---

## Known Limitations and Roadmap

Current limitations:

- The public IP of the task changes after every deployment.
- The app has no user login. Access is limited only by the security group.
- Traffic uses HTTP, not HTTPS.
- The image uses the `latest` tag, so you cannot roll back to an exact build easily.
- The pipeline does not stop when SonarQube finds serious problems.
- There are no automated tests yet.

Planned improvements:

- [ ] Add a SonarQube Quality Gate that fails the pipeline on serious issues.
- [ ] Add `pytest` tests for the API and a test stage in the pipeline.
- [ ] Tag images with the Jenkins build number.
- [ ] Add an Application Load Balancer for a fixed address and HTTPS.
- [ ] Add a health check for the ECS task using `/health`.
- [ ] Add an ECR lifecycle rule to delete old images.
- [ ] Start builds automatically with Poll SCM or a GitHub webhook.
- [ ] Add user login to the application.
- [ ] Pin exact library versions in `requirements.txt`.

---

## Contributing

1. Fork the repository and create a branch: `git checkout -b feature/your-change`.
2. Make your change and test it locally.
3. Commit with a short, clear message.
4. Push the branch and open a pull request.

Never include real keys or tokens in a commit.

---

## License

Add a `LICENSE` file and name the license here (for example MIT) before you share the project publicly.

---

## Author

[Anas Sohail](https://github.com/manasohail10-crypto)

Built as an end-to-end project covering AI agents, APIs, containers, CI/CD, and cloud deployment.