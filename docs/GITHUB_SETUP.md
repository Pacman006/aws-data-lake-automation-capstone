# Publishing the data lake capstone to GitHub (Pacman006)

This is a **separate project** from your earlier AWS DevOps / ECS repository. A dedicated repository makes it easier for reviewers to understand the data lake architecture and find your Python, AWS and infrastructure code.

## Step 0: review before making anything public

The project includes two original PDFs and **91 extracted screenshots/illustrations**. Some show the AWS Console and older Git authentication screens. **Open and inspect the images and PDFs** for account numbers, resource names, email addresses, tokens or other identifiers before publishing. Remove sensitive material or publish sanitized screenshots instead. Never upload AWS credentials, `~/.aws/credentials`, access tokens, secret keys or `.env` files.

## Step 1: create a repository

1. Sign in to [GitHub](https://github.com/) using **Pacman006**.
2. Open **https://github.com/new**.
3. Set **Owner** to `Pacman006`.
4. Set **Repository name** to `aws-data-lake-automation-capstone`.
5. Description: `AWS serverless data lake capstone with Kinesis, Firehose, S3, Lambda, DynamoDB, Glue, Athena and CloudFormation.`
6. Select **Public** if you have finished reviewing the images, or **Private** until you finish the security review.
7. Leave **Add README**, **Add .gitignore** and **Add license** unselected; they are addressed in this project already.
8. Click **Create repository**.

Your repository will be at `https://github.com/Pacman006/aws-data-lake-automation-capstone` **after** you create and push it.

## Step 2: download and extract the project

1. Download `datasoft-aws-data-lake-github-ready.zip` from the ChatGPT reply.
2. On Windows, right-click the downloaded ZIP and choose **Extract All**.
3. Open the extracted `datasoft-aws-data-lake` folder.
4. You should see `README.md`, `cloudformation/`, `src/`, `scripts/`, `docs/`, `.github/`, `tests/` and `reports/` inside.

**Don't upload the ZIP file to GitHub.** Upload/commit the extracted files so GitHub can display the source code and README correctly.

## Step 3: upload with Git (recommended for the image gallery)

There are more than 100 project files because all original screenshots are retained, so using Git is much easier than selecting batches of files in the website.

1. Install Git for Windows if necessary: **https://git-scm.com/downloads/win**.
2. Open the extracted project folder in **VS Code**.
3. Select **Terminal → New Terminal**. Use PowerShell or Git Bash; the Git commands below work in either.
4. Run these commands **inside the extracted `datasoft-aws-data-lake` folder**:

```bash
git init -b main
git add .
git status
git commit -m "Add Datasoft AWS data lake automation capstone"
git remote add origin https://github.com/Pacman006/aws-data-lake-automation-capstone.git
git push -u origin main
```

GitHub may open a browser window to authenticate you. Sign in to the correct account.

**If Git asks for your identity**, configure an email address and author name that you choose, then retry the commit:

```bash
git config --global user.name "YOUR_PREFERRED_GIT_NAME"
git config --global user.email "YOUR_GITHUB_EMAIL_OR_NOREPLY"
```

Do not paste passwords into the terminal. Never put a GitHub personal access token inside a remote URL in the repository.

### If you already initialized or uploaded to the repository

Don't rerun `git init` or `git remote add origin` blindly. If `origin` already exists, inspect `git remote -v`. If the GitHub repository already contains a README/commit, **clone that repository first**, copy the project files into the clone, and then use `git add .`, `git commit`, and `git push` to avoid unrelated histories.

## Step 4: verify the upload

Visit `https://github.com/Pacman006/aws-data-lake-automation-capstone` and check:

- `README.md` renders automatically under the file list.
- `cloudformation/template.yaml` is visible.
- `src/telemetry_processor/app.py`, `src/query_api/app.py` and `glue/transform_telemetry.py` are visible.
- `docs/images/original/` contains original screenshots.
- `docs/source/` contains both original PDFs.
- `.github/workflows/ci.yml` is present.

If you see only a `.zip` file, the extraction/upload step was incorrect.

## Step 5: verify GitHub Actions

1. Open the repository's **Actions** tab.
2. Find **Validate data lake project**.
3. Open the run triggered by your push, or select **Run workflow** if that button is visible.
4. Inspect the `unit-tests`, `sam-template` and `docker-test` jobs.
5. A **green check** means a job completed. A red X means a job failed: open the log and fix it before claiming the project is validated.

The workflow checks code and the SAM template only. **It does not deploy to AWS**, because that would require credentials, approvals and a budget.

## Step 6: write the About section and topics

On the repository home page, open the **About** panel gear icon:

**Description:** `AWS serverless data lake with Kinesis, Firehose, S3, Lambda, DynamoDB, Glue, Athena, Cognito and CloudFormation.`

**Topics:** `aws`, `cloud-architecture`, `data-lake`, `aws-lambda`, `kinesis`, `aws-glue`, `athena`, `amazon-s3`, `dynamodb`, `cloudformation`, `serverless`, `python`, `devops`, `cicd`

Optionally set a project homepage URL only if you actually have one. Do not add a demo URL if the API has not been deployed.

## Step 7: pin it to your profile

1. Open **https://github.com/Pacman006**.
2. Go to **Overview**.
3. Choose **Customize your pins**.
4. Select `aws-data-lake-automation-capstone`.
5. Save the change.

## Step 8: future changes

After editing files in the local project folder:

```bash
git status
git add .
git commit -m "Improve data lake deployment documentation"
git push
```

Prefer pull requests and review before adding production credentials, new IAM permissions or chargeable cloud resources. Your deployment evidence can be added later **only after you capture actual results**, and any screenshots should be sanitized.

## If you must use the GitHub website uploader

Open the repository's **Code** tab. For an empty repo, click **uploading an existing file** in **Quick setup**. For an initialized repo, use **Add file → Upload files**. Drag the extracted contents in manageable batches, preserving the folder structure, and click **Commit changes**. Web upload limits and hidden files make the Git method preferable for this project.
