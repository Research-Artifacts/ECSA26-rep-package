# Prepare Your Environment

### 1) Prerequisites

* **Git**
* **Python 3.13** (recommended)
* **pip**

---

### 2) Clone the repository

```bash
git clone git@github.com:Research-Artifacts/ECSA26-rep-package.git
cd ECSA26-rep-package
```

---

### 3) Set up environment variables

Create your `.env` file (used by the mining scripts):

```bash
cp .env.example .env
```

Then edit `.env` and set at least the following variable:

```dotenv
GITHUB_API_TOKEN=ghp_xxx...
```

⚠️ We recommend using a Personal Access Token (classic) with `repo` and `read:org` scopes to reduce GitHub API rate-limit issues during data collection.

---

### 4) Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

---

### 5) Install dependencies

```bash
pip install --upgrade pip
pip install -r docs/requirements.txt
```

---

## **[Back](README.md)**
